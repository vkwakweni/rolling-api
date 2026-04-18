from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class AnalystCreate(BaseModel):
    """
    Represents the data required to create a new analyst.
    
    Attributes:
        username (str): The username for the new analyst.
        email (EmailStr): The email address for the new analyst.
        password_hash (str): The hashed password for the new analyst.
        password_salt (str): The salt used for hashing the password.
    """
    username: str
    email: EmailStr
    password_hash: str
    password_salt: str

class AnalystResponse(BaseModel):
    """
    Represents the data returned for an existing analyst.
    
    Attributes:
        analyst_id (UUID): The unique identifier for the analyst.
        username (str): The username for the analyst.
        email (EmailStr): The email address for the analyst.
        created_at (datetime): The timestamp when the analyst was created.
        updated_at (datetime): The timestamp when the analyst was last updated.
    """
    analyst_id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    