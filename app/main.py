# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import engine, get_db, Base
from .models import Todo
from .schemas import TodoCreate, TodoUpdate, TodoResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    앱 생명주기 관리
    Django의 migrate와 유사하게 시작 시 테이블 생성
    """
    print("🚀 데이터베이스 초기화 중...")
    
    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ 테이블 생성 완료")
    
    yield  # 앱 실행
    
    # 종료 시 정리
    print("👋 데이터베이스 연결 종료")
    await engine.dispose()

# FastAPI 앱 생성
app = FastAPI(
    title="Todo API",
    description="SQLAlchemy 2.0을 사용한 Todo API",
    lifespan=lifespan  # ← lifespan 등록
)

@app.get("/")
async def root():
    return {"message": "Todo API with SQLAlchemy 2.0"}