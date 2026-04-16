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
UPLOAD_BASE_DIR = Path("data/uploads")

# MAIN SERVICE FUNCTION
async def process_dataset_upload(project_id: UUID,
                                 current_analyst_id: UUID,
                                 files: list[UploadFile]) -> DatasetUploadResponse:
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
    return hashlib.sha256(file_bytes).hexdigest()

def build_upload_directory(analyst_id: UUID, project_id: UUID) -> Path:
    # create a stable/unique directory for this upload batch
    upload_dir = UPLOAD_BASE_DIR / str(analyst_id) / str(project_id) / uuid4().hex # uuid4().hex works as a batch ID
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir

def build_stored_relative_path(upload_dir: Path, filename: str) -> str:
    file_path = upload_dir / filename
    return str(file_path.relative_to(UPLOAD_BASE_DIR.parent.parent))

def save_uploaded_file(upload_dir: Path, filename: str, file_bytes: bytes) -> str:
    file_path = upload_dir / filename
    file_path.write_bytes(file_bytes)
    return build_stored_relative_path(upload_dir, filename)

def parse_csv_bytes(file_bytes: bytes) -> list[dict[str, str]]:
    csv_text = file_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(csv_text))
    return [dict(row) for row in reader]

# VALIDATION ADAPTER
def validate_uploaded_files(uploaded_files: list[tuple[str, bytes]]) -> dict:
    # call ValidatorDisptcher.validate_files(...)
    # return raw validation result
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
    return row

# RESPONSE MODEL BUILDERS
def build_file_validation_models(validation_result: dict) -> list[FileValidationResult]:
    # convert raw per-file dicts into pydantic models
    file_results = [
        FileValidationResult(**result) for result in validation_result["files"]
    ]
    return file_results

def build_validation_summary(validation_result: dict, file_results: list[FileValidationResult]) -> UploadValidationSummary:
    validation_summary = UploadValidationSummary(is_valid=validation_result["is_valid"],
                                                 files=file_results)
    return validation_summary

def build_dataset_response_models(dataset_rows: list[dict]) -> list[DatasetResponse]:
    # convert created DB rows into DatasetResponse models
    dataset_responses = []
    for row in dataset_rows:
        dataset_response = DatasetResponse(**row)
        dataset_responses.append(dataset_response)
    return dataset_responses
