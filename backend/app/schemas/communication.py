from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class AssignmentCreate(BaseModel):
    standard: int = Field(..., ge=1, le=10)
    subject: str = Field(..., min_length=2, max_length=100)
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=5)
    due_date: Optional[str] = "Next Week"

class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    standard: int
    subject: str
    title: str
    description: str
    due_date: Optional[str]
    created_at: datetime

class AnnouncementCreate(BaseModel):
    standard: int = Field(default=0, description="0 for school-wide, or standard number 1-10")
    title: str = Field(..., min_length=2, max_length=200)
    content: str = Field(..., min_length=5)

class AnnouncementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    standard: int
    title: str
    content: str
    author_name: str
    created_at: datetime
