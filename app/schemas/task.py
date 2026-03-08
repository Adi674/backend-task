from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    task_id: UUID                           
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v

    
    def get_update_fields(self) -> dict:
        return {
            key: value
            for key, value in {
                "title": self.title,
                "description": self.description,
                "status": self.status
            }.items()
            if value is not None      
        }


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskDelete(BaseModel):
    task_id: UUID