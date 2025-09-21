from pydantic import BaseModel
from typing import Optional

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class TodoOut(TodoBase):
    id: int
    completed: bool

    class Config:
        from_attributes = True  # Changed from orm_mode = True