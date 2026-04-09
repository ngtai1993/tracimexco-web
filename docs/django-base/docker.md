# Docker Setup — Chạy Dự Án Trên Docker Desktop

---

## 1. Tổng Quan Services

```
docker-compose.yml
│
├── web          → Django + Gunicorn (cổng 8000 → 80 qua nginx)
├── nginx        → Reverse proxy (cổng 80)
├── db           → PostgreSQL 16 (cổng 5432)
├── redis        → Redis 7 (cổng 6379)
├── celery       → Celery Worker (xử lý async tasks)
└── celery-beat  → Celery Beat (scheduled tasks)
```

> **Dev mode**: `web` chạy `runserver` với hot-reload — không cần `nginx` và `gunicorn`

---

## 2. File `docker-compose.yml` (Production-like)

```yaml
version: "3.9"

services:

  db:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn config.wsgi:application
               --bind 0.0.0.0:8000
               --workers 4
               --timeout 120"
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    expose:
      - "8000"

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    command: celery -A tasks.celery worker --loglevel=info --concurrency=4
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    command: celery -A tasks.celery beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - celery

  nginx:
    image: nginx:1.25-alpine
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - static_volume:/var/www/static:ro
      - media_volume:/var/www/media:ro
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

---

## 3. File `docker-compose.dev.yml` (Local Development)

```yaml
version: "3.9"

services:

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"           # Expose ra host để dùng DB client
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: devdb
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpassword

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"           # Expose ra host để debug

  web:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app        # Mount source code — hot reload
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
      - DATABASE_URL=postgres://devuser:devpassword@db:5432/devdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: celery -A tasks.celery worker --loglevel=debug --concurrency=2
    volumes:
      - ./backend:/app        # Hot reload cho task
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
      - DATABASE_URL=postgres://devuser:devpassword@db:5432/devdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data_dev:
```

---

## 4. `Dockerfile` (Production)

```dockerfile
FROM python:3.12-slim

# Tránh tạo file .pyc, log thẳng ra stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài OS dependencies (psycopg2 cần libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

COPY . .

# Tạo user không phải root — bảo mật
RUN adduser --disabled-password --gecos "" appuser
USER appuser
```

---

## 5. `Dockerfile.dev` (Development)

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/development.txt .
RUN pip install --no-cache-dir -r development.txt

# Không COPY code — được mount qua volume để hot reload
```

---

## 6. Nginx Config (`nginx/nginx.conf`)

```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name localhost;

    client_max_body_size 20M;

    location /static/ {
        alias /var/www/static/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 7. File `.env.example`

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=appdb
DB_USER=appuser
DB_PASSWORD=strongpassword

# Redis
REDIS_URL=redis://redis:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourapp.com

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# JWT
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## 8. Lệnh Thường Dùng

### Khởi Động Dev

```bash
# Lần đầu — build image
docker compose -f docker-compose.dev.yml up --build

# Lần sau
docker compose -f docker-compose.dev.yml up

# Chạy ngầm (background)
docker compose -f docker-compose.dev.yml up -d
```

### Django Management

```bash
# Migrate
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# Tạo migration
docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations

# Tạo superuser
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# Django shell
docker compose -f docker-compose.dev.yml exec web python manage.py shell_plus

# Chạy tests
docker compose -f docker-compose.dev.yml exec web pytest
```

### Logs & Debug

```bash
# Xem log web
docker compose -f docker-compose.dev.yml logs web -f

# Xem log celery
docker compose -f docker-compose.dev.yml logs celery -f

# Vào container
docker compose -f docker-compose.dev.yml exec web bash
```

### Dọn Dẹp

```bash
# Dừng containers
docker compose -f docker-compose.dev.yml down

# Dừng + xóa volumes (reset DB)
docker compose -f docker-compose.dev.yml down -v
```

---

## 9. Môi Trường Settings

### `config/settings/base.py` — Cấu trúc chính

```python
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

INSTALLED_APPS = [
    # Django built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'django_celery_beat',
    # Local apps
    'apps.users.apps.UsersConfig',
    'apps.authentication.apps.AuthenticationConfig',
    'apps.core.apps.CoreConfig',
]

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardResultsPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
}
```

---

## 10. Scale Trên Docker

| Cần Scale | Cách Làm |
|-----------|----------|
| Tăng Gunicorn workers | Sửa `--workers` trong command của `web` service |
| Tăng Celery concurrency | Sửa `--concurrency` hoặc chạy nhiều `celery` replicas |
| Nhiều DB connection | Thêm service `pgbouncer` trước `db` |
| Deploy nhiều instance `web` | `docker compose up --scale web=3` + cấu hình Nginx upstream roundrobin |
