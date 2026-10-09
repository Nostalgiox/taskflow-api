# TaskFlow API

A REST API for managing teams, projects and tasks — built with Django REST Framework, PostgreSQL and JWT authentication.

[![CI](https://github.com/Nostalgiox/taskflow-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Nostalgiox/taskflow-api/actions/workflows/ci.yml)
![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)

## Tech Stack

- **Backend:** Django 5.1, Django REST Framework
- **Auth:** JWT (djangorestframework-simplejwt)
- **Database:** PostgreSQL 16
- **Docs:** drf-spectacular (OpenAPI 3, Swagger UI)
- **Tests:** pytest, pytest-django, factory_boy (~97% coverage)
- **Container:** Docker, Docker Compose
- **Lint/format:** ruff

## Features

- ✅ JWT authentication (register, login, refresh, verify)
- ✅ Teams with role-based access (`owner` / `admin` / `member`)
- ✅ Projects belonging to teams
- ✅ Tasks with status, priority, assignee and due date
- ✅ Comments on tasks
- ✅ Filtering, search and ordering on list endpoints
- ✅ Object-level permissions (users only see their teams' data)
- ✅ OpenAPI 3 docs with Swagger UI
- ✅ Test suite with 97% coverage

## Architecture

```
Client → DRF View → Serializer → Model → PostgreSQL
              ↓
        Permission layer (team membership)
```

Key decisions:
- **Service layer** (`services.py`) — business logic separated from views
- **Object-level permissions** — each user sees only data from their teams
- **Custom User model** — email required, ready for extension
- **Docker Compose** — single command to run everything

## Getting Started

### Requirements

- Docker & Docker Compose

### Run

```bash
git clone https://github.com/Nostalgiox/taskflow-api.git
cd taskflow-api
cp .env.example .env
docker compose up --build
```

Then in a separate terminal:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open:
- **Swagger UI:** http://localhost:8000/api/docs/
- **Admin panel:** http://localhost:8000/admin/

## API Examples

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dawid",
    "email": "dawid@example.com",
    "password": "strongpass123",
    "password_confirm": "strongpass123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "dawid", "password": "strongpass123"}'
```

Response:
```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc..."
}
```

### Create a team

```bash
curl -X POST http://localhost:8000/api/teams/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Team", "description": "Test team"}'
```

### List tasks with filters

```bash
curl "http://localhost:8000/api/tasks/?status=todo&priority=high&assignee=me" \
  -H "Authorization: Bearer <access_token>"
```

## Testing

```bash
# Run all tests
docker compose exec web pytest

# With coverage
docker compose exec web pytest --cov=apps --cov-report=term-missing
```

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Login (returns JWT) |
| POST | `/api/auth/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Current user profile |
| GET/POST | `/api/teams/` | List / create teams |
| GET/PATCH/DELETE | `/api/teams/{id}/` | Team detail |
| POST | `/api/teams/{id}/members/` | Add member |
| DELETE | `/api/teams/{id}/members/{user_id}/` | Remove member |
| GET/POST | `/api/projects/` | List / create projects |
| GET/PATCH/DELETE | `/api/projects/{id}/` | Project detail |
| GET/POST | `/api/tasks/` | List / create tasks |
| GET/PATCH/DELETE | `/api/tasks/{id}/` | Task detail |
| GET/POST | `/api/tasks/{id}/comments/` | List / add comments |
| DELETE | `/api/comments/{id}/` | Delete comment |

## Environment Variables

See `.env.example`.

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DJANGO_DEBUG` | Debug mode (True/False) |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list |
| `POSTGRES_*` | Database credentials |
| `JWT_*` | JWT token lifetimes |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list |

## What I'd Improve

- Add background tasks with Celery (e.g. email notifications on task assignment)
- Add activity log for teams and projects
- Add file attachments to tasks
- Add WebSocket support for real-time updates
- Deploy with proper CI/CD pipeline (GitHub Actions → Railway)

## License

MIT