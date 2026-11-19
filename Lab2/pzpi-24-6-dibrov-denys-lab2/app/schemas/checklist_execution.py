from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
)

from app.core.enums import (
    ChecklistAnswerStatus,
    CheckListExecutionStatus,
)


class ChecklistExecutionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checklist_id: int = Field(gt=0, strict=True)


class ChecklistAnswerSave(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ChecklistAnswerStatus

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ChecklistAnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    execution_id: int
    checklist_items_id: int
    status: ChecklistAnswerStatus
    comment: str | None


class ChecklistExecutionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    checklist_id: int
    service_session_id: int
    started_at: AwareDatetime
    completed_at: AwareDatetime | None
    status: CheckListExecutionStatus


class ChecklistExecutionResponse(ChecklistExecutionSummary):
    answers: list[ChecklistAnswerResponse]