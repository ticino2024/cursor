# Quick Start Guide

This guide will help you get the User Management API up and running quickly.

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.9+, PostgreSQL, and Redis

## Option 1: Using Docker (Recommended)

### Step 1: Clone and Configure

```bash
# Navigate to the project directory
cd workspace

# Copy environment file
cp .env.example .env

# (Optional) Edit .env to customize settings
# nano .env
```

### Step 2: Generate Secret Key

```bash
# Generate a secure secret key
make generate-secret

# Copy the generated key to your .env file
# Edit .env and replace SECRET_KEY with the generated value
```

### Step 3: Start Services

```bash
# Start all services (PostgreSQL, Redis, API)
make docker-up

# Or use docker-compose directly
docker-compose up -d
```

### Step 4: Initialize Database (Optional)

```bash
# Create sample users (admin, user, moderator)
make init-db
```

### Step 5: Access the API

- **API Base URL**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Sample Credentials (if you ran init-db)

- **Admin**: admin@example.com / Admin123!@#
- **User**: user@example.com / User123!@#
- **Moderator**: moderator@example.com / Mod123!@#

## Option 2: Manual Setup

### Step 1: Set Up Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Generate secret key
python scripts/generate_secret.py

# Edit .env with your database and Redis URLs
```

### Step 3: Start PostgreSQL and Redis

```bash
# Using Docker for databases only
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=userdb \
  postgres:15

docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### Step 4: Run Migrations

```bash
# Apply database migrations
alembic upgrade head

# (Optional) Initialize with sample data
python scripts/init_db.py
```

### Step 5: Start the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or using make
make dev
```

## Testing Your Installation

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "Test123!@#"
  }'
```

### 3. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
```

Save the `access_token` from the response for authenticated requests.

### 4. Get Your Profile

```bash
curl http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Common Commands

```bash
# Start services
make docker-up

# Stop services
make docker-down

# View logs
make docker-logs

# Run tests
make test

# Run tests with coverage
make coverage

# Create a database migration
make migrate-create MSG="your migration description"

# Apply migrations
make migrate

# Generate a new secret key
make generate-secret

# Format code
make format

# Clean cache files
make clean
```

## Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

```bash
# Check what's using the port
lsof -i :8000  # or :5432, :6379

# Stop conflicting services or change ports in .env
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs userdb_postgres

# Test connection
docker exec -it userdb_postgres psql -U user -d userdb
```

### Redis Connection Error

```bash
# Check if Redis is running
docker ps | grep redis

# Test connection
docker exec -it userdb_redis redis-cli ping
```

### Migration Errors

```bash
# Check current migration status
alembic current

# View migration history
alembic history

# If stuck, you can downgrade and re-migrate
alembic downgrade -1
alembic upgrade head
```

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/api/docs to see all available endpoints
2. **Read the Documentation**: Check README.md for detailed information
3. **Run Tests**: Execute `make test` to verify everything works
4. **Customize**: Modify the code to fit your specific needs

## Production Deployment

Before deploying to production:

1. Set `ENV=production` in .env
2. Set `DEBUG=False`
3. Use a strong `SECRET_KEY` (never commit it!)
4. Configure proper CORS origins
5. Set up SSL/TLS certificates
6. Use a production-grade database
7. Set up monitoring and logging
8. Configure backup strategies

## Support

For issues or questions:
- Check the README.md
- Review the API documentation
- Open an issue on the repository

## License

MIT License - See LICENSE file for details
