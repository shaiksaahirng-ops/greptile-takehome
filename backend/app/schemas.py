from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChangesSchema(BaseModel):
    features: List[str] = []
    bugfixes: List[str] = []
    improvements: List[str] = []
    breaking: List[str] = []

class ChangelogCreate(BaseModel):
    version: str
    title: str
    summary: Optional[str] = None
    changes: ChangesSchema
    commit_range: Optional[str] = None
    project_name: str = "default"

class ChangelogUpdate(BaseModel):
    version: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    changes: Optional[ChangesSchema] = None
    published: Optional[bool] = None

class ChangelogResponse(BaseModel):
    id: int
    version: str
    title: str
    summary: Optional[str]
    changes: ChangesSchema
    commit_range: Optional[str]
    project_name: str
    created_at: datetime
    published: bool

    class Config:
        from_attributes = True
