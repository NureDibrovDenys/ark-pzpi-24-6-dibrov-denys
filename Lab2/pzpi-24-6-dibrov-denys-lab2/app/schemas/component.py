from datetime import datetime, timezone
from typing import Annotated, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


ComponentName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]

ComponentSerial = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]


class ComponentBase(BaseModel):
    name: ComponentName
    serial_number: ComponentSerial

    installed_at: AwareDatetime

    operating_hours: int = Field(
        ge=0,
        strict=True,
        description="Напрацювання компонента в цілих годинах",
    )

    removed_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if (
            self.removed_at is not None
            and self.removed_at < self.installed_at
        ):
            raise ValueError(
                "Дата зняття не може бути раніше дати встановлення"
            )

        return self


class ComponentCreate(ComponentBase):
    model_config = ConfigDict(extra="forbid")

    installed_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    operating_hours: int = Field(
        default=0,
        ge=0,
        strict=True,
    )


class ComponentUpdate(ComponentBase):
    model_config = ConfigDict(extra="forbid")

    # PUT вимагає явно передати дату зняття або null.
    removed_at: AwareDatetime | None = Field(...)


class ComponentResponse(ComponentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    drone_id: int