# SpecMatrix

SpecMatrix is a specification-driven test validation system for embedded software and hardware projects.

It focuses on managing whether a test design is sufficient, not only storing test cases.

Documents:

- [Product specification draft](docs/specification.md)
- [Architecture decision draft](docs/architecture.md)

## Development

SpecMatrix uses the first-choice stack from the architecture draft:

- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Docker Compose

Start the development environment:

```bash
docker compose up --build
```

Run database migrations:

```bash
docker compose exec web python manage.py migrate
```

Open the app:

- Django: http://localhost:8000/
- Health check: http://localhost:8000/healthz/
- Admin: http://localhost:8000/admin/

Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

## VS Code Dev Container

Open the repository in VS Code and run:

```text
Dev Containers: Reopen in Container
```

The Dev Container uses `docker-compose.yml`, attaches to the `web` service, and starts PostgreSQL and Redis alongside Django.
