from datetime import datetime
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field

# TODO docstrings for classes

class DatasetCreate(BaseModel):
    original_file_name: str
    stored_relative_path: str
    content_hash: Optional[str] = None
    notes: Optional[str] = None


class DatasetResponse(BaseModel):
    dataset_id: UUID
    uploaded_by_id: UUID
    original_file_name: str
    stored_relative_path: str
    content_hash: Optional[str] = None
    uploaded_at: datetime
    import_status: Literal["uploaded", "pending", "failed"]
    notes: Optional[str] = None

class FileValidationResult(BaseModel):
    file_name: str
    is_valid: bool
    row_count: int
    errors: list[str]
    warnings: list[str]

class UploadValidationSummary(BaseModel):
    is_valid: bool
    files: list[FileValidationResult]

class DatasetUploadResponse(BaseModel):
    project_id: UUID
    is_valid: bool
    validation: UploadValidationSummary
    datasets: list[DatasetResponse] = Field(default_factory=list) # avoiding a mutable default