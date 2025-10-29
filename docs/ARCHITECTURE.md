# Architecture Documentation

## System Overview

The Todo API is built with a modern async Python stack using FastAPI and SQLAlchemy 2.0. The architecture follows a layered design pattern with clear separation of concerns.

```
┌─────────────────────────────────────────────────────┐
│                  Client Layer                        │
│   (HTTP Requests: curl, browser, Python client)     │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│              FastAPI Application                     │
│  ┌───────────────────────────────────────────────┐  │
│  │     Endpoint Handlers (app/main.py)           │  │
│  │  - Route definitions                          │  │
│  │  - Request/response handling                  │  │
│  │  - HTTP status codes                          │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│            Validation Layer                          │
│  ┌───────────────────────────────────────────────┐  │
│  │      Pydantic Schemas (app/schemas.py)        │  │
│  │  - TodoCreate: Input validation               │  │
│  │  - TodoUpdate: Partial update validation      │  │
│  │  - TodoResponse: Output serialization         │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│             Data Access Layer                        │
│  ┌───────────────────────────────────────────────┐  │
│  │    Database Session (app/database.py)         │  │
│  │  - Async session management                   │  │
│  │  - Connection pooling                         │  │
│  │  - Dependency injection                       │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │      ORM Models (app/models.py)               │  │
│  │  - Todo model definition                      │  │
│  │  - Table schema                               │  │
│  │  - Relationships                              │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│                Database Layer                        │
│              SQLite + aiosqlite                      │
│           (File: todos.db)                           │
└─────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Application Layer (`app/main.py`)

**Responsibilities**:
- FastAPI application initialization
- Route definitions and endpoint handlers
- Lifespan management (startup/shutdown)
- HTTP request/response handling
- Error handling and status codes

**Key Components**:

```python
# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Cleanup connections
    await engine.dispose()

# FastAPI app instance
app = FastAPI(
    title="Todo API",
    description="SQLAlchemy 2.0을 사용한 Todo API",
    lifespan=lifespan
)
```

**Endpoints**:
- `GET /` - Health check
- `GET /todos` - List todos with pagination
- `GET /todos/{id}` - Retrieve specific todo
- `POST /todos` - Create new todo
- `PUT /todos/{id}` - Update todo
- `DELETE /todos/{id}` - Delete todo

### 2. Validation Layer (`app/schemas.py`)

**Responsibilities**:
- Input validation using Pydantic
- Output serialization
- Type safety and data contracts
- API documentation generation

**Schema Hierarchy**:

```python
TodoCreate
├── Required: title
├── Optional: description, completed
└── Used for: POST /todos

TodoUpdate
├── Optional: title, description, completed
└── Used for: PUT /todos/{id}

TodoResponse
├── All fields from Todo model
├── from_attributes=True (ORM mode)
└── Used for: All GET endpoints
```

**Key Features**:
- Automatic type validation
- JSON schema generation
- ORM model conversion
- Partial updates support (`exclude_unset=True`)

### 3. Database Layer (`app/database.py`)

**Responsibilities**:
- Database engine configuration
- Session factory creation
- Connection lifecycle management
- Dependency injection provider

**Architecture**:

```python
# Async engine
engine = create_async_engine(
    "sqlite+aiosqlite:///./todos.db",
    echo=True  # SQL logging
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False  # Important for async
)

# Dependency injection
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

**Session Management**:
- Async context managers for automatic cleanup
- Connection pooling (SQLAlchemy default: 5-20 connections)
- Transaction management
- expire_on_commit=False prevents lazy loading issues

### 4. Model Layer (`app/models.py`)

**Responsibilities**:
- ORM model definitions
- Database table schema
- Column constraints and defaults
- Relationships (none in current version)

**Todo Model**:

```python
class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int]              # AUTO INCREMENT PRIMARY KEY
    title: Mapped[str]           # VARCHAR(200) NOT NULL
    description: Mapped[str|None] # TEXT NULL
    completed: Mapped[bool]      # BOOLEAN DEFAULT FALSE
    created_at: Mapped[datetime] # TIMESTAMP DEFAULT now()
    updated_at: Mapped[datetime] # TIMESTAMP DEFAULT now() ON UPDATE now()
```

**Type System**:
- `Mapped[type]`: SQLAlchemy 2.0 type hints
- `mapped_column()`: Column configuration
- `server_default`: Database-level defaults
- Automatic type inference from Python types

## Data Flow

### Create Todo Flow

```
1. Client sends POST /todos
   ↓
2. FastAPI receives request
   ↓
3. Pydantic validates against TodoCreate schema
   ↓
4. Endpoint handler creates Todo instance
   ↓
5. Session adds todo to transaction
   ↓
6. commit() persists to database
   ↓
7. refresh() loads generated values (id, timestamps)
   ↓
8. Pydantic serializes to TodoResponse
   ↓
9. FastAPI sends JSON response (201 Created)
```

### Query Todo Flow

```
1. Client sends GET /todos?skip=0&limit=20
   ↓
2. FastAPI parses query parameters
   ↓
3. Endpoint builds SQLAlchemy select statement
   stmt = select(Todo).order_by(...).offset(...).limit(...)
   ↓
4. Session executes query
   result = await db.execute(stmt)
   ↓
5. Extract results
   todos = result.scalars().all()
   ↓
6. Pydantic serializes list[Todo] to list[TodoResponse]
   ↓
7. FastAPI sends JSON response (200 OK)
```

### Update Todo Flow

```
1. Client sends PUT /todos/1
   ↓
2. Pydantic validates against TodoUpdate schema
   ↓
3. Query existing todo by ID
   ↓
4. If not found → 404 HTTPException
   ↓
5. Apply updates using model_dump(exclude_unset=True)
   ↓
6. commit() persists changes
   ↓
7. refresh() loads updated timestamps
   ↓
8. Pydantic serializes to TodoResponse
   ↓
9. FastAPI sends JSON response (200 OK)
```

## Async Architecture

### Why Async?

**Scalability**: Handle thousands of concurrent requests with minimal resource usage
**Efficiency**: Non-blocking I/O operations
**Performance**: Better throughput for I/O-bound operations

### Async Stack

```
FastAPI (async endpoints)
    ↓
SQLAlchemy 2.0 (AsyncSession, AsyncEngine)
    ↓
aiosqlite (async SQLite driver)
    ↓
SQLite database
```

### Async Patterns

**Endpoint Definition**:
```python
async def list_todos(db: AsyncSession = Depends(get_db)):
    # All operations use await
    result = await db.execute(stmt)
    return result.scalars().all()
```

**Database Operations**:
```python
# Execute queries
result = await db.execute(stmt)

# Commit transactions
await db.commit()

# Refresh objects
await db.refresh(todo)

# Delete objects
await db.delete(todo)
```

**Session Management**:
```python
async with AsyncSessionLocal() as session:
    # Session automatically closed on exit
    yield session
```

## Design Patterns

### 1. Dependency Injection

FastAPI's dependency injection system provides database sessions:

```python
@app.get("/todos")
async def list_todos(
    db: AsyncSession = Depends(get_db)  # Injected
):
    # Use db session
```

**Benefits**:
- Automatic session lifecycle management
- Testability (easy to mock)
- Clean separation of concerns

### 2. Repository Pattern (Implicit)

While not explicit, the code follows repository-like patterns:

```python
# Query construction
stmt = select(Todo).where(Todo.id == todo_id)

# Execution
result = await db.execute(stmt)

# Result extraction
todo = result.scalar_one_or_none()
```

### 3. DTO Pattern

Pydantic schemas act as Data Transfer Objects:

```
TodoCreate (Input DTO) → Todo (Domain Model) → TodoResponse (Output DTO)
```

### 4. Context Manager Pattern

Used extensively for resource management:

```python
# Lifespan management
async with AsyncSessionLocal() as session:
    yield session

# Database initialization
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

## Database Design

### Schema

```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    completed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

Currently no explicit indexes. Potential optimizations:

```sql
-- For completed status filtering
CREATE INDEX idx_todos_completed ON todos(completed);

-- For timestamp sorting
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
```

### Constraints

- **Primary Key**: `id` (auto-increment)
- **NOT NULL**: `title`
- **Defaults**: `completed=False`, `created_at=now()`, `updated_at=now()`

## Error Handling

### HTTP Exception Pattern

```python
if todo is None:
    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )
```

### Status Codes

| Code | Usage |
|------|-------|
| 200 | Successful GET/PUT |
| 201 | Successful POST |
| 204 | Successful DELETE (no body) |
| 404 | Resource not found |
| 422 | Validation error (automatic) |

### Validation Errors

Pydantic automatically handles validation:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Configuration Management

### Database Configuration

Located in `app/database.py`:

```python
DATABASE_URL = "sqlite+aiosqlite:///./todos.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL logging
)
```

### Application Configuration

Located in `app/main.py`:

```python
app = FastAPI(
    title="Todo API",
    description="SQLAlchemy 2.0을 사용한 Todo API",
    lifespan=lifespan
)
```

### Environment Variables (Future Enhancement)

Recommended pattern:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./todos.db"
    echo_sql: bool = True

    class Config:
        env_file = ".env"
```

## Testing Strategy

### Unit Testing Approach

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_todo():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/todos", json={
            "title": "Test",
            "description": "Testing"
        })
        assert response.status_code == 201
```

### Test Database

Use separate test database:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # ... yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

## Performance Considerations

### Current Limitations

1. **SQLite Concurrency**: SQLite doesn't handle high concurrent writes well
2. **No Caching**: Every request hits the database
3. **No Connection Pooling Tuning**: Using defaults

### Optimization Strategies

**For Production**:
1. Use PostgreSQL or MySQL for better concurrency
2. Add Redis caching layer
3. Implement pagination optimizations
4. Add database indexes for common queries
5. Enable connection pool tuning

**Example Connection Pool Config**:
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Max connections
    max_overflow=10,       # Additional connections
    pool_pre_ping=True,    # Verify connections
)
```

## Security Considerations

### Current State

- ✅ Input validation (Pydantic)
- ✅ Type safety
- ❌ No authentication
- ❌ No authorization
- ❌ No rate limiting
- ❌ No CORS configuration

### Production Requirements

1. **Authentication**: JWT tokens or OAuth2
2. **Authorization**: User ownership of todos
3. **Rate Limiting**: Prevent abuse
4. **CORS**: Configure allowed origins
5. **Input Sanitization**: Additional validation
6. **SQL Injection Protection**: SQLAlchemy handles this

**Example CORS Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Scalability Path

### Horizontal Scaling

1. Move to PostgreSQL for better concurrency
2. Add load balancer (nginx)
3. Run multiple FastAPI instances
4. Shared database with connection pooling

```
Client → Load Balancer → [FastAPI 1, FastAPI 2, FastAPI 3] → PostgreSQL
```

### Vertical Scaling

1. Increase database connection pool
2. Add caching layer (Redis)
3. Optimize queries with indexes
4. Enable database query caching

### Microservices Evolution

Future architecture could split into:
- **Auth Service**: User management
- **Todo Service**: Current functionality
- **Notification Service**: Email/push notifications
- **API Gateway**: Request routing

## Monitoring & Observability

### Recommended Additions

1. **Logging**: Structured logging with loguru
2. **Metrics**: Prometheus metrics
3. **Tracing**: OpenTelemetry for distributed tracing
4. **Health Checks**: `/health` endpoint

**Example Logging**:
```python
from loguru import logger

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

## Migration Strategy

### Database Migrations

Use Alembic for schema migrations:

```bash
# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head
```

### Deployment Strategy

1. **Blue-Green Deployment**: Zero downtime
2. **Rolling Updates**: Gradual instance replacement
3. **Canary Releases**: Test with small user percentage

## Future Enhancements

### Immediate (v1.1)
- [ ] Add authentication (JWT)
- [ ] Implement user ownership
- [ ] Add filtering and search
- [ ] Implement proper testing

### Short-term (v1.2-1.5)
- [ ] PostgreSQL migration
- [ ] Redis caching
- [ ] Rate limiting
- [ ] Docker containerization

### Long-term (v2.0+)
- [ ] Microservices architecture
- [ ] Event-driven architecture
- [ ] GraphQL API
- [ ] Real-time updates (WebSockets)

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Async Programming in Python](https://docs.python.org/3/library/asyncio.html)
