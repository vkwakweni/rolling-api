from uuid import UUID

from app.dependencies.auth import get_current_analyst_id

from app.models.datasets import DatasetUploadResponse
from app.services.dataset_upload import process_dataset_upload

from fastapi import APIRouter, Depends, UploadFile, File

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_data_files(project_id: UUID,
                            files: list[UploadFile] = File(...), # expects a multipart data request
                            current_analyst_id: UUID = Depends(get_current_analyst_id)) -> DatasetUploadResponse:
    return await process_dataset_upload(project_id=project_id,
                                        current_analyst_id=current_analyst_id,
                                        files=files)
