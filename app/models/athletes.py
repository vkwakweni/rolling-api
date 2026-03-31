from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator

# TODO: docstrings for classes

class AthleteCreate(BaseModel):
    external_code: str
    dataset_id: UUID
    birth_date: Optional[date] = None
    birth_year: Optional[int] = None
    age_at_observation: Optional[int] = None
    age_logged_at: Optional[date] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_age_fields(self):
        if (self.birth_date is None
            and self.birth_year is None
            and self.age_at_observation is None
            ):
            raise ValueError(
                "At least one of birth_date, birth_year, or age_at_observation must be provided."
            )
        return self

class AthleteResponse(BaseModel):
    athlete_id: UUID
    external_code: str
    birth_date: Optional[date] = None
    birth_year: Optional[int] = None
    age_at_observation: Optional[int] = None
    age_logged_at: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
