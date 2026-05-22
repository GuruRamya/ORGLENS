from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from email.utils import parsedate_to_datetime
import base64
from loguru import logger

from app.services.ingestion.zip_parser import ParsedMessage, IngestionResult


class GmailClient:
    """Gmail API client for fetching email data"""

    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.service = build("gmail", "v1", credentials=self._get_credentials())

    def _get_credentials(self) -> Credentials:
        """Create credentials from access token"""
        creds = Credentials(token=self.access_token)
        return creds

    async def fetch_all_emails(self, query: str = "is:important", max_results: int = 500) -> IngestionResult:
        """
        Fetch emails from Gmail.
        By default, fetches important emails (to reduce noise).
        """
        result = IngestionResult()

        try:
            # Get list of messages
            messages = self._get_message_ids(query, max_results)

            count = 0
            for msg_id in messages:
                try:
                    message = self.service.users().messages().get(
                        userId="me",
                        id=msg_id,
                        format="full"
                    ).execute()

                    parsed_msg = self._parse_email_message(message)
                    if parsed_msg:
                        result.messages.append(parsed_msg)
                        count += 1

                except HttpError as e:
                    logger.warning(f"Error fetching message {msg_id}: {str(e)}")
                    continue

            result.file_summary.append(f"Gmail → {count} emails")
            logger.info(f"✅ Gmail sync complete: {count} emails fetched")

        except HttpError as e:
            error_msg = f"Gmail API error: {str(e)}"
            result.errors.append(error_msg)
            logger.error(error_msg)

        return result

    def _get_message_ids(self, query: str, max_results: int) -> list:
        """Get list of message IDs matching query"""
        try:
            results = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=min(max_results, 100)
            ).execute()

            return [msg["id"] for msg in results.get("messages", [])]

        except HttpError as e:
            logger.error(f"Error listing messages: {str(e)}")
            return []

    def _parse_email_message(self, message: dict) -> ParsedMessage:
        """Parse an email message into ParsedMessage"""
        try:
            headers = message.get("payload", {}).get("headers", [])
            headers_dict = {h["name"]: h["value"] for h in headers}

            subject = headers_dict.get("Subject", "")
            sender = headers_dict.get("From", "")
            date_str = headers_dict.get("Date", "")
            msg_id = headers_dict.get("Message-ID", message.get("id", ""))

            # Extract body
            body = self._get_email_body(message)
            if not body or len(body) < 20:
                return None

            # Combine subject + body
            content = f"Subject: {subject}\n{body}".strip()

            # Parse date
            try:
                ts = parsedate_to_datetime(date_str).replace(tzinfo=None)
            except Exception:
                ts = datetime.utcnow()

            return ParsedMessage(
                source="gmail",
                external_id=msg_id,
                sender_raw=sender,
                channel_or_thread=f"thread:{subject[:50]}",
                content=content,
                timestamp=ts,
            )

        except Exception as e:
            logger.warning(f"Error parsing email: {str(e)}")
            return None

    def _get_email_body(self, message: dict) -> str:
        """Extract plain text body from email"""
        try:
            payload = message.get("payload", {})

            # Simple message
            if "parts" not in payload:
                data = payload.get("body", {}).get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                return ""

            # Multipart message - find text/plain part
            for part in payload.get("parts", []):
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

            # Fallback to first part
            first_part = payload.get("parts", [{}])[0]
            data = first_part.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

            return ""

        except Exception as e:
            logger.warning(f"Error extracting email body: {str(e)}")
            return ""