from uuid import UUID

from rolling.app.dependencies.auth import get_current_analyst_id

from rolling.app.models.datasets import DatasetUploadResponse
from rolling.app.services.dataset_upload import process_dataset_upload

from fastapi import APIRouter, Depends, UploadFile, File

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_data_files(project_id: UUID,
                            files: list[UploadFile] = File(...), # expects a multipart data request
                            current_analyst_id: UUID = Depends(get_current_analyst_id)) -> DatasetUploadResponse:
    """
    Persists uploaded files to the database.

    This endpoint receives files, which are then validated, and if successful, persisted to the database. It validates if
    the current analyst can access the project.

    Args:
        project_id (UUID): The ID of the project to which to upload the files.
        files (list[UploadFile]): The files to upload.
        current_analyst_id (UUID): The current analyst ID.

    Returns:
        DatasetUploadResponse: The result of the dataset upload.

    Raises:
        HTTPException:
            - HTTP_403_FORBIDDEN: If the analyst is not allowed to access the project.
            - HTTP_400_BAD_REQUEST: If a file import was unsuccessful.
    """
    return await process_dataset_upload(project_id=project_id,
                                        current_analyst_id=current_analyst_id,
                                        files=files)
