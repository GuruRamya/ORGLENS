"""
Handles ZIP upload, CSV employee parsing, Slack JSON exports, Gmail mbox exports.
All paths normalize into the same internal format before NLP pipeline.
"""
import zipfile
import csv
import json
import io
import os
import mailbox
import tempfile
from pathlib import Path
from datetime import datetime
from typing import BinaryIO
from loguru import logger
from app.config import settings
import pandas as pd

class ParsedEmployee:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "")
        self.email: str | None = kwargs.get("email")
        self.title: str | None = kwargs.get("title")
        self.department: str | None = kwargs.get("department")
        self.level: str | None = kwargs.get("level")
        self.manager_name: str | None = kwargs.get("manager_name")
        self.tenure_months: int | None = kwargs.get("tenure_months")


class ParsedMessage:
    def __init__(self, **kwargs):
        self.source: str = kwargs.get("source", "upload")   # slack | gmail | upload
        self.external_id: str | None = kwargs.get("external_id")
        self.sender_raw: str = kwargs.get("sender_raw", "")
        self.channel_or_thread: str | None = kwargs.get("channel_or_thread")
        self.content: str = kwargs.get("content", "")
        self.timestamp: datetime = kwargs.get("timestamp", datetime.utcnow())


class ParsedNarrative:
    """Company claims — from uploaded text, website copy, mission docs."""
    def __init__(self):
        self.mission_statement: str | None = None
        self.values: list[str] = []
        self.claims: list[str] = []       # individual claim sentences


class IngestionResult:
    def __init__(self):
        self.employees: list[ParsedEmployee] = []
        self.messages: list[ParsedMessage] = []
        self.narrative: ParsedNarrative = ParsedNarrative()
        self.errors: list[str] = []
        self.file_summary: list[str] = []


class ZipParser:
    """
    Accepts a ZIP file containing any combination of:
    - employees.csv  (employee roster)
    - slack/         (folder with Slack export JSONs per channel)
    - gmail.mbox     (Gmail Takeout export)
    - narrative.txt  (company claims / mission text)
    """

    def parse(self, file: BinaryIO, filename: str) -> IngestionResult:
        result = IngestionResult()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                with zipfile.ZipFile(file) as zf:
                    zf.extractall(tmpdir)
            except zipfile.BadZipFile:
                result.errors.append(f"{filename} is not a valid ZIP file.")
                return result

            extracted = list(Path(tmpdir).rglob("*"))
            for path in extracted:
                if path.is_file():
                    self._route_file(path, result)

        logger.info(f"ZIP parse complete: {len(result.employees)} employees, "
                    f"{len(result.messages)} messages")
        return result

    def _route_file(self, path: Path, result: IngestionResult):
        suffix = path.suffix.lower()
        
        parser = {
            ".csv": self._parse_csv,
            ".xlsx": self._parse_excel,
            ".xls": self._parse_excel,
            ".json": self._parse_slack_json,
            ".mbox": self._parse_mbox,
            ".txt": self._parse_narrative,
            ".md": self._parse_narrative,
        }.get(suffix)

        if parser:
            parser(path, result)
        else:
            logger.warning(f"Unsupported file type: {path.name}")
            result.errors.append(f"Unsupported file type: {path.name}")

    def _parse_csv(self, path: Path, result: IngestionResult):
        """
        Expected columns (flexible matching):
        name, email, title/role/position, department/team, manager, tenure
        """
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                headers = [h.lower().strip() for h in (reader.fieldnames or [])]

                def find_col(candidates):
                    for c in candidates:
                        for h in headers:
                            if c in h:
                                return reader.fieldnames[[h2.lower().strip() for h2 in reader.fieldnames].index(h)]
                    return None

                name_col = find_col(["name", "full name", "employee"])
                email_col = find_col(["email", "mail"])
                title_col = find_col(["title", "role", "position", "job"])
                dept_col = find_col(["department", "dept", "team", "division"])
                mgr_col = find_col(["manager", "supervisor", "reports to"])
                tenure_col = find_col(["tenure", "months", "seniority"])

                if not name_col:
                    result.errors.append(f"{path.name}: Could not find 'name' column in CSV")
                    return

                count = 0
                for row in reader:
                    name = row.get(name_col, "").strip()
                    if not name:
                        continue
                    emp = ParsedEmployee(
                        name=name,
                        email=row.get(email_col, "").strip() if email_col else None,
                        title=row.get(title_col, "").strip() if title_col else None,
                        department=row.get(dept_col, "").strip() if dept_col else None,
                        manager_name=row.get(mgr_col, "").strip() if mgr_col else None,
                        tenure_months=self._parse_tenure(row.get(tenure_col, "") if tenure_col else ""),
                    )
                    emp.level = self._infer_level(emp.title or "")
                    result.employees.append(emp)
                    count += 1

                result.file_summary.append(f"employees.csv → {count} employees")
        except Exception as e:
            result.errors.append(f"Error parsing {path.name}: {str(e)}")
            

    def _parse_excel(self, path: Path, result: IngestionResult):
        try:
            logger.info(f"📊 Parsing Excel: {path.name}")

            df = pd.read_excel(path)

            # Optional normalization
            df = df.rename(columns={
                'Employee Name': 'name',
                'Email': 'email',
                'Job Title': 'title',
                'Department': 'department',
                'Level': 'level',
                'Tenure (months)': 'tenure_months',
            })

            temp_csv = path.with_suffix(".csv")
            df.to_csv(temp_csv, index=False)

            self._parse_csv(temp_csv, result)

            temp_csv.unlink(missing_ok=True)

        except Exception as e:
            result.errors.append(f"Error parsing Excel {path.name}: {str(e)}")
            logger.error(f"❌ Excel parse error: {str(e)}")


    def _parse_slack_json(self, path: Path, result: IngestionResult):
        """
        Slack export: each file is a channel's messages.
        File name = channel name. Content = list of message objects.
        """
        try:
            channel_name = path.stem   # file name without extension = channel name
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                return

            count = 0
            for msg in data:
                if msg.get("type") != "message" or msg.get("subtype"):
                    continue
                text = msg.get("text", "").strip()
                if not text or len(text) < 5:
                    continue
                ts_raw = msg.get("ts", "0")
                try:
                    ts = datetime.fromtimestamp(float(ts_raw))
                except (ValueError, OSError):
                    ts = datetime.utcnow()

                parsed = ParsedMessage(
                    source="slack",
                    external_id=ts_raw,
                    sender_raw=msg.get("user", msg.get("username", "")),
                    channel_or_thread=channel_name,
                    content=text,
                    timestamp=ts,
                )
                result.messages.append(parsed)
                count += 1

            result.file_summary.append(f"#{channel_name} → {count} messages")
        except Exception as e:
            result.errors.append(f"Error parsing Slack JSON {path.name}: {str(e)}")

    def _parse_mbox(self, path: Path, result: IngestionResult):
        """Parse Gmail Takeout .mbox file."""
        try:
            mbox = mailbox.mbox(str(path))
            count = 0
            for msg in mbox:
                subject = msg.get("subject", "")
                sender = msg.get("from", "")
                date_str = msg.get("date", "")

                # Extract plain text body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                            except Exception:
                                pass
                            break
                else:
                    try:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="replace")
                    except Exception:
                        body = str(msg.get_payload())

                content = f"Subject: {subject}\n{body}".strip()
                if len(content) < 20:
                    continue

                ts = self._parse_email_date(date_str)
                parsed = ParsedMessage(
                    source="gmail",
                    external_id=msg.get("message-id", ""),
                    sender_raw=sender,
                    channel_or_thread=f"thread:{subject[:50]}",
                    content=content,
                    timestamp=ts,
                )
                result.messages.append(parsed)
                count += 1

            result.file_summary.append(f"gmail.mbox → {count} emails")
        except Exception as e:
            result.errors.append(f"Error parsing mbox: {str(e)}")

    def _parse_narrative(self, path: Path, result: IngestionResult):
        """Parse free-form narrative/claims text."""
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
            # Treat each non-empty line as a claim
            lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 20]
            result.narrative.claims.extend(lines)
            if not result.narrative.mission_statement and lines:
                result.narrative.mission_statement = lines[0]
            result.file_summary.append(f"{path.name} → {len(lines)} narrative claims")
        except Exception as e:
            result.errors.append(f"Error parsing narrative {path.name}: {str(e)}")

    # ─── Helpers ─────────────────────────────────────────────────────────────

    def _infer_level(self, title: str) -> str:
        title_lower = title.lower()
        if any(x in title_lower for x in ["ceo", "cto", "coo", "cfo", "chief", "president"]):
            return "C-Suite"
        if any(x in title_lower for x in ["vp", "vice president"]):
            return "VP"
        if any(x in title_lower for x in ["director"]):
            return "Director"
        if any(x in title_lower for x in ["manager", "lead", "head of"]):
            return "Manager"
        if any(x in title_lower for x in ["senior", "sr.", "principal", "staff"]):
            return "Senior IC"
        return "IC"

    def _parse_tenure(self, value: str) -> int | None:
        try:
            return int(float(value.strip()))
        except (ValueError, AttributeError):
            return None

    def _parse_email_date(self, date_str: str) -> datetime:
        from email.utils import parsedate_to_datetime
        try:
            return parsedate_to_datetime(date_str).replace(tzinfo=None)
        except Exception:
            return datetime.utcnow()


# Single file upload (not ZIP)
class SingleFileParser:
    def __init__(self):
        self._zip_parser = ZipParser()

    def parse_employee_csv(self, file: BinaryIO) -> IngestionResult:
        result = IngestionResult()
        tmp = Path(settings.upload_dir) / "tmp_employee.csv"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(file.read())
        self._zip_parser._parse_csv(tmp, result)
        tmp.unlink(missing_ok=True)
        return result

    def parse_slack_export(self, file: BinaryIO, channel_name: str) -> IngestionResult:
        result = IngestionResult()
        tmp = Path(settings.upload_dir) / f"{channel_name}.json"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(file.read())
        self._zip_parser._parse_slack_json(tmp, result)
        tmp.unlink(missing_ok=True)
        return result
    def parse_gmail_export(self, file: BinaryIO) -> IngestionResult:
        result = IngestionResult()

        with tempfile.NamedTemporaryFile(suffix=".mbox", delete=False) as f:
            f.write(file.read())
            tmp_path = f.name
        try:
            self._zip_parser._parse_mbox(Path(tmp_path), result)
        finally:
            os.unlink(tmp_path)

        return result
    def parse_narrative(self, text: str) -> IngestionResult:
        result = IngestionResult()
        lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 20]
        result.narrative.claims.extend(lines)
        return result