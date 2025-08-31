# JobPsych Backend

AI-powered resume analysis and job role recommendation service for HR professionals. This FastAPI application provides comprehensive resume parsing, job role recommendations, skill gap analysis, and interview question generation.

## 🚀 Features

- **Resume Parsing**: Extract information from PDF and DOCX resume files
- **Job Role Recommendations**: AI-powered suggestions for best-fitting job roles
- **Skill Gap Analysis**: Identify missing skills and provide learning recommendations
- **Interview Question Generation**: Generate tailored interview questions based on resume and job requirements
- **Role Fit Analysis**: Analyze candidate fit for specific job roles
- **RESTful API**: Clean, documented API endpoints

## 📋 Prerequisites

- Python 3.9 or higher
- Google Gemini API key (for AI features)
- uv package manager (recommended) or pip

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Rafiqdevhub/AI-Resume-Analayzer_Backend.git
cd AI-Resume-Analayzer_Backend
```

### 2. Set Up Environment Variables

```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your Google Gemini API key
GOOGLE_API_KEY="your_actual_api_key_here"
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
```

#### Using pip

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

## 🚀 Running the Application

### Development Mode

#### Using uv

```bash
uv run uvicorn app.main:app --port 8000 --reload
```

#### Using pip

```bash
# Activate virtual environment first
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

uvicorn app.main:app --port 8000 --reload
```

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

## 📖 API Documentation

Once the application is running, visit:

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint                  | Description                                     |
| ------ | ------------------------- | ----------------------------------------------- |
| `GET`  | `/`                       | Health check and API information                |
| `GET`  | `/health`                 | Detailed health check with API status           |
| `POST` | `/api/generate-questions` | Generate interview questions from resume        |
| `POST` | `/api/analyze-resume`     | Analyze resume and provide role recommendations |
| `POST` | `/api/hiredesk-analyze`   | Advanced HR analysis with fit assessment        |

### Request Examples

#### Generate Interview Questions

```bash
curl -X POST "http://localhost:8000/api/generate-questions" \
     -F "file=@resume.pdf"
```

#### Analyze Resume

```bash
curl -X POST "http://localhost:8000/api/analyze-resume" \
     -F "file=@resume.pdf" \
     -F "target_role=Software Engineer" \
     -F "job_description=Job description text here..."
```

#### Advanced HR Analysis

```bash
curl -X POST "http://localhost:8000/api/hiredesk-analyze" \
     -F "file=@resume.pdf" \
     -F "target_role=Product Manager" \
     -F "job_description=Detailed job description..."
```

## 🏗️ Project Structure

```
├── app/
│   ├── main.py                 # FastAPI application setup
│   ├── routers/
│   │   └── resume_router.py    # API route definitions
│   ├── services/
│   │   ├── resume_parser.py    # Resume parsing logic
│   │   ├── question_generator.py # Interview question generation
│   │   └── role_recommender.py # Job role recommendations
│   └── models/
│       └── schemas.py          # Pydantic models and schemas
├── .env.example               # Environment variables template
├── dockerfile                 # Docker container configuration
├── docker-compose.yml         # Docker Compose setup
├── pyproject.toml            # Project configuration
├── requirements.txt          # Python dependencies
└── test_services.py          # Service testing script
```

## 🔧 Configuration

### Environment Variables

| Variable         | Description                           | Required |
| ---------------- | ------------------------------------- | -------- |
| `GOOGLE_API_KEY` | Google Gemini API key for AI features | Yes      |
| `HOST`           | Server host (default: localhost)      | No       |
| `PORT`           | Server port (default: 8000)           | No       |

### CORS Configuration

The application is configured to accept requests from:

- `https://jobpsych.vercel.app` (Production frontend)
- `http://localhost:3000` (Development frontend)

## 🧪 Testing

### Run Service Tests

```bash
# Using uv
uv run python test_services.py

# Using pip
python test_services.py
```

### API Testing

```bash
# Health check
curl http://localhost:8000/

# Get API documentation
curl http://localhost:8000/docs
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build the image
docker build -t jobpsych-backend .

# Run with environment variables
docker run -p 8000:8000 --env-file .env jobpsych-backend
```

### Docker Compose Deployment

```bash
docker-compose up -d
```

### Vercel Deployment

The application includes Vercel configuration for serverless deployment:

```bash
vercel --prod
```

## 🔄 CI/CD Pipeline

The project includes GitHub Actions for automated:

- **Testing**: Runs on every push and pull request
- **Building**: Creates Docker images
- **Deployment**: Pushes to Docker Hub

### Pipeline Features

- Multi-stage Docker builds
- Automated testing
- Security scanning
- Production deployments

## 📦 Dependencies

### Core Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and serialization
- **Google Generative AI**: AI-powered text generation

### Document Processing

- **PyPDF2**: PDF file processing
- **python-docx**: Word document processing
- **pdfplumber**: Advanced PDF text extraction

### Utilities

- **python-dotenv**: Environment variable management
- **python-multipart**: File upload handling
- **slowapi**: Rate limiting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `python test_services.py`
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

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

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the health endpoint at `/health`

## 🔄 Recent Updates

- **v2.0.0**: Complete rewrite with FastAPI, improved AI integration
- Removed heavy ML dependencies for better performance
- Added comprehensive error handling and validation
- Enhanced Docker and CI/CD setup

---

**Built with ❤️ for HR professionals and job seekers**</content>
