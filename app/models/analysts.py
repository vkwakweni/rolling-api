from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

# TODO: docstrings for classes

class AnalystCreate(BaseModel):
    username: str
    email: EmailStr
    password_hash: str
    password_salt: str

class AnalystResponse(BaseModel):
    analyst_id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    