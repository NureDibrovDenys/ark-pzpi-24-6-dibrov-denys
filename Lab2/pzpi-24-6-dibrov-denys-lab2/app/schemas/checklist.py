from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


ChecklistName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]

ChecklistItemTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=150,
    ),
]


class ChecklistItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: ChecklistItemTitle

    sort_order: int = Field(
        ge=1,
        strict=True,
    )

    is_required: bool = Field(
        default=True,
        strict=True,
    )


class ChecklistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    checklist_id: int
    title: str
    sort_order: int
    is_required: bool


class ChecklistCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: ChecklistName

    description: str | None = Field(
        default=None,
        max_length=255,
    )

    items: list[ChecklistItemCreate] = Field(
        min_length=1,
        max_length=100,
    )

    @model_validator(mode="after")
    def validate_item_order(self) -> Self:
        positions = [item.sort_order for item in self.items]

        if len(positions) != len(set(positions)):
            raise ValueError(
                "Позиції пунктів sort_order не повинні повторюватися"
            )

        return self


class ChecklistUpdate(ChecklistCreate):
    description: str | None = Field(
        ...,
        max_length=255,
    )


class ChecklistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    items: list[ChecklistItemResponse]