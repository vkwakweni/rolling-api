from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_analyst_id
from app.models.projects import ProjectCreate, ProjectResponse, ProjectShareCreate, ProjectMemberResponse
from app.repositories.projects import (create_project, get_project_by_id,
                                       get_project_by_name, list_projects_for_analyst,
                                       analyst_can_access_project, share_project_with_analyst,
                                       list_project_members, analyst_can_share_project)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project_route(payload: ProjectCreate,
                         current_analyst_id: UUID = Depends(get_current_analyst_id)
                         ) -> ProjectResponse:
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
    row = get_project_by_id(project_id)

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Project not found",)
    
    if not analyst_can_access_project(current_analyst_id, project_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not allowed to access this project",)
    return ProjectResponse(**row)

@router.get("", response_model=list[ProjectResponse])
def list_projects_route(current_analyst_id: UUID = Depends(get_current_analyst_id),
                        ) -> list[ProjectResponse]:
    rows = list_projects_for_analyst(current_analyst_id)
    return [ProjectResponse(**row) for row in rows]

@router.post("/{project_id}/share", response_model=list[ProjectMemberResponse])
def share_project_route(project_id: UUID,
                        members_to_share: list[ProjectShareCreate],
                        current_analyst_id: UUID = Depends(get_current_analyst_id),) -> list[ProjectMemberResponse]:
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
    if not analyst_can_access_project(current_analyst_id, project_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not allowed to access this project",)
    return [ProjectMemberResponse(**row) for row in list_project_members(project_id)]
