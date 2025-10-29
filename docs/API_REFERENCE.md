# Todo API Reference

## Overview
FastAPI-based REST API for managing todos with SQLAlchemy 2.0 async support.

**Base URL**: `http://localhost:8000`
**Database**: SQLite with aiosqlite async driver

---

## Endpoints

### Root Endpoint

#### `GET /`
Health check endpoint.

**Response**
```json
{
  "message": "Todo API with SQLAlchemy 2.0"
}
```

---

### Todo Operations

#### `GET /todos`
List all todos with pagination.

**Query Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Number of records to skip |
| `limit` | int | 20 | Maximum records to return |

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Learn FastAPI",
    "description": "Study async patterns",
    "completed": false,
    "created_at": "2025-10-29T10:30:00",
    "updated_at": "2025-10-29T10:30:00"
  }
]
```

**Example Request**
```bash
curl http://localhost:8000/todos?skip=0&limit=10
```

---

#### `GET /todos/{todo_id}`
Retrieve a specific todo by ID.

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `todo_id` | int | Todo ID |

**Response** `200 OK`
```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Study async patterns",
  "completed": false,
  "created_at": "2025-10-29T10:30:00",
  "updated_at": "2025-10-29T10:30:00"
}
```

**Error Response** `404 Not Found`
```json
{
  "detail": "Todo with id 999 not found"
}
```

**Example Request**
```bash
curl http://localhost:8000/todos/1
```

---

#### `POST /todos`
Create a new todo.

**Request Body**
```json
{
  "title": "Learn FastAPI",
  "description": "Study async patterns",
  "completed": false
}
```

**Field Requirements**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | Yes | - | Todo title (max 200 chars) |
| `description` | string | No | null | Todo description |
| `completed` | boolean | No | false | Completion status |

**Response** `201 Created`
```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Study async patterns",
  "completed": false,
  "created_at": "2025-10-29T10:30:00",
  "updated_at": "2025-10-29T10:30:00"
}
```

**Example Request**
```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Study async patterns"}'
```

---

#### `PUT /todos/{todo_id}`
Update an existing todo (partial update supported).

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `todo_id` | int | Todo ID |

**Request Body**
```json
{
  "title": "Learn FastAPI Advanced",
  "completed": true
}
```

**Field Requirements**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | No | Updated title |
| `description` | string | No | Updated description |
| `completed` | boolean | No | Updated status |

**Response** `200 OK`
```json
{
  "id": 1,
  "title": "Learn FastAPI Advanced",
  "description": "Study async patterns",
  "completed": true,
  "created_at": "2025-10-29T10:30:00",
  "updated_at": "2025-10-29T11:45:00"
}
```

**Error Response** `404 Not Found`
```json
{
  "detail": "Todo not found"
}
```

**Example Request**
```bash
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

---

#### `DELETE /todos/{todo_id}`
Delete a todo.

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `todo_id` | int | Todo ID |

**Response** `204 No Content`
No response body.

**Error Response** `404 Not Found`
```json
{
  "detail": "Todo not found"
}
```

**Example Request**
```bash
curl -X DELETE http://localhost:8000/todos/1
```

---

## Data Models

### Todo Schema

**TodoCreate** (Request body for creating todos)
```python
{
  "title": str,           # Required, max 200 chars
  "description": str,     # Optional
  "completed": bool       # Optional, default: false
}
```

**TodoUpdate** (Request body for updating todos)
```python
{
  "title": str,           # Optional
  "description": str,     # Optional
  "completed": bool       # Optional
}
```

**TodoResponse** (Response schema for all read operations)
```python
{
  "id": int,              # Auto-generated
  "title": str,
  "description": str,
  "completed": bool,
  "created_at": datetime, # Auto-generated
  "updated_at": datetime  # Auto-updated
}
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Error description"
}
```

### HTTP Status Codes
| Code | Meaning | When Used |
|------|---------|-----------|
| `200` | OK | Successful GET/PUT operations |
| `201` | Created | Successful POST operations |
| `204` | No Content | Successful DELETE operations |
| `404` | Not Found | Todo with specified ID doesn't exist |
| `422` | Unprocessable Entity | Invalid request body validation |

---

## Database Schema

### `todos` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-increment ID |
| `title` | VARCHAR(200) | NOT NULL | Todo title |
| `description` | TEXT | NULLABLE | Todo description |
| `completed` | BOOLEAN | DEFAULT false | Completion status |
| `created_at` | DATETIME | DEFAULT now() | Creation timestamp |
| `updated_at` | DATETIME | DEFAULT now(), ON UPDATE now() | Last update timestamp |

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all available endpoints
- View request/response schemas
- Test API calls directly from the browser
- Download OpenAPI specification
