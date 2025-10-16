# User Management API

A comprehensive user management system with authentication, authorization, and user profile management capabilities built with FastAPI, PostgreSQL, Redis, and JWT.

## 🚀 Features

### Core Features
- **User Authentication**: Register, login, password reset, token refresh
- **User Management**: CRUD operations, search, soft delete
- **User Profiles**: View and update profile, avatar upload
- **Role-Based Access Control**: Admin, user, and moderator roles
- **JWT Authentication**: Secure token-based authentication
- **Redis Caching**: Fast data access and rate limiting
- **PostgreSQL Database**: Robust data storage with async operations

### Technical Features
- **RESTful API**: Following REST conventions
- **API Versioning**: URL-based versioning (`/api/v1/`)
- **OpenAPI Documentation**: Auto-generated Swagger/Redoc docs
- **Input Validation**: Comprehensive validation using Pydantic
- **Error Handling**: Consistent error responses
- **Security Headers**: CORS, HSTS, CSP, XSS protection
- **Rate Limiting**: Redis-based request throttling
- **Database Migrations**: Alembic for schema versioning
- **Comprehensive Tests**: High test coverage with pytest
- **Docker Support**: Easy deployment with Docker Compose

## 📋 Requirements

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd workspace
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

### Manual Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd workspace
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start PostgreSQL and Redis**
   ```bash
   # Using Docker
   docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePass123!@#"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!@#"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Forgot Password
```http
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Reset Password
```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass123!@#"
}
```

### User Management Endpoints

#### List Users (Admin/Moderator Only)
```http
GET /api/v1/users?page=1&size=10
Authorization: Bearer <access_token>
```

#### Search Users (Admin/Moderator Only)
```http
GET /api/v1/users/search?query=john&role=user&is_active=true
Authorization: Bearer <access_token>
```

#### Get User by ID
```http
GET /api/v1/users/{user_id}
Authorization: Bearer <access_token>
```

#### Update User
```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "email": "newemail@example.com"
}
```

#### Delete User (Admin Only)
```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <access_token>
```

### Profile Endpoints

#### Get Current Profile
```http
GET /api/v1/profile
Authorization: Bearer <access_token>
```

#### Update Profile
```http
PUT /api/v1/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "email": "newemail@example.com"
}
```

#### Upload Avatar
```http
POST /api/v1/profile/avatar
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <image-file>
```

### Health Check

#### Health Status
```http
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## 🏗️ Project Structure

```
workspace/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py            # Shared dependencies
│   │   └── routes/
│   │       └── v1/            # API version 1
│   │           ├── __init__.py
│   │           ├── health.py  # Health check endpoints
│   │           ├── auth.py    # Authentication endpoints
│   │           ├── users.py   # User management endpoints
│   │           └── profile.py # Profile endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration
│   │   └── security.py        # Security utilities
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py            # Database base
│   │   ├── session.py         # Database session
│   │   └── models/
│   │       ├── __init__.py
│   │       └── user.py        # User model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py          # Common schemas
│   │   └── user.py            # User schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py    # User service
│   └── utils/
│       ├── __init__.py
│       └── redis_client.py    # Redis client
├── alembic/
│   ├── versions/              # Database migrations
│   ├── env.py                 # Alembic environment
│   └── script.py.mako         # Migration template
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test configuration
│   ├── test_auth.py           # Auth tests
│   ├── test_users.py          # User tests
│   ├── test_profile.py        # Profile tests
│   └── test_health.py         # Health tests
├── .env.example               # Environment variables template
├── .gitignore
├── alembic.ini                # Alembic configuration
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker image definition
├── pytest.ini                 # Pytest configuration
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run with verbose output
```bash
pytest -v
```

## 🗄️ Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

### Show current revision
```bash
alembic current
```

### Show migration history
```bash
alembic history
```

## 🔒 Security

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### Security Features
- JWT token-based authentication
- Bcrypt password hashing
- Rate limiting (60 requests per minute)
- CORS protection
- Security headers (XSS, HSTS, etc.)
- Input validation and sanitization
- Soft deletes for user data
- Role-based access control

## 🌍 Environment Variables

See `.env.example` for all available environment variables:

### Required Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (generate with `openssl rand -hex 32`)

### Optional Variables
- `REDIS_URL`: Redis connection string
- `ALLOWED_ORIGINS`: CORS allowed origins
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `SMTP_*`: Email configuration for password reset
- `LOG_LEVEL`: Logging level

## 🚀 Deployment

### Production Considerations

1. **Use strong secrets**
   ```bash
   # Generate a secure secret key
   openssl rand -hex 32
   ```

2. **Set environment to production**
   ```env
   ENV=production
   DEBUG=False
   ```

3. **Use HTTPS**
   - Configure SSL/TLS certificates
   - Enable HSTS headers

4. **Database**
   - Use connection pooling
   - Regular backups
   - Enable SSL connections

5. **Monitoring**
   - Set up logging
   - Monitor API performance
   - Track error rates

6. **Scaling**
   - Use load balancer
   - Increase worker count
   - Scale horizontally

### Docker Production Deployment

```bash
# Build production image
docker build -t user-management-api:latest .

# Run with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📖 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Support

For support, please open an issue in the repository or contact the maintainers.

## 🎯 Roadmap

- [ ] Email verification
- [ ] Two-factor authentication
- [ ] OAuth2 integration
- [ ] WebSocket support
- [ ] Admin dashboard
- [ ] Audit logging
- [ ] Export user data
- [ ] Advanced search filters
- [ ] User groups/organizations
- [ ] API rate limit customization per user

## ✨ Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for powerful ORM
- Pydantic for data validation
- Alembic for database migrations
