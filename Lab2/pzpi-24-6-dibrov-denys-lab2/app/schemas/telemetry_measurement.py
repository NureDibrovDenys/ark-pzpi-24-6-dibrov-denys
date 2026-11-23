
from pydantic import AwareDatetime, BaseModel, Field, ConfigDict


class TelemetryMeasurementCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    measured_at: AwareDatetime | None = None
    acceleration_x: float
    acceleration_y: float
    acceleration_z: float
    
    temperature_c: float
    
    voltage_v: float = Field(ge=0)
    
class TelemetryMeasurementResponse(TelemetryMeasurementCreate):
    model_config = ConfigDict(extra="forbid")
    
    id: int
    telemetry_session_id: int
    measured_at: AwareDatetime