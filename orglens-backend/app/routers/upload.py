from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from pathlib import Path
from loguru import logger
from uuid import uuid4
from app.services.ingestion.deduplicator import deduplicate_employees
from app.config import settings
from app.database import get_db
from app.models import Organization, Message, Employee
from app.schemas.upload import UploadResponse
from app.services.ingestion.zip_parser import ZipParser, SingleFileParser
from app.services.ingestion.slack_client import SlackClient
from app.services.ingestion.gmail_client import GmailClient
from app.services.auth import get_current_user, require_org_access
from app.models.auth import User

router = APIRouter()

# Initialize parsers and clients
zip_parser = ZipParser()
single_parser = SingleFileParser()


def ensure_upload_dir():
    """Ensure upload directory exists"""
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


@router.post("/zip")
async def upload_zip(
    file: UploadFile = File(...),
    org_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UploadResponse:
    """
    Upload a ZIP file containing CSV + Slack + Gmail exports.
    Parses and ingests all data.
    """
    ensure_upload_dir()

    # Verify org exists
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    try:
        # Save uploaded file temporarily
        file_path = Path(settings.upload_dir) / f"{uuid4()}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Parse ZIP
        with open(file_path, "rb") as f:
            ingestion_result = zip_parser.parse(f, file.filename)

        # Store data in database
        await _ingest_parsed_data(org_id, ingestion_result, db)

        # Clean up temp file
        file_path.unlink(missing_ok=True)

        logger.info(f"✅ ZIP uploaded for org {org.name}: {len(ingestion_result.messages)} messages, {len(ingestion_result.employees)} employees")

        return UploadResponse(
            upload_id=str(uuid4()),
            org_id=org_id,
            files_received=ingestion_result.file_summary,
            records_parsed=len(ingestion_result.messages) + len(ingestion_result.employees),
            status="success",
            message="Data imported successfully"
        )

    except Exception as e:
        logger.error(f"ZIP upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/csv-employees")
async def upload_employee_csv(
    file: UploadFile = File(...),
    org_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UploadResponse:
    """Upload employee CSV only"""
    ensure_upload_dir()

    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    try:
        file_path = Path(settings.upload_dir) / f"{uuid4()}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        with open(file_path, "rb") as f:
            ingestion_result = single_parser.parse_employee_csv(f)

        await _ingest_employees(org_id, ingestion_result.employees, db)
        file_path.unlink(missing_ok=True)

        logger.info(f"✅ Employee CSV uploaded for org {org.name}: {len(ingestion_result.employees)} employees")

        return UploadResponse(
            upload_id=str(uuid4()),
            org_id=org_id,
            files_received=["employees.csv"],
            records_parsed=len(ingestion_result.employees),
            status="success",
            message=f"{len(ingestion_result.employees)} employees imported"
        )

    except Exception as e:
        logger.error(f"CSV upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/slack-export")
async def upload_slack_export(
    file: UploadFile = File(...),
    org_id: str = Form(...),
    channel_name: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UploadResponse:
    """Upload Slack export JSON for a specific channel"""
    ensure_upload_dir()

    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    try:
        file_path = Path(settings.upload_dir) / f"{uuid4()}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        with open(file_path, "rb") as f:
            ingestion_result = single_parser.parse_slack_export(f, channel_name)

        await _ingest_parsed_data(org_id, ingestion_result, db)
        file_path.unlink(missing_ok=True)

        logger.info(f"✅ Slack export uploaded for org {org.name}: {len(ingestion_result.messages)} messages")

        return UploadResponse(
            upload_id=str(uuid4()),
            org_id=org_id,
            files_received=[f"#{channel_name}"],
            records_parsed=len(ingestion_result.messages),
            status="success",
            message=f"{len(ingestion_result.messages)} messages imported from #{channel_name}"
        )

    except Exception as e:
        logger.error(f"Slack export upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/gmail-export")
async def upload_gmail_export(
    file: UploadFile = File(...),
    org_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UploadResponse:
    """Upload Gmail export (.mbox)"""
    ensure_upload_dir()

    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    try:
        # Save uploaded file temporarily
        file_path = Path(settings.upload_dir) / f"{uuid4()}_{file.filename}"

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Parse Gmail export
        with open(file_path, "rb") as f:
            ingestion_result = single_parser.parse_gmail_export(f)

        # Store in DB
        await _ingest_parsed_data(org_id, ingestion_result, db)

        # Cleanup
        file_path.unlink(missing_ok=True)

        logger.info(
            f"✅ Gmail export uploaded for org {org.name}: "
            f"{len(ingestion_result.messages)} emails"
        )

        return UploadResponse(
            upload_id=str(uuid4()),
            org_id=org_id,
            files_received=[file.filename],
            records_parsed=len(ingestion_result.messages),
            status="success",
            message=f"{len(ingestion_result.messages)} emails imported"
        )

    except Exception as e:
        logger.error(f"Gmail export upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/sync-slack/{org_id}")
async def sync_slack_data(org_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> UploadResponse:
    """
    Connect to Slack API and pull live data.
    Requires slack_access_token to be saved in organization.
    """
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if not org.slack_access_token:
        raise HTTPException(status_code=400, detail="Slack not connected. Please authorize first.")

    try:
        slack_client = SlackClient(org.slack_access_token)
        ingestion_result = await slack_client.fetch_all_data()

        await _ingest_parsed_data(str(org.id), ingestion_result, db)

        logger.info(f"✅ Slack data synced for org {org.name}: {len(ingestion_result.messages)} messages")

        return UploadResponse(
            upload_id=str(uuid4()),
            org_id=str(org.id),
            files_received=ingestion_result.file_summary,
            records_parsed=len(ingestion_result.messages),
            status="success",
            message="Slack data synced successfully"
        )

    except Exception as e:
        logger.error(f"Slack sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-gmail/{org_id}")
async def sync_gmail_data(org_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> UploadResponse:
    """
    Connect to Gmail API and pull live email data.
    Requires gmail_access_token to be saved in organization.
    """
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if not org.gmail_access_token:
        raise HTTPException(status_code=400, detail="Gmail not connected. Please authorize first.")

    try:
        gmail_client = GmailClient(org.gmail_access_token)
        ingestion_result = await gmail_client.fetch_all_emails()

        await _ingest_parsed_data(str(org.id), ingestion_result, db)

        logger.info(f"✅ Gmail data synced for org {org.name}: {len(ingestion_result.messages)} emails")

        return UploadResponse(
            upload_id=str(uuid4()),
            org_id=str(org.id),
            files_received=ingestion_result.file_summary,
            records_parsed=len(ingestion_result.messages),
            status="success",
            message="Gmail data synced successfully"
        )

    except Exception as e:
        logger.error(f"Gmail sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _ingest_parsed_data(org_id: str, ingestion_result, db: AsyncSession ):
    """Store parsed employees and messages in database"""
    await _ingest_employees(org_id, ingestion_result.employees, db)
    await _ingest_messages(org_id, ingestion_result.messages, db)


async def _ingest_employees(org_id: str, employees, db: AsyncSession):
    from uuid import UUID
    
    logger.info(f"_ingest_employees called with {len(employees)} employees for org {org_id}")
    
    raw = [vars(e) if not isinstance(e, dict) else e for e in employees]
    deduped = deduplicate_employees(raw)
    
    logger.info(f"After dedup: {len(deduped)} employees")
    
    org_id_uuid = UUID(org_id)
    
    count = 0
    for parsed_emp in deduped:
        if parsed_emp.get("email"):
            existing = await db.execute(
                select(Employee).where(
                    (Employee.org_id == org_id_uuid) & 
                    (Employee.email == parsed_emp.get("email"))
                )
            )
            if existing.scalar_one_or_none():
                logger.info(f"  Skipping {parsed_emp.get('name')} (already exists)")
                continue

        emp = Employee(
            org_id=org_id_uuid,
            name=parsed_emp.get("name"),
            email=parsed_emp.get("email"),
            title=parsed_emp.get("title"),
            department=parsed_emp.get("department"),
            level=parsed_emp.get("level"),
            tenure_months=parsed_emp.get("tenure_months"),
        )
        db.add(emp)
        count += 1

    logger.info(f"About to commit {count} new employees")
    await db.commit()
    logger.info(f"✅ Committed {count} employees to database")

async def _ingest_messages(org_id: str, messages, db: AsyncSession):
    """Store messages in database"""
    from uuid import UUID
    from app.models import MessageSource
    org_id_uuid = UUID(org_id)

    for parsed_msg in messages:
        # Skip if message already exists
        existing = await db.execute(
            select(Message).where(
                (Message.org_id == UUID(org_id)) & 
                (Message.external_id == parsed_msg.external_id) &
                (Message.source == parsed_msg.source)
            )
        )
        if existing.scalar_one_or_none():
            continue

        # Resolve sender
        sender_id = None
        if parsed_msg.sender_raw:
            sender_result = await db.execute(
                select(Employee).where(
                    (Employee.org_id == UUID(org_id)) &
                    ((Employee.name == parsed_msg.sender_raw) | (Employee.email == parsed_msg.sender_raw))
                )
            )
            sender = sender_result.scalar_one_or_none()
            if sender:
                sender_id = sender.id

        msg = Message(
            org_id=UUID(org_id),
            source=MessageSource[parsed_msg.source.upper()],
            external_id=parsed_msg.external_id,
            sender_id=sender_id,
            sender_raw=parsed_msg.sender_raw,
            channel_or_thread=parsed_msg.channel_or_thread,
            content=parsed_msg.content,
            timestamp=parsed_msg.timestamp,
        )
        db.add(msg)

    await db.commit()