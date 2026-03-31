from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator

class HormoneMeasurementCreate(BaseModel):
    athlete_id: UUID
    dataset_id: UUID
    hormone_id: UUID
    measured_value: float
    unit: Optional[str] = None
    observed_on: date


class HormoneMeasurementResponse(BaseModel):
    hormone_measurement_id: UUID
    dataset_id: UUID
    athlete_id: UUID
    hormone_id: int
    measured_value: float
    unit: Optional[str]
    observed_on: date
    created_at: datetime
    updated_at: datetime