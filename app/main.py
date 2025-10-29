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

@app.get("/todos", response_model=list[TodoResponse])
async def list_todos(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    할일 목록 조회
    
    Django와의 차이:
    - select() 문으로 명시적 쿼리 작성
    - execute() → scalars() → all() 3단계 과정
    """
    # 1. 쿼리 작성 (아직 실행 안 됨), statement
    stmt = (
        select(Todo)
        .order_by(Todo.created_at.desc())  # Django의 order_by('-created_at')
        .offset(skip)  # Django의 [skip:]
        .limit(limit)  # Django의 [:limit]
    )
    
    # 2. 쿼리 실행
    result = await db.execute(stmt)
    
    # 3. 결과 추출
    todos = result.scalars().all()
    
    return todos

@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 할일 조회
    
    Django와의 차이:
    - .get() 대신 select() + where()
    - 명시적 404 처리
    """
    # 쿼리 작성
    stmt = select(Todo).where(Todo.id == todo_id)
    result = await db.execute(stmt)
    todo = result.scalar_one_or_none()
    
    # 404 처리
    if todo is None:
        raise HTTPException(
            status_code=404,
            detail=f"Todo with id {todo_id} not found"
        )
    
    return todo

@app.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(
    todo_data: TodoCreate,
    db: AsyncSession = Depends(get_db)  # Django의 request와 유사
):
    """
    할일 생성
    
    Django와의 차이:
    - 명시적 세션 관리
    - add → commit → refresh 3단계
    """
    # 1. 모델 인스턴스 생성 (Django와 동일)
    todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        completed=todo_data.completed,
    )
    
    # 2. 세션에 추가 (Django의 save() 전 상태)
    db.add(todo)
    # 이 시점에는 아직 DB에 저장 안 됨!
    # Django는 .save() 호출 시 즉시 저장
    
    # 3. 커밋 (실제 DB에 저장)
    await db.commit()
    # Django: todo.save()와 동일한 효과
    
    # 4. 리프레시 (DB에서 생성된 값 가져오기)
    await db.refresh(todo)
    # id, created_at 같은 DB 생성 값을 가져옴
    
    return todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    할일 수정
    
    Django와의 차이:
    - 명시적 commit 필요
    - exclude_unset으로 부분 업데이트
    """
    # 1. 기존 데이터 조회
    stmt = select(Todo).where(Todo.id == todo_id)
    result = await db.execute(stmt)
    todo = result.scalar_one_or_none()
    
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # 2. 데이터 업데이트
    update_data = todo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    # 3. 커밋 (Django의 .save())
    await db.commit()
    await db.refresh(todo)
    
    return todo

@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    할일 삭제
    
    Django와의 차이:
    - session.delete() + commit
    - 204 No Content 상태 코드
    """
    # 조회
    stmt = select(Todo).where(Todo.id == todo_id)
    result = await db.execute(stmt)
    todo = result.scalar_one_or_none()
    
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # 삭제
    await db.delete(todo)
    await db.commit()
    
    # 204는 응답 본문 없음
    return None