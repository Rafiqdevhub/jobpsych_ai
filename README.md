# JobPsych AI - Resume Analysis & HR Intelligence Platform

[![CI/CD Pipeline](https://github.com/Rafiqdevhub/AI-Resume-Analayzer_Backend/actions/workflows/tests.yml/badge.svg)](https://github.com/Rafiqdevhub/AI-Resume-Analayzer_Backend/actions/workflows/tests.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

AI-powered resume analysis and job role recommendation service for HR professionals. This FastAPI application provides comprehensive resume parsing, job role recommendations, skill gap analysis, interview question generation, and advanced HR analytics using Google Gemini AI.

## Features

### Core Functionality

- Resume Parsing: Extract information from PDF and DOCX resume files
- Job Role Recommendations: AI-powered suggestions for best-fitting job roles with match percentages
- Skill Gap Analysis: Identify missing skills and provide learning recommendations
- Interview Question Generation: Generate tailored interview questions (technical, behavioral, experience-based)
- Resume Scoring: Comprehensive scoring (0-100) with breakdown by technical, experience, education, and communication skills

### Advanced Features

- Personality Insights: AI-powered personality analysis and work style assessment
- Career Path Prediction: Predict career advancement and timeline
- Batch Processing: Analyze multiple resumes simultaneously
- Resume Comparison: Compare and rank multiple candidates
- Role Fit Analysis: Analyze candidate fit for specific job roles with detailed reasoning

### Technical Features

- RESTful API: Clean, documented API endpoints with automatic OpenAPI documentation
- JWT Authentication: Secure endpoints with token-based authentication
- Rate Limiting: IP-based rate limiting (5 requests/day for public endpoints)
- Docker Support: Containerized deployment with Docker Compose
- Vercel Ready: Serverless deployment configuration
- Comprehensive Testing: 44 automated tests with 37% code coverage
- Type Safety: Full type hints with mypy validation
- Code Quality: Ruff linting and formatting

## Tech Stack

- **Backend**: FastAPI 0.115+ (Python web framework)
- **AI Engine**: Google Gemini AI
- **Document Processing**: pypdf, pdfplumber, python-docx
- **Data Validation**: Pydantic
- **Authentication**: python-jose with JWT
- **Rate Limiting**: slowapi, aiohttp
- **Package Management**: uv (modern Python package manager)
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Code Quality**: ruff, mypy, safety
- **Deployment**: Docker, Docker Compose, Vercel
- **CI/CD**: GitHub Actions

## Prerequisites

- Python 3.9 or higher
- Google Gemini API key (for AI features)
- uv package manager
- Docker & Docker Compose (optional, for containerized deployment)

## Installation

### 1. Clone the Repository

```bash
git clone
cd
```

### 2. Set Up Environment Variables

````bash
# Copy the environment template
cp .env.example .env
```bash
# Copy the environment template
cp .env.example .env
````

Edit `.env` and add your configuration:

```bash
# Google Gemini API Key (Required)
GOOGLE_API_KEY="your_actual_api_key_here"

# JWT Configuration (Required for authenticated endpoints)
JWT_SECRET="your_jwt_secret_key_here"
JWT_ACCESS_SECRET="your_jwt_access_secret_here"

# FastAPI Settings (Optional)
HOST="localhost"
PORT="8000"
```

### 3. Install Dependencies

#### Using uv (Recommended)

```bash
# Install uv if you don't have it
pip install uv

# Install dependencies
uv sync

# For development with all tools
uv sync --dev
```

#### Using pip (Alternative)

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Development Mode

#### Using uv

````bash
```bash
uv run uvicorn app.main:app --port 8000 --reload
````

#### Using pip

````bash

```bash
# Activate virtual environment first
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

uvicorn app.main:app --port 8000 --reload
````

### Production Mode

#### Using uv

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Using pip

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Docker

#### Build and Run with Docker Compose

```bash
docker-compose up --build
```

#### Build and Run with Docker

```bash
# Build the image
docker build -t jobpsych-backend .

# Run the container
docker run -p 8000:8000 --env-file .env jobpsych-backend
```

## API Documentation

Once the application is running, visit:

- **Interactive API Docs (Swagger UI)**: <http://localhost:8000/docs>
- **ReDoc Documentation**: <http://localhost:8000/redoc>
- **Health Check**: <http://localhost:8000/>
- **Detailed Health Check**: <http://localhost:8000/health>

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint                | Authentication | Description                                                                  |
| ------ | ----------------------- | -------------- | ---------------------------------------------------------------------------- |
| `GET`  | `/`                     | ❌ No          | API information and health status                                            |
| `GET`  | `/health`               | ❌ No          | Detailed health check with API configuration                                 |
| `POST` | `/api/analyze-resume`   | ❌ No          | Basic resume analysis with role recommendations (Rate limited: 5/day per IP) |
| `POST` | `/api/hiredesk-analyze` | ✅ Yes         | Advanced HR analysis with fit assessment (Requires JWT token)                |
| `POST` | `/api/batch-analyze`    | ❌ No          | Batch processing for multiple resumes                                        |
| `POST` | `/api/compare-resumes`  | ❌ No          | Compare and rank multiple resumes                                            |

### Request Examples

#### Basic Resume Analysis (Public)

```bash
curl -X POST "http://localhost:8000/api/analyze-resume" \
     -F "file=@resume.pdf" \
     -F "target_role=Software Engineer" \
     -F "job_description=Develop and maintain web applications using Python, React, and cloud technologies..."
```

#### Advanced HR Analysis (Authenticated)

```bash
curl -X POST "http://localhost:8000/api/hiredesk-analyze" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "file=@resume.pdf" \
     -F "target_role=Product Manager" \
     -F "job_description=Detailed job description with requirements..."
```

#### Batch Analysis (Multiple Resumes)

```bash
curl -X POST "http://localhost:8000/api/batch-analyze" \
     -F "files=@resume1.pdf" \
     -F "files=@resume2.pdf" \
     -F "target_role=Data Scientist" \
     -F "job_description=Analyze data and build ML models..."
```

#### Compare Resumes

```bash
curl -X POST "http://localhost:8000/api/compare-resumes" \
     -F "files=@resume1.pdf" \
     -F "files=@resume2.pdf" \
     -F "files=@resume3.pdf"
```

## Project Structure

```text
jobpsych_ai/
├── app/
│   ├── main.py                      # FastAPI application setup and CORS configuration
│   ├── dependencies/
│   │   └── auth.py                  # JWT authentication dependency
│   ├── routers/
│   │   └── resume_router.py         # API route definitions and request handlers
│   ├── services/
│   │   ├── resume_parser.py         # Resume parsing logic (PDF/DOCX processing)
│   │   ├── question_generator.py    # AI-powered interview question generation
│   │   ├── role_recommender.py      # Job role recommendations and fit analysis
│   │   ├── advanced_analyzer.py     # Advanced analysis (scoring, personality, career)
│   │   └── rate_limit_service.py    # Rate limiting service
│   └── models/
│       └── schemas.py               # Pydantic models and API response schemas
├── tests/
│   ├── test_services.py             # Integration tests (25 tests)
│   ├── test_unit.py                 # Unit tests (19 tests)
│   └── __init__.py                  # Package marker
├── .github/
│   └── workflows/
│       └── tests.yml                # GitHub Actions CI/CD pipeline
├── conftest.py                      # Pytest configuration and fixtures
├── .env.example                     # Environment variables template
├── .vercelignore                    # Vercel deployment exclusions
├── dockerfile                       # Docker container configuration
├── docker-compose.yml               # Docker Compose setup
├── pyproject.toml                   # Project configuration and dependencies
├── requirements.txt                 # Python dependencies (Vercel deployment)
├── vercel.json                      # Vercel deployment configuration
└── uv.lock                          # uv dependency lock file
```

## Configuration

### Environment Variables

| Variable            | Description                                  | Required       | Default   |
| ------------------- | -------------------------------------------- | -------------- | --------- |
| `GOOGLE_API_KEY`    | Google Gemini API key for AI features        | Yes            | -         |
| `JWT_SECRET`        | Secret key for JWT token signing             | Yes (for auth) | -         |
| `JWT_ACCESS_SECRET` | Access token secret (fallback to JWT_SECRET) | No             | -         |
| `HOST`              | Server host                                  | No             | localhost |
| `PORT`              | Server port                                  | No             | 8000      |

### CORS Configuration

The application accepts requests from:

- `https://jobpsych.vercel.app` (Production frontend)
- `https://hiredesk.vercel.app` (HR Dashboard)
- `http://localhost:3000` (Development frontend)
- `http://localhost:3001` (Alternative dev port)

## Testing

### Run All Tests

```bash
# Using uv
uv run pytest tests/ --cov=app --cov-report=term-missing

# Using pip
pytest tests/ --cov=app --cov-report=term-missing
```

### Run Specific Test File

```bash
# Using uv
uv run pytest tests/test_services.py -v
uv run pytest tests/test_unit.py -v

# Using pip
pytest tests/test_services.py -v
pytest tests/test_unit.py -v
```

### Run Specific Test Class

```bash
# Using uv
uv run pytest tests/test_unit.py::TestResumeParser -v
```

### Test Coverage

Current coverage: **37%**

- `app/dependencies/auth.py`: 94%
- `app/main.py`: 86%
- `app/models/schemas.py`: 100%

### API Testing

```bash
# Health check
curl http://localhost:8000/

# Detailed health check
curl http://localhost:8000/health

# CORS test
curl http://localhost:8000/api/cors-test
```

## CI/CD Pipeline

The project includes GitHub Actions for automated:

- **Testing**: Runs 44 tests on every push and pull request
- **Code Quality**: Linting with ruff, type checking with mypy
- **Security**: Vulnerability scanning with safety
- **Multi-Python Support**: Tests across Python 3.9, 3.10, and 3.11

### Pipeline Features

- Multi-version Python testing (3.9, 3.10, 3.11)
- Automated testing with pytest and coverage reporting
- Code quality checks (ruff linting and formatting)
- Static type checking (mypy)
- Security vulnerability scanning (safety)
- Coverage reporting with Codecov

## Dependencies

### Core Dependencies

- **fastapi>=0.115.12**: Modern web framework for building APIs
- **uvicorn>=0.34.2**: ASGI server for FastAPI
- **pydantic>=2.11.5**: Data validation and serialization
- **google-generativeai>=0.8.5**: AI-powered text generation

### Document Processing

- **pypdf>=4.0.0**: PDF file processing (modern, maintained)
- **python-docx>=1.1.2**: Word document processing
- **pdfplumber>=0.11.6**: Advanced PDF text extraction

### Authentication & Security

- **python-jose[cryptography]>=3.3.0**: JWT token handling
- **slowapi>=0.1.9**: Rate limiting for FastAPI
- **aiohttp>=3.8.0**: Async HTTP client

### Utilities

- **python-dotenv>=1.1.0**: Environment variable management
- **python-multipart>=0.0.20**: File upload handling

### Development Dependencies

- **pytest>=8.0.0**: Testing framework
- **pytest-asyncio>=0.23.0**: Async test support
- **pytest-cov>=4.1.0**: Coverage reporting
- **httpx>=0.25.0**: HTTP client for testing
- **ruff>=0.1.0**: Fast Python linter and formatter
- **mypy>=1.8.0**: Static type checking
- **safety>=2.3.0**: Security vulnerability scanning

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `uv run pytest tests/ --cov=app`
5. Run linting: `uv run ruff check . && uv run ruff format .`
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

## Troubleshooting

### Common Issues

#### 1. "Failed to canonicalize script path" Error

```bash
# Try running with explicit app directory
uvicorn app.main:app --port 8000 --reload --app-dir .
```

#### 2. Missing Google API Key

```bash
# Check your .env file
cat .env
# Should contain: GOOGLE_API_KEY="your_key_here"
```

#### 3. Port Already in Use

```bash
# Use a different port
uvicorn app.main:app --port 8001 --reload
```

#### 4. Docker Build Issues

```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker-compose up --build --force-recreate
```

#### 5. Import Errors

```bash
# Ensure you're in the correct directory
cd /path/to/AI-Resume-Analayzer_Backend

# Install dependencies
uv sync

# Run with proper Python path
PYTHONPATH=. uvicorn app.main:app --reload
```

#### 6. ModuleNotFoundError: No module named 'pypdf'

```bash
# Install pypdf (not PyPDF2)
uv pip install pypdf

# Or reinstall all dependencies
uv sync --dev
```
