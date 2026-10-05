from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class NoteCreate(BaseModel):
    standard: int = Field(..., ge=1, le=10)
    subject: str = Field(..., min_length=2, max_length=100)
    title: str = Field(..., min_length=2, max_length=200)
    content: str = Field("", max_length=10000)
    teacher: Optional[str] = "Class Teacher"
    date: Optional[str] = "Today"

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    content: Optional[str] = Field(None, min_length=5)
    subject: Optional[str] = Field(None, min_length=2, max_length=100)
    standard: Optional[int] = Field(None, ge=1, le=10)

class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    standard: int
    subject: str
    title: str
    content: str
    teacher: str
    date: str
    created_at: datetime
    pdf_url: Optional[str] = None

class NoteListResponse(BaseModel):
    total: int
    notes: list[NoteResponse]
