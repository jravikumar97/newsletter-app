# Newsletter Curator API - Stage 1

A FastAPI-based application for curating and ranking newsletters based on user preferences and interaction behavior.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Git

### Installation & Setup

1. **Clone/Create the project directory:**
```bash
mkdir newsletter-app
cd newsletter-app
```

2. **Create the project structure using the setup commands provided**

3. **Start the application with Docker:**
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

4. **Verify the installation:**
```bash
# Run the test script
python test_api.py
```

## 📋 What's Included in Stage 1

### ✅ Core Infrastructure
- **FastAPI Application** with automatic API documentation
- **PostgreSQL Database** with SQLAlchemy ORM
- **Docker Configuration** for easy deployment
- **Database Migrations** with Alembic
- **Project Structure** following FastAPI best practices

### ✅ User Management
- User registration and profile management
- Password hashing and security
- CRUD operations for user data
- Comprehensive user schema validation

### ✅ API Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check with database connection test
- `GET /api/v1/` - API information
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/{id}` - Get user by ID
- `GET /api/v1/users/email/{email}` - Get user by email
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Deactivate user
- `GET /api/v1/users/` - List users

## 🔧 API Usage Examples

### Create a User
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
-H "Content-Type: application/json" \
-d '{
  "email": "john.doe@example.com",
  "name": "John Doe",
  "password": "securepassword123",
  "job_title": "Software Engineer",
  "industry": "Technology",
  "location_city": "New York",
  "location_country": "USA"
}'
```

### Get User Information
```bash
curl -X GET "http://localhost:8000/api/v1/users/1"
```

### Update User Profile
```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
-H "Content-Type: application/json" \
-d '{
  "job_title": "Senior Software Engineer",
  "location_city": "San Francisco"
}'
```

## 🗄️ Database Schema

### Users Table
- **Authentication**: email, hashed_password, is_active, is_verified
- **Personal Info**: name, phone, age, location_city, location_country, timezone
- **Professional**: job_title, industry, company_size, education_level, experience_level
- **Email Integration**: email_connected, email_connected_at
- **Timestamps**: created_at, updated_at, last_active_at

## 🐳 Docker Services

### Application (app)
- **Port**: 8000
- **Framework**: FastAPI with Uvicorn
- **Features**: Auto-reload in development mode

### Database (db)
- **Port**: 5432
- **Type**: PostgreSQL 15
- **Database**: newsletter_app
- **Credentials**: admin/password123

### Database Admin (pgadmin) - Optional
- **Port**: 5050
- **URL**: http://localhost:5050
- **Credentials**: admin@newsletter.com/admin123

## 📊 API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_api.py
```

The test script verifies:
- ✅ Health check endpoint
- ✅ Root and API info endpoints
- ✅ User creation, retrieval, and updates
- ✅ Database connectivity
- ✅ Error handling

## 🔍 Monitoring & Debugging

### Check Application Logs
```bash
docker-compose logs app
```

### Check Database Logs
```bash
docker-compose logs db
```

### Access Database Directly
```bash
docker-compose exec db psql -U admin -d newsletter_app
```

### Check Container Status
```bash
docker-compose ps
```

## 🚧 What's Next (Stage 2)

Stage 2 will add:
- **Authentication & JWT tokens**
- **User login/logout functionality**
- **Password reset capabilities**
- **User interest management**
- **Enhanced security features**

## 📁 Project Structure

```
newsletter-app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py             # API router
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       └── users.py        # User endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Settings
│   ├── crud/
│   │   ├── __init__.py
│   │   └── user.py             # User CRUD operations
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py             # Database models
│   └── schemas/
│       ├── __init__.py
│       └── user.py             # Pydantic schemas
├── gmail_extractor.py          # Your existing Gmail extractor
├── test_api.py                 # API test script
├── docker-compose.yml          # Docker services
├── Dockerfile                  # App container
├── requirements.txt            # Python dependencies
├── alembic.ini                 # Database migrations config
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🔧 Environment Variables

Key environment variables in `.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret key
- `ENVIRONMENT` - development/production
- `DEBUG` - Enable/disable debug mode

## ⚠️ Important Notes

1. **Security**: Change default passwords and secret keys before production
2. **Database**: Data persists in Docker volume `postgres_data`
3. **Development**: Auto-reload is enabled for code changes
4. **Testing**: Use the test script to verify functionality

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps db

# Restart database
docker-compose restart db
```

### Port Conflicts
If port 8000 or 5432 is already in use, modify `docker-compose.yml` to use different ports.

### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

---

🎉 **Congratulations!** You've successfully set up Stage 1 of the Newsletter Curator API. The foundation is ready for adding authentication, email integration, and LLM-powered features in the next stages.