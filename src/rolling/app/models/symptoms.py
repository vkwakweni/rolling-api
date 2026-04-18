from datetime import datetime, date
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel


class SymptomCreate(BaseModel):
    """
    Represents the data required to create a new symptom record for an athlete.
    
    Attributes:
        athlete_id (UUID): Unique identifier for the athlete.
        dataset_id (UUID): Unique identifier for the dataset to which this symptom record belongs.
        symptom_id (int): An integer representing the type of symptom observed (e.g. 1 for cramps, 2 for bloating, etc.)
        observed_on (date): The date on which the symptom was observed.
        symptom_severity (Optional[Literal["MILD", "MODERATE", "SEVERE"]]): An optional field representing the severity of the symptom observed.
        notes (Optional[str]): An optional field for any additional notes about the symptom observation.
        relative_day_to_cycle (Optional[int]): An optional field representing the number of days since the first menstrual bleeding (the beginning of a new menstrual cycle) on which the symptom was observed.
    """
    athlete_id: UUID
    dataset_id: UUID
    symptom_id: int
    observed_on: date
    symptom_severity: Optional[Literal["MILD", "MODERATE", "SEVERE"]]
    notes: Optional[str]
    relative_day_to_cycle: Optional[int]

class SymptomResponse(BaseModel):
    """
    Represents a symptom record as stored in the database, including metadata such as creation and update timestamps.

    Attributes:
        symptom_record_id (UUID): The unique identifier for the symptom record.
        athlete_id (UUID): Unique identifier for the athlete.
        dataset_id (UUID): Unique identifier for the dataset to which this symptom record belongs.
        symptom_id (int): An integer representing the type of symptom observed (e.g. 1 for cramps, 2 for bloating, etc.)
        observed_on (date): The date on which the symptom was observed.
        symptom_severity (Optional[Literal["MILD", "MODERATE", "SEVERE"]]): An optional field representing the severity of the symptom observed.
    """
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