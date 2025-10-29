# app/schemas.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TodoCreate(BaseModel):
    """할일 생성 시 받는 데이터 (Django Form/Serializer와 유사)"""
    title: str
    description: str | None = None
    completed: bool = False

class TodoUpdate(BaseModel):
    """할일 수정 시 받는 데이터"""
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

class TodoResponse(BaseModel):
    """할일 응답 시 보내는 데이터 (Django Serializer와 유사)"""
    model_config = ConfigDict(from_attributes=True)  # ORM 모델 → Pydantic
    
    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime