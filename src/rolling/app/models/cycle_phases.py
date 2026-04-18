from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class CyclePhaseCreate(BaseModel):
    """
    Represents the input data required to create a cycle phase record for an athlete on a specific day.
    
    Attributes:
        athlete_id (UUID): Unique identifier for an athlete.
        dataset_id (UUID): Unique identifier for the dataset to which the cycle phase record belongs.
        observed_on (date): The date on which the cycle phase was observed.
        cycle_phase_type (int): An integer representing the type of cycle phase (e.g. 'LUTEAL', 'FOLLICULAR', 'MENSTRUATION', 'OVULATION').
        cycle_day (Optional[int]): The day of the cycle corresponding to the observed date, where day 1 is the first day of menstrual bleeding. This field is optional because it may not always be possible to determine the exact cycle day.
    """
    athlete_id: UUID
    dataset_id: UUID
    observed_on: date
    cycle_phase_type: int
    cycle_day: Optional[int]
    
class CyclePhaseResponse(BaseModel):
    """
    Represents the data returned for an existing cycle phase record.
    
    Attributes:
        cycle_phase_record_id (UUID): Unique identifier for the cycle phase record.
        athlete_id (UUID): Unique identifier for an athlete.
        dataset_id (UUID): Unique identifier for the dataset to which the cycle phase record belongs.
        observed_on (date): The date on which the cycle phase was observed.
        cycle_phase_type (int): An integer representing the type of cycle phase (e.g. 'LUTEAL', 'FOLLICULAR', 'MENSTRUATION', 'OVULATION').
        cycle_day (Optional[int]): The day of the cycle corresponding to the observed date, where day 1 is the first day of menstrual bleeding. This field is optional because it may not always be possible to determine the exact cycle day.
        created_at (datetime): The date and time when the cycle phase record was created.
        updated_at (datetime): The date and time when the cycle phase record was last updated.
    """
    cycle_phase_record_id: UUID
    athlete_id: UUID
    dataset_id: UUID
    observed_on: date
    cycle_phase_type: int
    cycle_day: int
    created_at: datetime
    updated_at: datetime
