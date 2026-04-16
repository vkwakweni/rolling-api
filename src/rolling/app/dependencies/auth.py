from uuid import UUID

from fastapi import Header, HTTPException, status

def get_current_analyst_id(x_analyst_id: str = Header(..., alias="X-Analyst-Id")) -> UUID:
    try:
        return UUID(x_analyst_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid X-Analyst-Id header",
                            ) from e