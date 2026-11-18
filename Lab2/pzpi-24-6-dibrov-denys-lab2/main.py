from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from database import check_database_connection

from app.api.auth import router as auth_router
from app.api.drones import router as drones_router
from app.api.components import router as components_router

app = FastAPI(
    title = "DroneCare API",
    description = "API for DroneCare application",
)

app.include_router(auth_router)
app.include_router(drones_router)
app.include_router(components_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to DroneCare API!"}


@app.get("/check-db-connection")
def check_db():
    try:
        database_name = check_database_connection()
        return {
            "status": "connected",
            "database": database_name
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e)
        }
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Не вдалося підключитися до бази даних",
        )

