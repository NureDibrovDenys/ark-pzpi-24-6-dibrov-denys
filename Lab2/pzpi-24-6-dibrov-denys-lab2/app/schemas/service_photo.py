

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class ServicePhotoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    description: str | None = Field(..., max_length = 255)
    
    
class ServicePhotoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    id: int
    service_session_id: int
    description: str | None
    uploaded_at: AwareDatetime 