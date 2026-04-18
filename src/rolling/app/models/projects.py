from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class ProjectCreate(BaseModel):
    """
    Represents the data required to create a new project.

    Attributes:
        name (str): The name of the project.
        description (Optional[str]): A brief description of the project. By default, this is None.
    """
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    """
    Represents a project record as stored in the database, including metadata such as creation and update timestamps.
    
    Attributes:
        project_id (UUID): The unique identifier for the project.
        owner_analyst_id (UUID): The ID of the analyst who owns the project.
        name (str): The name of the project.
        description (Optional[str]): A brief description of the project. By default, this is None.
        created_at (datetime): The timestamp when the record was created.
        updated_at (datetime): The timestamp when the record was last updated.
    """
    project_id: UUID
    owner_analyst_id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ProjectShareCreate(BaseModel):
    """
    Represents the data required to share a project with another analyst.
    
    Attributes:
        project_id (UUID): The ID of the project to be shared.
        analyst_id (UUID): The ID of the analyst with whom the project is to be shared.
    """
    project_id: UUID
    analyst_id: UUID

class ProjectMemberResponse(BaseModel):
    """
    Represents a member of a project, including their details and the timestamp when they were added.

    Attributes:
        analyst_id (UUID): The ID of the analyst.
        username (str): The username of the analyst.
        email (EmailStr): The email address of the analyst.
        created_at (datetime): The timestamp when the analyst was added to the project.
    """
    analyst_id: UUID
    username: str
    email: str # TODO change to EmailStr after fixing circular import issue
    created_at: datetime