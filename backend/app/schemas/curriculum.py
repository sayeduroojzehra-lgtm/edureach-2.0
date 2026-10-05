from typing import Optional
from pydantic import BaseModel, ConfigDict

class LessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_id: int
    title: str
    topic: str
    content: str
    duration_minutes: int

class ChapterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    standard: int
    title: str
    subtitle: str
    order_index: int
    lessons: list[LessonResponse] = []

class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    min_standard: int
    max_standard: int
    icon_name: str
    color_code: str
