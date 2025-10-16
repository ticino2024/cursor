# Troubleshooting Guide

## Common Issues and Solutions

### 1. Alembic Migration Errors

#### Error: "The asyncio extension requires an async driver to be used"

**Problem**: Alembic is trying to use async driver but psycopg2 is loaded.

**Solution**: This has been fixed in the code. The `alembic/env.py` now automatically converts async URLs to sync URLs for migrations.

If you still encounter this:
```bash
# Check your DATABASE_URL in .env
# For async app: postgresql+asyncpg://...
# Alembic will auto-convert to: postgresql://...
```

#### Error: "No such table: users"

**Problem**: Migrations haven't been run.

**Solution**:
```bash
# If using Docker
docker-compose exec api alembic upgrade head

# If running locally
alembic upgrade head
```

### 2. Database Connection Errors

#### Error: "Connection refused" or "Could not connect to server"

**Problem**: PostgreSQL is not running or not accessible.

**Solution**:
```bash
# Check if PostgreSQL container is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs userdb_postgres

# Restart PostgreSQL
docker-compose restart postgres

# Wait a bit longer for PostgreSQL to start
# The app waits 10 seconds, but you might need more
```

#### Error: "FATAL: database does not exist"

**Problem**: Database hasn't been created.

**Solution**:
```bash
# Recreate the database
docker-compose down -v  # Remove volumes
docker-compose up -d postgres
sleep 5
docker-compose up -d api
```

### 3. Redis Connection Errors

#### Error: "Error connecting to Redis"

**Problem**: Redis is not running or not accessible.

**Solution**:
```bash
# Check if Redis is running
docker ps | grep redis

# Check Redis logs
docker logs userdb_redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# Restart Redis
docker-compose restart redis
```

### 4. Secret Key Warnings

#### Warning: "SECRET_KEY is using default value"

**Problem**: Using default SECRET_KEY (not secure for production).

**Solution**:
```bash
# Generate a new secret key
python scripts/generate_secret.py
# or
openssl rand -hex 32

# Update .env file with the new key
# SECRET_KEY=<your-generated-key>

# Restart the application
docker-compose restart api
```

### 5. Port Conflicts

#### Error: "Port already in use"

**Problem**: Another service is using the required port.

**Solution**:
```bash
# Find what's using the port
lsof -i :8000  # For API
lsof -i :5432  # For PostgreSQL
lsof -i :6379  # For Redis

# Stop the conflicting service or change ports in docker-compose.yml
# For example, change "8000:8000" to "8001:8000"
```

### 6. Docker Issues

#### Error: "Cannot connect to Docker daemon"

**Problem**: Docker is not running.

**Solution**:
```bash
# Start Docker
sudo systemctl start docker  # Linux
# or start Docker Desktop (Mac/Windows)

# Check Docker status
docker ps
```

#### Error: "No space left on device"

**Problem**: Docker has run out of disk space.

**Solution**:
```bash
# Clean up Docker
docker system prune -a --volumes

# Remove specific containers and volumes
docker-compose down -v
```

### 7. Import Errors

#### Error: "ModuleNotFoundError: No module named 'app'"

**Problem**: Python can't find the app module.

**Solution**:
```bash
# Make sure you're in the project root
cd /workspace

# If using virtual environment, activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run from project root
python -m app.main
# or
uvicorn app.main:app --reload
```

### 8. Test Failures

#### Error: Tests failing with "connection refused"

**Problem**: Test database is not configured properly.

**Solution**:
```bash
# Tests use SQLite by default
# Make sure the test.db is writable
chmod 666 test.db 2>/dev/null || true

# Run tests with verbose output
pytest -v

# Clean test database and rerun
rm -f test.db
pytest
```

### 9. Authentication Issues

#### Error: "Invalid authentication credentials"

**Problem**: Token is invalid or expired.

**Solution**:
```bash
# Login again to get a new token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "User123!@#"}'

# Use the new access_token in your requests
```

#### Error: "Token has expired"

**Problem**: Access token has expired (default: 30 minutes).

**Solution**:
```bash
# Use the refresh token to get a new access token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

### 10. Permission Errors

#### Error: "Insufficient permissions"

**Problem**: User doesn't have required role.

**Solution**:
```bash
# Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "Admin123!@#"}'

# Or update user role (as admin)
curl -X PUT http://localhost:8000/api/v1/users/{user_id} \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```

### 11. Rate Limiting

#### Error: "Rate limit exceeded"

**Problem**: Too many requests from the same IP.

**Solution**:
```bash
# Wait for the rate limit window to reset (default: 1 minute)
# Or disable rate limiting in .env
RATE_LIMIT_ENABLED=false

# Restart the application
docker-compose restart api
```

### 12. CORS Errors

#### Error: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Problem**: Frontend origin is not allowed.

**Solution**:
```bash
# Update ALLOWED_ORIGINS in .env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,https://yourdomain.com

# Restart the application
docker-compose restart api
```

## Debugging Tips

### View Application Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 api
```

### Access Database

```bash
# PostgreSQL
docker-compose exec postgres psql -U user -d userdb

# List tables
\dt

# Query users
SELECT * FROM users;

# Exit
\q
```

### Access Redis CLI

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# List all keys
KEYS *

# Get a specific key
GET rate_limit:127.0.0.1

# Exit
exit
```

### Check Service Health

```bash
# API health check
curl http://localhost:8000/api/v1/health

# PostgreSQL
docker-compose exec postgres pg_isready -U user

# Redis
docker-compose exec redis redis-cli ping
```

### Reset Everything

```bash
# Complete reset (WARNING: This deletes all data!)
docker-compose down -v
rm -f test.db
docker-compose up -d
sleep 10
make init-db  # Optional: Create sample users
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs**: `docker-compose logs -f`
2. **Verify configuration**: Check `.env` file
3. **Review documentation**: README.md, QUICKSTART.md
4. **Run health checks**: Test each service individually
5. **Search issues**: Check if others have had similar problems
6. **Create an issue**: Provide logs and configuration details

## Common Commands Quick Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart api

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Create migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Run tests
docker-compose exec api pytest

# Access database
docker-compose exec postgres psql -U user -d userdb

# Access Redis
docker-compose exec redis redis-cli

# Check service status
docker-compose ps

# Rebuild containers
docker-compose up -d --build
```
