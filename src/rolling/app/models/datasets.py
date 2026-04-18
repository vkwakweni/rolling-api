from datetime import datetime
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class DatasetCreate(BaseModel):
    """
    Represents the data required to create a new dataset record in the system.
    
    Attributes:
        original_file_name (str): The original name of the uploaded file.
        stored_relative_path (str): The relative path where the uploaded file is stored in the system.
        content_hash (Optional[str]): An optional hash of the file content for integrity verification.
        notes (Optional[str]): Optional notes about the dataset.
    """
    original_file_name: str
    stored_relative_path: str
    content_hash: Optional[str] = None
    notes: Optional[str] = None


class DatasetResponse(BaseModel):
    """
    Represents a dataset record in the system, including metadata about the dataset and its storage.
    
    Attributes:
        dataset_id (UUID): Unique identifier for the dataset.
        uploaded_by_id (UUID): Unique identifier for the user who uploaded the dataset.
        original_file_name (str): The original name of the uploaded file.
        stored_relative_path (str): The relative path where the uploaded file is stored in the system.
        content_hash (Optional[str]): An optional hash of the file content for integrity verification.
        uploaded_at (datetime): The timestamp when the dataset was uploaded.
        import_status (Literal["uploaded", "pending", "failed"]): The current status of the dataset import process.
        notes (Optional[str]): Optional notes about the dataset.
    """
    dataset_id: UUID
    uploaded_by_id: UUID
    original_file_name: str
    stored_relative_path: str
    content_hash: Optional[str] = None
    uploaded_at: datetime
    import_status: Literal["uploaded", "pending", "failed"]
    notes: Optional[str] = None

class FileValidationResult(BaseModel):
    """
    Represents the result of validating an uploaded file, including its name, validity status, row count, and any errors or warnings encountered during validation.
    
    Attributes:
        file_name (str): The name of the uploaded file.
        is_valid (bool): A boolean indicating whether the file is valid.
        row_count (int): The number of rows in the file.
        errors (list[str]): A list of errors encountered during validation.
        warnings (list[str]): A list of warnings encountered during validation.
    """
    file_name: str
    is_valid: bool
    row_count: int
    errors: list[str]
    warnings: list[str]

class UploadValidationSummary(BaseModel):
    """
    Represents a summary of the validation results for an uploaded dataset, including the overall validity status and a list of validation results for each file.
    
    Attributes:
        is_valid (bool): A boolean indicating whether the uploaded dataset is valid.
        files (list[FileValidationResult]): A list of validation results for each file in the dataset.
    """
    is_valid: bool
    files: list[FileValidationResult]

class DatasetUploadResponse(BaseModel):
    """
    Represents the response returned after a dataset upload attempt, including the project ID, overall validity status, validation summary, and a list of dataset records created from the upload.
    
    Attributes:
        project_id (UUID): The ID of the project to which the dataset belongs.
        is_valid (bool): A boolean indicating whether the uploaded dataset is valid.
        validation (UploadValidationSummary): A summary of the validation results for the uploaded dataset.
        datasets (list[DatasetResponse]): A list of dataset records created from the upload.
    """
    project_id: UUID
    is_valid: bool
    validation: UploadValidationSummary
    datasets: list[DatasetResponse] = Field(default_factory=list) # avoiding a mutable default