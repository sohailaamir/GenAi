
from typing import Literal, Optional
from pydantic import BaseModel, Field

class Decision(BaseModel):
    agent: Literal["translate", "summarize", "calculate"] = Field(..., description="Which node to route to")
    input: str = Field("", description="The original input to process")

class TaskResult(BaseModel):
    result: str = Field(..., description="Final textual result")

class AppState(BaseModel):
    task: str
    input: str
    agent: Optional[str] = None
    result: Optional[str] = None
