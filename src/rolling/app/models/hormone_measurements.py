from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator

class HormoneMeasurementCreate(BaseModel):
    """
    Represents the data required to create a new hormone measurement record.
    
    Attributes:
        athlete_id (UUID): The ID of the athlete for whom the measurement was taken.
        dataset_id (UUID): The ID of the dataset to which the measurement belongs.
        hormone_id (UUID): The ID of the hormone being measured.
        measured_value (float): The value of the hormone measurement.
        unit (Optional[str]): The unit of measurement for the hormone value.
        observed_on (date): The date on which the hormone measurement was observed.
    """
    athlete_id: UUID
    dataset_id: UUID
    hormone_id: UUID
    measured_value: float
    unit: Optional[str] = None
    observed_on: date


class HormoneMeasurementResponse(BaseModel):
    """
    Represents a hormone measurement record as stored in the database, including metadata such as creation and update timestamps.
    
    Attributes:
        hormone_measurement_id (UUID): The unique identifier for the hormone measurement record.
        dataset_id (UUID): The ID of the dataset to which the measurement belongs.
        athlete_id (UUID): The ID of the athlete for whom the measurement was taken.
        hormone_id (int): The ID of the hormone being measured.
        measured_value (float): The value of the hormone measurement.
        unit (Optional[str]): The unit of measurement for the hormone value.
        observed_on (date): The date on which the hormone measurement was observed.
        created_at (datetime): The timestamp when the record was created.
        updated_at (datetime): The timestamp when the record was last updated.
    """
    hormone_measurement_id: UUID
    dataset_id: UUID
    athlete_id: UUID
    hormone_id: int
    measured_value: float
    unit: Optional[str]
    observed_on: date
    created_at: datetime
    updated_at: datetime