from email.policy import strict
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from app.core.enums import DroneStatus

from app.core.enums import DroneStatus
from database import Base

#кастомні типи даних (шаблони)
Text100 = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100
    )
]

SerianlNumber = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255
        
    )
]


class DroneBase(BaseModel):
    name: Text100
    serial_number: SerianlNumber
    manufacturer: Text100
    model: Text100
    
    max_flight_time: int = Field(gt=0, strict=True, description = "Максимальний час польоту у хвилинах")
    
    
class DroneCreate(DroneBase):
    model_config = ConfigDict(extra="forbid")
    
    status: DroneStatus = DroneStatus.WORKING
    
class DroneUpdate(DroneBase):
    model_config = ConfigDict(extra="forbid")

    status: DroneStatus
    
class DroneResponse(DroneBase):
    model_config = ConfigDict(from_attributes=True)

    id:int
    owner_id:int
    status: DroneStatus