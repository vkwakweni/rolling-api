from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PerformanceCreate(BaseModel):
    """
    Represents the data required to create a new performance record.
    
    Attributes:
        athlete_id (UUID): The ID of the athlete for whom the performance was recorded.
        dataset_id (UUID): The ID of the dataset to which the performance belongs.
        performance_type (UUID): The ID of the type of performance being recorded.
        metric_type (int): The ID of the type of metric being recorded (e.g. heart rate, power output).
        metric_value (float): The value of the performance metric.
        metric_unit (Optional[str]): The unit of measurement for the performance metric value. By default, this is None.
        observed_on (date): The date on which the performance was observed.
    """
    athlete_id: UUID
    dataset_id: UUID
    perfromance_type: UUID # TODO fix typo in column name
    metric_type: int # BIGINT
    metric_value: float
    metric_unit: Optional[str]
    observed_on: date

class PerformanceResponse(BaseModel):
    """
    Represents a performance record as stored in the database, including metadata such as creation and update timestamps
    
    Attributes:
        performance_record_id (UUID): The unique identifier for the performance record.
        athlete_id (UUID): The ID of the athlete for whom the performance was recorded.
        dataset_id (UUID): The ID of the dataset to which the performance belongs.
        performance_type (UUID): The ID of the type of performance being recorded.
        metric_type (int): The ID of the type of metric being recorded (e.g. heart rate, power output).
        metric_value (float): The value of the performance metric.
        metric_unit (Optional[str]): The unit of measurement for the performance metric value. By default, this is None.
        observed_on (date): The date on which the performance was observed.
        created_at (datetime): The timestamp when the record was created.
        updated_at (datetime): The timestamp when the record was last updated.
    """
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
