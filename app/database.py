# app/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# SQLite 데이터베이스 URL
DATABASE_URL = "sqlite+aiosqlite:///./todos.db"

# 비동기 엔진 생성
# echo=True: 실행되는 SQL 쿼리를 콘솔에 출력 (학습용)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL 로그 출력
)

# 세션 팩토리 생성
# expire_on_commit=False: 커밋 후에도 객체 속성 접근 가능 (비동기 필수)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 모델 베이스 클래스
class Base(DeclarativeBase):
    """모든 모델이 상속받을 베이스 클래스"""
    pass

# 의존성 주입용 함수
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 의존성 주입으로 세션 제공
    
    Django와의 차이:
    - Django: 자동으로 각 요청마다 DB 연결 관리
    - FastAPI: 명시적으로 의존성 주입 패턴 사용
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()