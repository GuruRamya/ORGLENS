from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
import enum


class UploadType(str, enum.Enum):
    ZIP = "zip"
    CSV_EMPLOYEES = "csv_employees"
    GMAIL_EXPORT = "gmail_export"
    SLACK_EXPORT = "slack_export"
    NARRATIVE_TEXT = "narrative_text"

class UploadResponse(BaseModel):
    upload_id: str
    org_id: UUID
    files_received: list[str]
    records_parsed: int
    status: str
    message: str


class FileUploadStatus(BaseModel):
    org_id: UUID
    file_type: UploadType
    status: str 
    progress_percent: int
    message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
