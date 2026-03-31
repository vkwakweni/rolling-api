from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class CyclePhaseCreate(BaseModel):
    athlete_id: UUID
    dataset_id: UUID
    observed_on: date
    cycle_phase_type: int
    cycle_day: Optional[int]
    
class CyclePhaseResponse(BaseModel):
    cycle_phase_record_id: UUID
    athlete_id: UUID
    dataset_id: UUID
    observed_on: date
    cycle_phase_type: int
    cycle_day: int
    created_at: datetime
    updated_at: datetime
