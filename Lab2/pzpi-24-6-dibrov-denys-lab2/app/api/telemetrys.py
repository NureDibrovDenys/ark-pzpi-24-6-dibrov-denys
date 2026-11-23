
from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.schemas.telemetry_session import TelemetrySessionCreate, TelemetrySessionResponse
from app.models.user import User
from app.crud import telemetry_session as telemetry_crud
from database import get_db


router = APIRouter(prefix="/telemetry/sessions")

@router.post(
    "",
    response_model=TelemetrySessionResponse,
    status_code= status.HTTP_201_CREATED
)
def create_session(
    data:TelemetrySessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return telemetry_crud.create_telemetry_session(db, data)