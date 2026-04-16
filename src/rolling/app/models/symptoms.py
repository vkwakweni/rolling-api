from datetime import datetime, date
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel

# TODO docstrings

class SymptomCreate(BaseModel):
    athlete_id: UUID
    dataset_id: UUID
    symptom_id: int
    observed_on: date
    symptom_severity: Optional[Literal["MILD", "MODERATE", "SEVERE"]]
    notes: Optional[str]
    relative_day_to_cycle: Optional[int]

class SymptomResponse(BaseModel):
    # TODO these names will be changed
    symptom_record_id: UUID
    athlete_id: UUID
    dataset_id: UUID
    symptom_id: int
    observed_on: date
    symptom_severity: Optional[Literal["MILD", "MODERATE", "SEVERE"]]
    notes: Optional[str]
    relative_day_to_cycle: Optional[int]
    created_at: datetime
    updated_at: datetime