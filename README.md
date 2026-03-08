#  TaskFlow — Task Manager API

A production-ready **Task Management REST API** built with FastAPI, PostgreSQL, and JWT-based Role-Based Access Control (RBAC). Includes a fully functional Vanilla JS frontend.

---

##  Live Deployments

| | Link |
|---|---|
|  **Frontend** | [https://taskmanager2003.netlify.app](https://taskmanager2003.netlify.app) |
|  **Backend API** | [https://backend-task-2swq.onrender.com](https://backend-task-2swq.onrender.com) |
|  **Swagger Docs** | [https://backend-task-2swq.onrender.com/docs](https://backend-task-2swq.onrender.com/docs) |

---

##  Test Credentials

###  Admin Account
```
Email    : admin@primetrade.ai
Password : admin123
```
> Admin can **view, update, and delete all tasks** from all users across the system.

###  Test User Account
```
Email    : testuser@example.com
Password : test123
```
> Regular user can only **create and manage their own tasks**.

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT via `python-jose` + `bcrypt` |
| Validation | Pydantic v2 |
| Frontend | Vanilla JS, HTML, CSS |
| Backend Hosting | Render |
| Frontend Hosting | Netlify |
| DB Hosting | Supabase |

---

##  Project Structure

```
backend-task/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py          # Register, Login, /me
│   │       └── tasks.py         # Full task CRUD + admin routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic settings / env vars
│   │   ├── dependencies.py      # JWT auth dependencies
│   │   ├── exceptions.py        # Global error handlers
│   │   ├── response.py          # Standardised response helpers
│   │   └── security.py          # Hashing + JWT utils
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py              # SQLAlchemy DeclarativeBase
│   │   ├── registry.py          # Model registration (avoids circular imports)
│   │   └── session.py           # Engine + session factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py              # Task ORM model
│   │   └── user.py              # User ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── task.py              # Task request/response schemas
│   │   └── user.py              # User request/response schemas
│   └── main.py                  # FastAPI app, CORS, routers
├── frontend/
│   └── index.html               # Single-file Vanilla JS frontend
├── .env                         # Local environment variables (gitignored)
├── .gitignore
├── build.sh                     # Render build script
├── render.yaml                  # Render deployment config
├── requirements.txt
├── runtime.txt
└── README.md
```

---

##  Local Setup

### Prerequisites
- Python 3.12+
- PostgreSQL database (local or Supabase)

### 1. Clone the repo
```bash
git clone https://github.com/Adi674/backend-task.git
cd backend-task
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file in the root directory
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

### 6. Open in browser
```
API:   http://localhost:8000
Docs:  http://localhost:8000/docs
```

---

##  Database Schema

### SQL Setup (run once in Supabase / psql)

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE userrole   AS ENUM ('user', 'admin');
CREATE TYPE taskstatus AS ENUM ('todo', 'in_progress', 'done');

CREATE TABLE users (
    id              UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role            userrole     NOT NULL DEFAULT 'user',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE tasks (
    id          UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    status      taskstatus   NOT NULL DEFAULT 'todo',
    owner_id    UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Auto-update updated_at on row change
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Create Admin Account (SQL only — admins cannot self-register via API)
```sql
INSERT INTO users (id, email, hashed_password, role, created_at)
VALUES (
  uuid_generate_v4(),
  'admin@primetrade.ai',
  '<bcrypt_hashed_password>',
  'admin',
  NOW()
);
```

---

##  API Reference

### Auth Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Register new user (role always `user`) |
| `POST` | `/api/v1/auth/login` | Public | Login — returns JWT + role |
| `GET` | `/api/v1/auth/me` | 🔒 Required | Get current user profile |

### Task Endpoints — User

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/tasks/` | 🔒 Required | Create a new task |
| `GET` | `/api/v1/tasks/` | 🔒 Required | Get all own tasks |
| `GET` | `/api/v1/tasks/single?task_id=` | 🔒 Required | Get single task by ID |
| `PUT` | `/api/v1/tasks/` | 🔒 Required | Update own task (task_id in body) |
| `DELETE` | `/api/v1/tasks/` | 🔒 Required | Delete own task (task_id in body) |

### Task Endpoints — Admin Only

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/tasks/admin/all` |  Admin | Get all tasks from all users |
| `PUT` | `/api/v1/tasks/admin` |  Admin | Update any task |
| `DELETE` | `/api/v1/tasks/admin` |  Admin | Delete any task |

---

##  Standard Response Format

Every endpoint returns a consistent JSON envelope:

```json
{
  "status": "success",
  "message": "Task created successfully",
  "data": { ... }
}
```

```json
{
  "status": "error",
  "message": "Task not found",
  "errors": null
}
```

---

## 🔑 Authentication

### Flow
1. Call `/api/v1/auth/login` with email + password
2. Receive a **JWT Bearer token** in the response
3. Pass the token in the `Authorization` header on all protected requests

```bash
# Step 1 — Login and get token
curl -X POST https://backend-task-2swq.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser@example.com", "password": "test123"}'

# Step 2 — Use token on protected routes
curl -X GET https://backend-task-2swq.onrender.com/api/v1/tasks/ \
  -H "Authorization: Bearer <your_token_here>"
```

### JWT Payload structure
```json
{
  "sub":   "user-uuid",
  "role":  "user",
  "email": "user@example.com",
  "exp":   1234567890,
  "iat":   1234567890,
  "type":  "access"
}
```

---

## 🔒 Security Design

| Concern | Approach |
|---|---|
| Password storage | bcrypt hashing — never stored in plain text |
| Token expiry | JWT expires in 30 minutes |
| Role assignment | Hardcoded to `user` on register — never accepted from request body |
| Admin creation | Direct DB insert only — cannot be created via API |
| Error messages | Generic `"Invalid email or password"` — prevents email enumeration |
| Input validation | Pydantic v2 schemas on all endpoints |
| CORS | Restricted to specific allowed origins only |
| Error leakage | Global exception handlers — raw stack traces never exposed to clients |

---

##  Scalability

### Design decisions that support scale

**API Versioning** — all routes sit under `/api/v1/`. Breaking changes go to `/api/v2/` without disrupting existing clients.

**Stateless JWT Auth** — no server-side sessions. The backend can be horizontally scaled across multiple instances behind a load balancer with zero coordination needed between them.

**Modular folder structure** — each domain (auth, tasks) is fully isolated. Adding new features like `projects` or `comments` only requires a new module without touching existing code.

**Pydantic v2 schemas** — request and response shapes are strictly typed and validated before reaching business logic, preventing malformed data from entering the database.

**SQLAlchemy ORM + Alembic** — schema migrations are version-controlled, making database changes safe to roll out incrementally in production without downtime.

### Growth path

```
Now          →  Single instance on Render (free tier)
Next step    →  Redis cache for GET /tasks/ reads + token blacklisting on logout
Scaling up   →  Docker + multiple horizontal replicas behind a load balancer
Microservice →  Split into auth-service and task-service with API gateway in front
Cloud-ready  →  AWS ECS / GCP Cloud Run / Kubernetes with auto-scaling
```

---

##  Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | — |
| `SECRET_KEY` | Secret used to sign JWT tokens | — |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL in minutes | `30` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:8000` |

---

## 👨‍💻 Author

**Aditya Kumar Srivastav**
GitHub: [@Adi674](https://github.com/Adi674)
