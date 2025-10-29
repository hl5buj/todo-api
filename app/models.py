# app/models.py
from datetime import datetime
from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Todo(Base):
    """
    할일 모델
    
    Django와의 차이:
    - Mapped[타입]: 타입 힌팅으로 IDE 지원 강화
    - mapped_column(): 컨럼 세부 옵션 설정
    - __tablename__: 테이블 이름 명시적 지정
    """
    __tablename__ = "todos"
    
    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 길이 제한 (Django의 max_length)
    title: Mapped[str] = mapped_column(String(200))
    
    # 긴 텍스트 (Django의 TextField), NULL 허용
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # 불린 필드 (Django의 BooleanField)
    completed: Mapped[bool] = mapped_column(default=False)
    
    # 생성/수정 시각 (server_default: DB 레벨에서 기본값 설정)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<Todo(id={self.id}, title='{self.title}', completed={self.completed})>"