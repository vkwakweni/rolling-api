from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

# TODO docstrings for class

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    project_id: UUID
    owner_analyst_id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ProjectShareCreate(BaseModel):
    analyst_id: UUID

class ProjectMemberResponse(BaseModel):
    analyst_id: UUID
    username: str
    email: str
    created_at: datetime