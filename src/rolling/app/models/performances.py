from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

# TODO docstring for classes

class PerformanceCreate(BaseModel):
    athlete_id: UUID
    dataset_id: UUID
    perfromance_type: UUID
    metric_type: int # BIGINT
    metric_value: float
    metric_unit: Optional[str]
    observed_on: date

class PerformanceResponse(BaseModel):
    performance_record_id: UUID
    athlete_id: UUID
    dataset_id: UUID
    performance_type: UUID
    metric_type: int
    metric_value: float
    metric_unit: Optional[str]
    observed_on: date
    created_at: datetime
    updated_at: datetime
