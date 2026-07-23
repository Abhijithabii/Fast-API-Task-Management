from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum



class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskBase(BaseModel):
    title : str = Field(..., min_length=1, max_length=200)
    description :Optional[str] = None
    completed : bool = False
    priority : PriorityLevel = PriorityLevel.MEDIUM
    due_date : Optional[datetime] = None
    category : Optional[str] = Field(None, max_length=50)


class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title : Optional[str] = Field(None, min_length=1, max_length=200)
    description : Optional[str] = None
    completed : Optional[bool] = None
    priority : Optional[PriorityLevel] = None
    due_date : Optional[datetime] = None
    category : Optional[str] = Field(None, max_length=50)


class Task(TaskBase):
    id : int
    created_at : datetime
    updated_at : Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class TaskListResponse(BaseModel):
    tasks : list[Task]
    total : int
    page : int
    pages : int
    limit : int
    
