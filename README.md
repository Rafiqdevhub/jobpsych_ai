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

## 🔌 API Endpoints & Workflows

### System Endpoints

#### 1. Root Endpoint (`GET /`)

**Purpose**: API information and system status overview

**Workflow**:

1. Returns comprehensive system information
2. No authentication required
3. Provides quick overview of all capabilities

**Response**:

```json
{
  "app_name": "JobPsych AI - Role Suggestion and HR Intelligence Platform",
  "message": "AI-Powered Resume Analysis & Job Role Recommendation Service",
  "status": "running",
  "version": "2.0.0",
  "core_capabilities": {
    "resume_parsing": {...},
    "ai_analysis": {...},
    "interview_assistance": {...},
    "batch_processing": {...}
  },
  "documentation": "Interactive API docs available at /docs",
  "health_check": "System health status available at /health",
  "rate_limiting": "Protected endpoints: 5 requests per day per IP for /analyze-resume",
  "ai_powered_by": "Google Gemini 2.5 Flash"
}
```

#### 2. Health Check (`GET /health`)

**Purpose**: System health monitoring and configuration validation

**Workflow**:

1. Checks Google Gemini API key configuration
2. Validates environment setup
3. Returns deployment environment info

**Response**:

```json
{
  "status": "healthy",
  "api_configured": true,
  "environment": "development"
}
```

#### 3. CORS Test (`GET /api/cors-test`)

**Purpose**: Test CORS configuration and connectivity

**Workflow**:

1. Validates cross-origin request handling
2. Returns success confirmation with timestamp

### Resume Analysis Endpoints

#### 4. Basic Resume Analysis (`POST /api/analyze-resume`)

**Purpose**: Quick resume analysis with role recommendations (Public endpoint)

**Authentication**: ❌ None required
**Rate Limit**: 5 requests per day per IP address
**File Support**: PDF, DOCX, DOC (max 10MB)

**Workflow**:

1. **File Upload**: Accept resume file via multipart/form-data
2. **Resume Parsing**: Extract structured data (personal info, experience, education, skills)
3. **AI Analysis**: Generate role recommendations using Google Gemini AI
4. **Optional Parameters**: target_role and job_description for focused analysis
5. **Response**: Resume data + role recommendations (no interview questions)

**Parameters**:

- `file` (required): Resume file (PDF/DOCX/DOC)
- `target_role` (optional): Specific job role to analyze fit for
- `job_description` (optional): Job requirements for better analysis

**Example Request**:

```bash
curl -X POST "http://localhost:8000/api/analyze-resume" \
     -F "file=@resume.pdf" \
     -F "target_role=Software Engineer" \
     -F "job_description=Develop and maintain web applications using Python, React, and cloud technologies..."
```

**Response Structure**:

```json
{
  "resumeData": {
    "personalInfo": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "location": "San Francisco, CA"
    },
    "workExperience": [...],
    "education": [...],
    "skills": ["Python", "React", "AWS"],
    "highlights": [...]
  },
  "questions": [],
  "roleRecommendations": [
    {
      "roleName": "Software Engineer",
      "matchPercentage": 85,
      "reasoning": "Strong technical skills match...",
      "requiredSkills": ["Python", "React"],
      "missingSkills": ["Kubernetes"],
      "learningResources": [...]
    }
  ]
}
```

#### 5. Advanced HR Analysis (`POST /api/hiredesk-analyze`)

**Purpose**: Comprehensive HR analysis with full AI insights (Authenticated endpoint)

**Authentication**: ✅ JWT token required
**Rate Limit**: 10 files per user account (tracked via external auth service)
**File Support**: PDF, DOCX, DOC (max 10MB)

**Workflow**:

1. **Authentication**: Validate JWT token and extract user identity
2. **Rate Limit Check**: Verify user hasn't exceeded 10-file limit
3. **File Validation**: Check file format, size, and integrity
4. **Resume Parsing**: Extract comprehensive structured data
5. **AI Analysis**: Perform complete analysis including:
   - Role recommendations with best-fit selection
   - Role fit assessment for target position
   - Interview question generation (technical, behavioral, experience-based)
   - Resume scoring (0-100) with detailed breakdown
   - Personality insights and work style analysis
   - Career path prediction and advancement timeline
6. **Rate Limit Update**: Increment user's upload counter

**Parameters**:

- `file` (required): Resume file (PDF/DOCX/DOC)
- `target_role` (required): Specific job role for detailed analysis
- `job_description` (required): Complete job requirements

**Example Request**:

```bash
curl -X POST "http://localhost:8000/api/hiredesk-analyze" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -F "file=@resume.pdf" \
     -F "target_role=Product Manager" \
     -F "job_description=Lead product development for SaaS platform. 5+ years experience in product management, agile methodologies, data analysis, stakeholder management..."
```

**Response Structure**:

```json
{
  "resumeData": {
    "personalInfo": {...},
    "workExperience": [...],
    "education": [...],
    "skills": [...],
    "highlights": [...]
  },
  "questions": [
    {
      "question": "Can you describe a time when you led a cross-functional team through a product launch?",
      "type": "behavioral",
      "category": "leadership"
    },
    {
      "question": "How do you prioritize features in your product roadmap?",
      "type": "technical",
      "category": "product_management"
    }
  ],
  "roleRecommendations": [...],
  "resumeScore": {
    "overall_score": 82,
    "technical_score": 85,
    "experience_score": 80,
    "education_score": 90,
    "communication_score": 75,
    "strengths": ["Strong technical background", "Leadership experience"],
    "weaknesses": ["Limited formal product management education"],
    "recommendations": [...]
  },
  "personalityInsights": {
    "work_style": "Analytical and collaborative",
    "leadership_style": "Transformational",
    "communication_style": "Clear and concise",
    "decision_making": "Data-driven approach"
  },
  "careerPath": {
    "current_level": "Senior Individual Contributor",
    "next_roles": ["Product Manager", "Engineering Manager"],
    "timeline": "2-3 years",
    "development_areas": [...]
  }
}
```

#### 6. Batch Resume Analysis (`POST /api/batch-analyze`)

**Purpose**: Process multiple resumes simultaneously for bulk analysis

**Authentication**: ❌ None required
**Rate Limit**: 10 resumes per batch request
**File Support**: PDF, DOCX, DOC (max 10MB each)

**Workflow**:

1. **Batch Validation**: Accept 2-10 resume files
2. **Parallel Processing**: Process each resume independently
3. **Error Handling**: Continue processing other files if one fails
4. **Comprehensive Analysis**: Full AI analysis for each resume
5. **Results Aggregation**: Return array of analysis results

**Parameters**:

- `files` (required): Array of resume files (2-10 files)
- `target_role` (optional): Analyze all resumes against this role
- `job_description` (optional): Job requirements for focused analysis

**Example Request**:

```bash
curl -X POST "http://localhost:8000/api/batch-analyze" \
     -F "files=@candidate1.pdf" \
     -F "files=@candidate2.pdf" \
     -F "files=@candidate3.pdf" \
     -F "target_role=Frontend Developer" \
     -F "job_description=Build responsive web applications using React, TypeScript, and modern CSS frameworks..."
```

**Response Structure**:

```json
[
  {
    "resumeData": {...},
    "questions": [...],
    "roleRecommendations": [...],
    "resumeScore": {...},
    "personalityInsights": {...},
    "careerPath": {...}
  },
  {
    "resumeData": {...},
    "questions": [...],
    "roleRecommendations": [...],
    "resumeScore": {...},
    "personalityInsights": {...},
    "careerPath": {...}
  }
]
```

#### 7. Resume Comparison (`POST /api/compare-resumes`)

**Purpose**: Compare and rank multiple candidates for the same position

**Authentication**: ❌ None required
**Rate Limit**: 5 resumes per comparison request
**File Support**: PDF, DOCX, DOC (max 10MB each)

**Workflow**:

1. **Comparison Setup**: Accept 2-5 resume files
2. **Individual Scoring**: Calculate comprehensive scores for each candidate
3. **Ranking Algorithm**: Sort candidates by overall score (descending)
4. **Comparison Summary**: Generate aggregate statistics
5. **HR Recommendations**: Provide hiring guidance based on scores

**Parameters**:

- `files` (required): Array of resume files (2-5 files)

**Example Request**:

```bash
curl -X POST "http://localhost:8000/api/compare-resumes" \
     -F "files=@candidate_a.pdf" \
     -F "files=@candidate_b.pdf" \
     -F "files=@candidate_c.pdf" \
     -F "files=@candidate_d.pdf"
```

**Response Structure**:

```json
{
  "comparison_summary": {
    "total_candidates": 4,
    "highest_score": 88,
    "average_score": 76.5,
    "score_range": "65-88"
  },
  "ranked_candidates": [
    {
      "filename": "candidate_a.pdf",
      "resumeData": {...},
      "score": 88,
      "strengths": ["Exceptional technical skills", "Strong leadership experience"],
      "weaknesses": ["Limited formal education in target field"],
      "rank": 1
    },
    {
      "filename": "candidate_b.pdf",
      "resumeData": {...},
      "score": 82,
      "strengths": ["Excellent communication skills", "Diverse industry experience"],
      "weaknesses": ["Some technical skill gaps"],
      "rank": 2
    }
  ],
  "recommendations": [
    "Consider top 3 candidates for interviews",
    "Review candidates with scores > 80 for immediate consideration",
    "Candidates with scores < 60 may need additional training",
    "Schedule technical interviews for top 2 candidates"
  ]
}
```

## 🔄 Complete Workflow Examples

### Scenario 1: Initial Candidate Screening

```bash
# Step 1: Quick analysis of single resume
curl -X POST "http://localhost:8000/api/analyze-resume" \
     -F "file=@candidate_resume.pdf" \
     -F "target_role=Software Engineer"

# Step 2: If promising, get detailed analysis
curl -X POST "http://localhost:8000/api/hiredesk-analyze" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "file=@candidate_resume.pdf" \
     -F "target_role=Software Engineer" \
     -F "job_description=Detailed job requirements..."
```

### Scenario 2: Bulk Recruitment Drive

```bash
# Step 1: Batch analyze all applications
curl -X POST "http://localhost:8000/api/batch-analyze" \
     -F "files=@app1.pdf" \
     -F "files=@app2.pdf" \
     -F "files=@app3.pdf" \
     -F "target_role=Data Scientist"

# Step 2: Compare top candidates
curl -X POST "http://localhost:8000/api/compare-resumes" \
     -F "files=@top_candidate1.pdf" \
     -F "files=@top_candidate2.pdf" \
     -F "files=@top_candidate3.pdf"
```

### Scenario 3: HR Dashboard Integration

```bash
# Step 1: Authenticate user
# (JWT token obtained from authentication service)

# Step 2: Upload and analyze resume
curl -X POST "http://localhost:8000/api/hiredesk-analyze" \
     -H "Authorization: Bearer ${JWT_TOKEN}" \
     -F "file=@resume.pdf" \
     -F "target_role=${JOB_ROLE}" \
     -F "job_description=${JOB_DESCRIPTION}"

# Step 3: Store results in HR system
# Process the comprehensive analysis response
```

## 📊 Rate Limiting & Usage Guidelines

### Public Endpoints

- **`/api/analyze-resume`**: 5 requests per day per IP address
- **`/api/batch-analyze`**: No specific limit (reasonable usage expected)
- **`/api/compare-resumes`**: No specific limit (reasonable usage expected)

### Authenticated Endpoints

- **`/api/hiredesk-analyze`**: 10 files per user account (tracked via external service)

### File Upload Limits

- **Maximum file size**: 10MB per file
- **Supported formats**: PDF, DOCX, DOC
- **Batch limits**: 2-10 files for batch analysis, 2-5 files for comparison

### Error Handling

- **400 Bad Request**: Invalid parameters or file format
- **401 Unauthorized**: Missing or invalid JWT token
- **422 Unprocessable Entity**: Validation errors or file processing issues
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server-side processing errors

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
