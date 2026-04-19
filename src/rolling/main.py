from fastapi import FastAPI

from rolling.app.config import dbSettings
from rolling.app.db import get_connection
from rolling.app.routes.analysts import router as analysts_router
from rolling.app.routes.projects import router as projects_router
from rolling.app.routes.datasets import router as datasets_router
from rolling.app.routes.analyses import router as analyses_router

app = FastAPI(title=dbSettings.app_name)
app.include_router(analysts_router)
app.include_router(projects_router)
app.include_router(datasets_router)
app.include_router(analyses_router)

@app.get("/")
def root(): # TODO add return type
    """
    Returns the application name and environment.

    This endpoint serves as the landing page for the API, confirming that the service is reachable via web browser or client.

    Returns:
        dict: A dictionary describing the landing page.
            - "name" (str) : The application name.
            - "environment" (str) : The application environment.
    """
    return {
        "name": dbSettings.app_name,
        "environment": dbSettings.app_env
        }

@app.get("/health")
def health() -> dict[str, str | bool]:
    """
    Performs a basic health check of the application.

    This endpoint verifies that the application instance is healthy and ready to serve

    Returns:
        dict: A dictionary describing the health of the application.
            - "ok" (bool): True if the application can connect to the database.
            - "app_name" (str): Name of the application.
            - "enivornment" (str) : Enviroment of the application.
            - "database" (str) : connection status of the database
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return {"ok": True,
                "app_name": dbSettings.app_name,
                "environement": dbSettings.app_env, # TODO fix typo
                "database": "connected",
                }
    except Exception as e:
        return {
            "ok": False,
            "app_name": dbSettings.app_name,
            "environemnt": dbSettings.app_env,
            "database": f"Error: {e}",
            }