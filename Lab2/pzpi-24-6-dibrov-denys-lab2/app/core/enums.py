from enum import Enum

class DroneStatus(str, Enum):
    WORKING = "working"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    
class ChecklistAnswerStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"
    
class CheckListExecutionStatus(str, Enum):
    IN_PROGRESS = "in_progres"
    COMPLETED = "completed"