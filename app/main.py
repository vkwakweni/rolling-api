from fastapi import FastAPI

from app.config import dbSettings
from app.db import get_connection
from app.routes.analysts import router as analysts_router
from app.routes.projects import router as projects_router
from app.routes.datasets import router as datasets_router
from app.routes.analyses import router as analyses_router

app = FastAPI(title=dbSettings.app_name)
app.include_router(analysts_router)
app.include_router(projects_router)
app.include_router(datasets_router)
app.include_router(analyses_router)

@app.get("/")
def root():
    return {
        "name": dbSettings.app_name,
        "environment": dbSettings.app_env
        }

@app.get("/health")
def health() -> dict[str, str | bool]:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return {"ok": True,
                "app_name": dbSettings.app_name,
                "environement": dbSettings.app_env,
                "database": "connected",
                }
    except Exception as e:
        return {
            "ok": False,
            "app_name": dbSettings.app_name,
            "environemnt": dbSettings.app_env,
            "database": f"Error: {e}",
            }