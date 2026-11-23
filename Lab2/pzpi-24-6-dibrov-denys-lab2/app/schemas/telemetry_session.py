

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

class TelemetrySessionBase(BaseModel):
    description: str | None = Field(default=None, max_length=255)


class TelemetrySessionCreate(TelemetrySessionBase):
    model_config = ConfigDict(extra="forbid")
    
    service_session_id: int = Field(gt=0, strict=True)
    started_at: AwareDatetime | None = None

class TelemetrySessionUpdate(TelemetrySessionBase):
    model_config = ConfigDict(extra="forbid")

    ended_at: AwareDatetime | None = None    

class TelemetrySessionResponse(TelemetrySessionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    service_session_id: int
    started_at: AwareDatetime
    ended_at: AwareDatetime |  None

    
    