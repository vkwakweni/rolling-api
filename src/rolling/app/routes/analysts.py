from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from rolling.app.models.analysts import AnalystCreate, AnalystResponse
from rolling.app.repositories.analysts import create_analyst, get_analyst_by_id, get_analyst_by_username

router = APIRouter(prefix="/analysts", tags=["analysts"])

@router.post("", response_model=AnalystResponse, status_code=status.HTTP_201_CREATED)
def create_analyst_route(payload: AnalystCreate) -> AnalystResponse:
    existing = get_analyst_by_username(payload.username)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Analyst username already exists",
                            )
    
    # TODO: implement username restrictions somewhere
    row = create_analyst(username=payload.username,
                         email=payload.email,
                         password_hash=payload.password_hash,
                         password_salt=payload.password_salt,
                         )
    return AnalystResponse(**row)

@router.get("/{analyst_id}", response_model=AnalystResponse)
def get_analyst_route(analyst_id: UUID) -> AnalystResponse:
    row = get_analyst_by_id(analyst_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Analyst not found",
                            )
    # TODO if it gets a value that's not a UUID, its gets 422 Unprocessable Entity response
    return AnalystResponse(**row)

# TODO get analyst by username in url (should redirect?)
# TODO get all analysts
