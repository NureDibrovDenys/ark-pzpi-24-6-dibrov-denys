from datetime import datetime, timezone
from typing import Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class ServiceSessionBase(BaseModel):
    started_at: AwareDatetime
    ended_at: AwareDatetime | None = None

    description: str | None = Field(
        default=None,
        max_length=255,
    )

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if (
            self.ended_at is not None
            and self.ended_at < self.started_at
        ):
            raise ValueError(
                "Дата завершення не може бути раніше дати початку"
            )

        return self


class ServiceSessionCreate(ServiceSessionBase):
    model_config = ConfigDict(extra="forbid")

    started_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ServiceSessionUpdate(ServiceSessionBase):
    model_config = ConfigDict(extra="forbid")

    ended_at: AwareDatetime | None = Field(...)
    description: str | None = Field(..., max_length=255)


class ServiceSessionResponse(ServiceSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    drone_id: int