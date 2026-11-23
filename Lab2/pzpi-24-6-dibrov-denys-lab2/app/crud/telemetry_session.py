from datetime import datetime, timezone
from os import stat

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import delete, select
from app.models.telemetry.telemetry_session import TelemetrySession
from app.schemas.telemetry_session import TelemetrySessionCreate


def create_telemetry_session(db: Session, data: TelemetrySessionCreate) -> TelemetrySession:
   session_data = data.model_dump()

   if session_data["started_at"] is None:
      session_data["started_at"] = datetime.now(timezone.utc)

   db_session = TelemetrySession(**session_data)

   db.add(db_session)
   db.commit()
   db.refresh(db_session)
   
   return db_session

def get_telemetry_sessions(db: Session, offset: int = 0, limit: int = 50, service_session_id: int | None = None)-> list[TelemetrySession]:
   statement = select(TelemetrySession)
   
   if service_session_id is not None:
      statement = statement.where(TelemetrySession.service_session_id == service_session_id)
      
   statement = statement.order_by(TelemetrySession.id.desc()).offset(offset).limit(limit)
   
   return list(db.scalars(statement).all())


def get_telemetry_session(db: Session, session_id: int) -> TelemetrySession:
   telemetry_session = db.get(TelemetrySession, session_id)
   
   if telemetry_session is None: 
      raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail="Телеметрію не знайдено"
      )
      
   return telemetry_session
      
def end_telemetry_session(db: Session, session_id: int, ended_at: datetime | None = None)->TelemetrySession:
   session = get_telemetry_session(db, session_id)
   

  
   session.ended_at = ended_at or datetime.now(timezone.utc)
    

   db.commit()
   db.refresh(session)
   
   return session