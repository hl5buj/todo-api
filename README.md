# Todo API

FastAPI-based REST API for managing todos with SQLAlchemy 2.0 async support and SQLite database.

## Features

- ✅ **Async/Await**: Full async support with SQLAlchemy 2.0 and aiosqlite
- 📝 **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- 🗄️ **SQLite Database**: Simple file-based database with async support
- 📚 **Auto Documentation**: Interactive Swagger UI and ReDoc
- 🔄 **Auto Migration**: Database tables created on startup
- 🎯 **Type Safety**: Full type hints with Pydantic validation

## Tech Stack

- **FastAPI**: Modern async web framework
- **SQLAlchemy 2.0**: Async ORM with type hints
- **Pydantic**: Data validation and serialization
- **SQLite + aiosqlite**: Lightweight async database
- **Python 3.12+**: Latest Python features

## Project Structure

```
todo-api/
├── app/
│   ├── __init__.py          # Package marker
│   ├── main.py              # FastAPI app & endpoints
│   ├── database.py          # Database config & session
│   ├── models.py            # SQLAlchemy models
│   └── schemas.py           # Pydantic schemas
├── docs/
│   └── API_REFERENCE.md     # API documentation
├── todos.db                 # SQLite database (auto-generated)
└── README.md                # This file
```

## Quick Start

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd todo-api
```

2. **Install dependencies**
```bash
pip install fastapi sqlalchemy aiosqlite
pip install "uvicorn[standard]"
```

### Running the Server

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## Usage Examples

### Using curl

**Create a todo**
```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Study async patterns"}'
```

**List todos**
```bash
curl http://localhost:8000/todos
```

**Get specific todo**
```bash
curl http://localhost:8000/todos/1
```

**Update todo**
```bash
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Delete todo**
```bash
curl -X DELETE http://localhost:8000/todos/1
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000"

# Create todo
response = requests.post(
    f"{base_url}/todos",
    json={"title": "Learn FastAPI", "description": "Study async patterns"}
)
print(response.json())

# List todos
response = requests.get(f"{base_url}/todos")
print(response.json())

# Update todo
response = requests.put(
    f"{base_url}/todos/1",
    json={"completed": True}
)
print(response.json())
```

### Using Interactive Docs

1. Open http://localhost:8000/docs in your browser
2. Click on any endpoint to expand
3. Click "Try it out"
4. Fill in parameters and request body
5. Click "Execute" to test the endpoint
6. View the response

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/todos` | List all todos (with pagination) |
| GET | `/todos/{id}` | Get specific todo |
| POST | `/todos` | Create new todo |
| PUT | `/todos/{id}` | Update todo |
| DELETE | `/todos/{id}` | Delete todo |

See [API_REFERENCE.md](docs/API_REFERENCE.md) for detailed documentation.

## Development

### Database Management

The database is automatically initialized on startup. The SQLite file `todos.db` is created in the project root.

**View SQL queries**: SQL logging is enabled by default (`echo=True` in database.py). Check console output to see executed queries.

**Reset database**: Simply delete `todos.db` and restart the server.

### Code Structure

**app/main.py**
- FastAPI application instance
- Endpoint definitions
- Lifespan management (startup/shutdown)

**app/database.py**
- Database engine configuration
- Session factory
- Dependency injection for database sessions

**app/models.py**
- SQLAlchemy ORM models
- Database table definitions

**app/schemas.py**
- Pydantic models for request/response validation
- Data serialization/deserialization

### Django vs FastAPI Patterns

This project includes inline comments comparing FastAPI patterns with Django:

```python
# Django: Todo.objects.filter(...).order_by('-created_at')[:20]
# FastAPI/SQLAlchemy:
stmt = select(Todo).order_by(Todo.created_at.desc()).limit(20)
result = await db.execute(stmt)
todos = result.scalars().all()
```

Key differences:
- **Explicit sessions**: FastAPI requires manual session management
- **Async all the way**: Use `async/await` throughout
- **3-step process**: select → execute → extract results
- **Pydantic validation**: Separate schemas for validation vs ORM models

## Configuration

### Database URL
Located in `app/database.py`:
```python
DATABASE_URL = "sqlite+aiosqlite:///./todos.db"
```

Change to use different database:
- **PostgreSQL**: `postgresql+asyncpg://user:pass@localhost/dbname`
- **MySQL**: `mysql+aiomysql://user:pass@localhost/dbname`

### Server Settings
```bash
# Custom host and port
uvicorn app.main:app --host 0.0.0.0 --port 8080

# Production mode (no auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testing

### Manual Testing with httpie

```bash
# Install httpie
pip install httpie

# Create todo
http POST :8000/todos title="Test" description="Testing API"

# List todos
http :8000/todos

# Update todo
http PUT :8000/todos/1 completed=true
```

### Testing with Python

```python
import asyncio
import httpx

async def test_api():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Create
        response = await client.post("/todos", json={
            "title": "Test todo",
            "description": "Testing"
        })
        assert response.status_code == 201

        # List
        response = await client.get("/todos")
        assert response.status_code == 200

        # Update
        response = await client.put("/todos/1", json={"completed": True})
        assert response.status_code == 200

asyncio.run(test_api())
```

## Troubleshooting

### Database locked error
SQLite doesn't handle high concurrency well. For production, use PostgreSQL or MySQL.

### Import errors
Ensure you're in the project root directory when running uvicorn:
```bash
cd todo-api
uvicorn app.main:app --reload
```

### Port already in use
Change the port:
```bash
uvicorn app.main:app --port 8080
```

## Next Steps

- [ ] Add authentication (JWT tokens)
- [ ] Add user management and todo ownership
- [ ] Implement filtering and search
- [ ] Add proper testing suite (pytest)
- [ ] Set up migrations (Alembic)
- [ ] Add Docker support
- [ ] Deploy to production

## Documentation

- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Official FastAPI documentation
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) - SQLAlchemy documentation

## License

MIT License - feel free to use for learning and projects.
