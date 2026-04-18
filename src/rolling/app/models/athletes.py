from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator


class AthleteCreate(BaseModel):
    """
    Represents the data required to create a new athlete.
    
    Attributes:
        external_code (str): The external code for the new athlete.
        dataset_id (UUID): The ID of the dataset to which the athlete belongs.
        birth_date (Optional[date]): The birth date of the athlete.
        birth_year (Optional[int]): The year of birth of the athlete.
        age_at_observation (Optional[int]): The age of the athlete at the time of observation.
        age_logged_at (Optional[date]): The date when the athlete's age was logged.
        notes (Optional[str]): Any additional notes about the athlete.
    """
    external_code: str
    dataset_id: UUID
    birth_date: Optional[date] = None
    birth_year: Optional[int] = None
    age_at_observation: Optional[int] = None
    age_logged_at: Optional[date] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_age_fields(self):
        """
        Validates that at least one of birth_date, birth_year, or age_at_observation is provided.
        
        Returns:
            AthleteCreate: The validated AthleteCreate instance.
            
        Raises:
            ValueError: If none of birth_date, birth_year, or age_at_observation is provided.
        """
        if (self.birth_date is None
            and self.birth_year is None
            and self.age_at_observation is None
            ):
            raise ValueError(
                "At least one of birth_date, birth_year, or age_at_observation must be provided."
            )
        return self

class AthleteResponse(BaseModel):
    """
    Represents the data returned for an existing athlete.
    
    Attributes:
        athlete_id (UUID): The unique identifier for the athlete.
        external_code (str): The external code for the athlete.
        birth_date (Optional[date]): The birth date of the athlete. By default, this field is None.
        birth_year (Optional[int]): The year of birth of the athlete. By default, this field is None.
        age_at_observation (Optional[int]): The age of the athlete at the time of observation. By default, this field is None.
        age_logged_at (Optional[date]): The date when the athlete's age was logged. By default, this field is None.
        notes (Optional[str]): Any additional notes about the athlete. By default, this field is None.
        created_at (datetime): The timestamp when the athlete was created.
        updated_at (datetime): The timestamp when the athlete was last updated."""
    athlete_id: UUID
    external_code: str
    birth_date: Optional[date] = None
    birth_year: Optional[int] = None
    age_at_observation: Optional[int] = None
    age_logged_at: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
