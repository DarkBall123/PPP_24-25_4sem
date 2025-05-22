from enum import Enum
from pydantic import BaseModel

class Status(str, Enum):
    started = "STARTED"
    progress = "PROGRESS"
    completed = "COMPLETED"

class StartedEvent(BaseModel):
    status: Status = Status.started
    task_id: str
    word: str
    algorithm: str

class ProgressEvent(BaseModel):
    status: Status = Status.progress
    task_id: str
    progress: int
    current_word: str

class CompletedEvent(BaseModel):
    status: Status = Status.completed
    task_id: str
    execution_time: float
    results: list
