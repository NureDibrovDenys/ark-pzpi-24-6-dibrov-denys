from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from database import check_database_connection

app = FastAPI(
    title = "DroneCare API",
    description = "API for DroneCare application",
)

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
