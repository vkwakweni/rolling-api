from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from rolling.app.dependencies.auth import get_current_analyst_id
from rolling.app.models.projects import ProjectCreate, ProjectResponse, ProjectShareCreate, ProjectMemberResponse
from rolling.app.repositories.projects import (create_project, get_project_by_id,
                                       get_project_by_name, list_projects_for_analyst,
                                       analyst_can_access_project, share_project_with_analyst,
                                       list_project_members, analyst_can_share_project)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project_route(payload: ProjectCreate,
                         current_analyst_id: UUID = Depends(get_current_analyst_id)
                         ) -> ProjectResponse:
    """
    Creates a new project and persists it to the database.

    This endpoint received a JSON payload for creating a project record, persists it to the  database, and returns a
    structured project record response. It first verifies if the project name exists.

    Args:
        payload (ProjectCreate): A Pydantic model with the data needed to create a project.
        current_analyst_id (UUID): The analyst creating the project.

    Returns:
        ProjectResponse: The created project record.

    Raises:
        HTTPException: If the submitted project name already exists (409 Conflict).
    """
    existing = get_project_by_name(payload.name, current_analyst_id)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Project name already exists for this analyst",
                            )
    
    row = create_project(owner_analyst_id=current_analyst_id,
                         name=payload.name,
                         description=payload.description
                         )
    return ProjectResponse(**row)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_route(project_id: UUID,
                      current_analyst_id: UUID = Depends(get_current_analyst_id)) -> ProjectResponse:
    """
    Retrieves the details of a given project.

    This endpoint queries the database to find a project by its ID. It first verifies if the project exists, then if the
    current analyst can access the project.

    Args:
        project_id (UUID): The ID of the project to be retrieved.
        current_analyst_id (UUID): The current analyst accessing the project.

    Returns:
        ProjectResponse: The retrieved project.

    Raises:
        HTTPException:
            - If the project does not exist (404 Not Found).
            - If the analyst cannot access the project (403 Forbidden).
    """
    row = get_project_by_id(project_id)

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Project not found",)
    
    if not analyst_can_access_project(current_analyst_id, project_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not allowed to access this project",)
    return ProjectResponse(**row)

@router.get("/user/{project_name}", response_model=ProjectResponse)
def get_project_route_by_name(project_name: str,
                              current_analyst_id: UUID = Depends(get_current_analyst_id)) -> ProjectResponse:
    """
    Retrieves the details of a given project.

    This endpoint queries the database to find a project by its ID. It first verifies if the project exists, then if the
    current analyst can access the project.

    Args:
        project_name (UUID): The name of the project to be retrieved.
        current_analyst_id (UUID): The current analyst accessing the project.

    Returns:
        ProjectResponse: The retrieved project.

    Raises:
        HTTPException:
            - If the project does not exist (404 Not Found).
            - If the analyst cannot access the project (403 Forbidden).
    """
    row = get_project_by_name(name=project_name, owner_analyst_id=current_analyst_id)

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Project not found",)
    
    if not analyst_can_access_project(current_analyst_id, row["project_id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not allowed to access this project",)
    return ProjectResponse(**row)

@router.get("", response_model=list[ProjectResponse])
def list_projects_route(current_analyst_id: UUID = Depends(get_current_analyst_id),
                        ) -> list[ProjectResponse]:
    """
    Retrieves a list of projects associated with the current analyst.

    This endpoint queries the database to find the projects associated with the current analyst.

    Args:
        current_analyst_id (UUID): The analyst for whom to check projects.

    Returns:
        list[ProjectResponse]: The list of projects associated with the current analyst. If no records are found, an empty list is returned.
    """
    rows = list_projects_for_analyst(current_analyst_id)
    return [ProjectResponse(**row) for row in rows]

@router.post("/{project_id}/share", response_model=list[ProjectMemberResponse])
def share_project_route(project_id: UUID,
                        members_to_share: list[ProjectShareCreate],
                        current_analyst_id: UUID = Depends(get_current_analyst_id),) -> list[ProjectMemberResponse]:
    """
    Grants access to the given project to the given members, only if the current analyst is validated.

    This endpoint grants access to the project to the given members, only if the current analyst is validated. It first
    validates that the current analyst can share the project. A list of project members is returned.

    Args:
        project_id (UUID): The project to be shared.
        members_to_share (list[ProjectShareCreate]): The members to grant access to the project.
        current_analyst_id (UUID): The analyst to share the project.
    """
    if not analyst_can_share_project(current_analyst_id, project_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not allowed to share this project")
    
    shared_project_members = list()
    for member in members_to_share:
        row = share_project_with_analyst(project_id=project_id, analyst_id=member.analyst_id)
        if row is not None:
            shared_project_members.append(ProjectMemberResponse(**row))

    return shared_project_members

@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
def list_project_members_route(project_id: UUID,
                               current_analyst_id: UUID = Depends(get_current_analyst_id),) -> list[ProjectMemberResponse]:
    """
    Retrieves the list of members associated with the given project.

    This endpoint queries the database to find the projects members associated with the given project. It first verifies
    if the current analyst can access the project.

    Args:
        project_id (UUID): The project to be accessed.
        current_analyst_id (UUID): The analyst to access the project.

    Returns:
        list[ProjectMemberResponse]: The list of members associated with the current analyst.

    Raises:
        HTTPException: If the current analyst is not allowed to access the project (403 Forbidden).
    """
    if not analyst_can_access_project(current_analyst_id, project_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not allowed to access this project",)
    return [ProjectMemberResponse(**row) for row in list_project_members(project_id)]
