import csv
from datetime import datetime, date
import hashlib
import io
from pathlib import Path
from uuid import UUID, uuid4
from typing import Optional

from rolling.app.repositories.athletes import create_athlete
from rolling.app.repositories.datasets import create_dataset
from rolling.app.repositories.projects import analyst_can_access_project, link_dataset_to_project
from rolling.app.services.upload_validation import ValidatorDispatcher
from rolling.app.services.dataset_mapping import MapperDispatcher
from rolling.app.models.datasets import DatasetResponse, FileValidationResult, UploadValidationSummary, DatasetUploadResponse
from rolling.app.models.athletes import AthleteCreate, AthleteResponse

from fastapi import UploadFile, HTTPException, status


# CONFIGURATION
UPLOAD_BASE_DIR = Path("data/uploads") # TODO note this for package use

# MAIN SERVICE FUNCTION
async def process_dataset_upload(project_id: UUID,
                                 current_analyst_id: UUID,
                                 files: list[UploadFile]) -> DatasetUploadResponse:
    """
    Uploads files as datasets to the database.

    The main steps of the process include:
    1. Validating that the analyst can access the project.
    2. Reading the files to upload to the database.
    3. Validating the files to upload.
    4. Building a validation summary.
    5. If the file upload was not valid, a response is immediately returned.
    6. If the file upload was valid, it proceeds.
    7. Creating an upload directory
    8. Locally storing the uploaded files.
    9. Persist the file contents as datasets in the database.
    10. If an error occurs during persistence, an HTTP exception is raised.
    11. If there are no errors, a structured output is returned.

    Args:
        project_id (UUID): The project to which to upload the dataset.
        current_analyst_id (UUID): The analyst uploading the dataset.
        files (list[UploadFile]): The files to upload.

    Returns:
        DatasetUploadResponse: The result of the dataset upload.

    Raises:
        HTTPException:
            - HTTP_403_FORBIDDEN: If the analyst is not allowed to access the project.
            - HTTP_400_BAD_REQUEST: If a file import was unsuccessful.

    """
    # verify current analyst can access the project
    if not analyst_can_access_project(current_analyst_id, project_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not allowed to upload to this project")

    # read uploaded files into [(filename, bytes), ...]
    uploaded_files = []
    for file in files:
        file_bytes = await file.read()
        uploaded_files.append({"file_name": file.filename,
                               "file_bytes": file_bytes})

    # validate the files
    validation_input = [(item["file_name"], item["file_bytes"]) for item in uploaded_files]
    validation_result = validate_uploaded_files(validation_input)

    # build validation summary
    file_results = build_file_validation_models(validation_result=validation_result)
    validation_summary = build_validation_summary(validation_result=validation_result,
                                                  file_results=file_results)
    
    # if invalid -> return DatasetUploadResponse with no dataset
    if not validation_result["is_valid"]:
        return DatasetUploadResponse(project_id=project_id,
                                     is_valid=False,
                                     validation=validation_summary,
                                     datasets=[])

    # if valid
    # create upload directory
    upload_dir = build_upload_directory(current_analyst_id, project_id)
    mapper_dispatcher = MapperDispatcher()
    dataset_records = list()

    upload_order = {
        "athletes.csv": 0,
        "performances.csv": 1,
        "hormones.csv": 2,
        "symptoms.csv": 3,
        "cycle_phases.csv": 4
    }

    uploaded_files.sort(key=lambda item: upload_order.get(item["file_name"], 999))

    for result in uploaded_files:
        file_name = result.get("file_name")
        file_bytes = result.get("file_bytes")

        # save each file
        stored_relative_path = save_uploaded_file(upload_dir=upload_dir,
                                                  filename=file_name,
                                                  file_bytes=file_bytes)
        
        # TODO create dataset metadata row

        # compute content hash
        content_hash = compute_content_hash(file_bytes)

        # create dataset rows
        dataset_row = create_dataset(uploaded_by_id=current_analyst_id,
                                     original_file_name=file_name,
                                     stored_relative_path=stored_relative_path,
                                     content_hash=content_hash, # I don't see the point of uploading a content_hash if I can't decrypt it
                                     notes=result.get("notes")) # TODO fix notes
        dataset_records.append(dataset_row)

        link_dataset_to_project(project_id, dataset_row["dataset_id"])

        rows = parse_csv_bytes(file_bytes)
        mapper_result = mapper_dispatcher.map_file(file_name, rows, dataset_row["dataset_id"])

        if not mapper_result["import_successful"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"file_name": file_name,
                                        "errors": mapper_result["errors"]})
    
    dataset_responses = build_dataset_response_models(dataset_rows=dataset_records)

    return DatasetUploadResponse(project_id=project_id,
                                 is_valid=True,
                                 validation=validation_summary,
                                 datasets=dataset_responses)

# FILE HELPERS
def compute_content_hash(file_bytes: bytes) -> str:
    """Hashes content from file bytes."""
    return hashlib.sha256(file_bytes).hexdigest()

def build_upload_directory(analyst_id: UUID, project_id: UUID) -> Path:
    """
    Create a stable and unique directory for an upload batch.

    Args:
        analyst_id (UUID): The ID of the analyst uploading the dataset batch.
        project_id (UUID): The ID of the project to which the datasets were uplooaded.

    Return:
        Path: The path to the directory for this upload batch.
    """
    upload_dir = UPLOAD_BASE_DIR / str(analyst_id) / str(project_id) / uuid4().hex # uuid4().hex works as a batch ID
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir

def build_stored_relative_path(upload_dir: Path, filename: str) -> str:
    """
    Builds the stored relative path for a given filename after an upload.

    Args:
        upload_dir (Path): The path to the file.
        filename (str): The specific file name.

    Returns:
        str: The relative path of the stored file.
    """
    file_path = upload_dir / filename
    return str(file_path.relative_to(UPLOAD_BASE_DIR.parent.parent))

def save_uploaded_file(upload_dir: Path, filename: str, file_bytes: bytes) -> str:
    """
    Saves a file a given directory.

    Args:
        upload_dir (Path): The directory to upload the file.
        filename (str): The name of the file.
        file_bytes (bytes): The content of the file as bytes.

    Returns:
        str: The path to the uploaded file.
    """
    file_path = upload_dir / filename
    file_path.write_bytes(file_bytes)
    return build_stored_relative_path(upload_dir, filename)

def parse_csv_bytes(file_bytes: bytes) -> list[dict[str, str]]:
    """
    Converts file bytes to a readable content.

    Args:
        file_bytes (bytes): The content of the file as bytes.

    Returns:
        list[dict[str, str]]: The readable content of the file.
    """
    csv_text = file_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(csv_text))
    return [dict(row) for row in reader]

# VALIDATION ADAPTER
def validate_uploaded_files(uploaded_files: list[tuple[str, bytes]]) -> dict: # TODO rename to files_to_upload
    """
    Creates an instance the ValidatorDispatcher that validates uploaded files.
    Args:
        uploaded_files (list[tuple[str, bytes]]): The files to upload.

    Returns:
        dict: A dictionary of the validation results.
            - "is_valid" (bool): True if the file to upload is valid.
            - "files" (list[dict]): The result of the file validation.
                - "file_name" (str): The name of the file.
                - "is_valid" (bool): True if the file to upload is valid.
                - "row_count" (int): The number of rows in the file.
                - "errors" (list[str]): If the file to upload is invalid, it contains the error messages. Otherwise, an empty list.
                - "warnings" (list[str]): If there are any warnings about the file, it contains the warning messages. Otherwise, an empty list.
    """
    validation_dispatcher = ValidatorDispatcher()
    return validation_dispatcher.validate_files(uploaded_files)

# ATHLETE ROW CREATION HELPER
def create_athlete_record(external_code: str,
                          birth_date: Optional[date]=None,
                          birth_year: Optional[int]=None,
                          age_at_observation: Optional[int]=None,
                          age_logged_at: Optional[date] = None,
                          notes: Optional[str] = None) -> dict:
    row = create_athlete(external_code=external_code,
                         birth_date=birth_date,
                         birth_year=birth_year,
                         age_at_observation=age_at_observation,
                         age_logged_at=age_logged_at,
                         notes=notes)
    """TODO: deprecated."""
    return row

# RESPONSE MODEL BUILDERS
def build_file_validation_models(validation_result: dict) -> list[FileValidationResult]:
    """
    Converts raw per-file dictionaries into a list of validation results.

    Args:
        validation_result (dict): A dictionary of the validation results.

    Returns:
        list[FileValidationResult]: A list of validation results.
    """
    file_results = [
        FileValidationResult(**result) for result in validation_result["files"]
    ]
    return file_results

def build_validation_summary(validation_result: dict, file_results: list[FileValidationResult]) -> UploadValidationSummary:
    """
    Constructs a summary of the validation results.

    Args:
        validation_result (dict): A dictionary of the validation results.
        file_results (list[FileValidationResult]): A list of validation results.

    Returns:
        UploadValidationSummary: A summary of the validation results.
    """
    validation_summary = UploadValidationSummary(is_valid=validation_result["is_valid"],
                                                 files=file_results)
    return validation_summary

def build_dataset_response_models(dataset_rows: list[dict]) -> list[DatasetResponse]:
    """
    Converts the created database rows of dataset uploads into a list of dataset responses.

    Args:
        dataset_rows (list[dict]): A list of dataset rows.

    Returns:
        list[DatasetResponse]: A list of dataset responses.
    """
    dataset_responses = []
    for row in dataset_rows:
        dataset_response = DatasetResponse(**row)
        dataset_responses.append(dataset_response)
    return dataset_responses
