# JobPsych AI

AI-powered resume analysis and job role recommendation service for HR professionals. This FastAPI application provides comprehensive resume parsing, job role recommendations, skill gap analysis, interview question generation, and advanced HR analytics.AI-powered resume analysis and job role recommendation service for HR professionals. This FastAPI application provides comprehensive resume parsing, job role recommendations, skill gap analysis, and interview question generation.

## 🚀 Features

- **Resume Parsing**: Extract information from PDF and DOCX resume files
- **Job Role Recommendations**: AI-powered suggestions for best-fitting job roles with match percentages

- **Skill Gap Analysis**: Identify missing skills and provide learning recommendations
- **Interview Question Generation**: Generate tailored interview questions (technical, behavioral, experience-based)

- **Role Fit Analysis**: Analyze candidate fit for specific job roles with detailed reasoning
- **Resume Scoring**: Comprehensive scoring (0-100) with breakdown by technical, experience, education, and communication skills
- **RESTful API**: Clean, documented API endpoints

- **Personality Insights**: AI-powered personality analysis and work style assessment

- **Career Path Prediction**: Predict career advancement and timeline

- **Batch Processing**: Analyze multiple resumes simultaneously

- **Resume Comparison**: Compare and rank multiple candidates- Python 3.9 or higher

- **RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation- Google Gemini API key (for AI features)

- uv package manager (recommended) or pip

## 🛠️ Installation

- Python 3.9 or higher

- Google Gemini API key (for AI features)

### 1. Clone the Repository

- uv package manager (recommended) or pip

  ```bash

  ```

## 🛠️ Installation

### 1. Clone the Repository

````bash
git clone https://github.com/Rafiqdevhub/jobpsych_ai.git

cd jobpsych_ai```bash

```# Copy the environment template

cp .env.example .env

### 2. Set Up Environment Variables

# Edit .env and add your Google Gemini API key

```bashGOOGLE_API_KEY="your_actual_api_key_here"

# Copy the environment templateHOST="localhost"

cp .env.example .envPORT="8000"

````

# Edit .env and add your Google Gemini API key

GOOGLE_API_KEY="your_actual_api_key_here"### 3. Install Dependencies

HOST="localhost"

PORT="8000"#### Using uv (Recommended)

````

```bash

### 3. Install Dependencies# Install uv if you don't have it

pip install uv

#### Using uv (Recommended)

# Install dependencies

```bashuv sync

# Install uv if you don't have it```

pip install uv

#### Using pip

# Install dependencies

uv sync```bash

```# Create virtual environment

python -m venv .venv

#### Using pip

# Activate virtual environment

```bash# On Windows:

# Create virtual environment.venv\Scripts\activate

python -m venv .venv# On macOS/Linux:

source .venv/bin/activate

# Activate virtual environment

# On Windows:# Install dependencies

.venv\Scripts\activatepip install -r requirements.txt

# On macOS/Linux:```

source .venv/bin/activate

## 🚀 Running the Application

# Install dependencies

pip install -r requirements.txt### Development Mode

````

#### Using uv

## 🚀 Running the Application

```bash

### Development Modeuv run uvicorn app.main:app --port 8000 --reload

```

````bash

uv run uvicorn app.main:app --port 8000 --reload```bash

```# Activate virtual environment first

.venv\Scripts\activate  # Windows

#### Using pipsource .venv/bin/activate  # macOS/Linux



```bashuvicorn app.main:app --port 8000 --reload

# Activate virtual environment first```

.venv\Scripts\activate  # Windows

source .venv/bin/activate  # macOS/Linux### Production Mode



uvicorn app.main:app --port 8000 --reload#### Using uv

````

```bash

### Production Modeuv run uvicorn app.main:app --host 0.0.0.0 --port 8000

```

#### Using uv

#### Using pip

````bash

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000```bash

```uvicorn app.main:app --host 0.0.0.0 --port 8000

````

#### Using pip

### Using Docker

```bash

uvicorn app.main:app --host 0.0.0.0 --port 8000#### Build and Run with Docker Compose

```

```bash

### Using Dockerdocker-compose up --build

```

#### Build and Run with Docker Compose

#### Build and Run with Docker

````bash

docker-compose up --build```bash

```# Build the image

docker build -t jobpsych-backend .

#### Build and Run with Docker

# Run the container

```bashdocker run -p 8000:8000 --env-file .env jobpsych-backend

# Build the image```

docker build -t jobpsych-ai .

## 📖 API Documentation

# Run the container

docker run -p 8000:8000 --env-file .env jobpsych-aiOnce the application is running, visit:

````

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs

## 📖 API Documentation- **ReDoc Documentation**: http://localhost:8000/redoc

- **Health Check**: http://localhost:8000/

Once the application is running, visit:

## 🔌 API Endpoints

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs

- **ReDoc Documentation**: http://localhost:8000/redoc### Core Endpoints

- **Health Check**: http://localhost:8000/health

- **API Info**: http://localhost:8000/| Method | Endpoint | Description |

| ------ | ------------------------- | ----------------------------------------------- |

## 🔌 API Endpoints| `GET` | `/` | Health check and API information |

| `GET` | `/health` | Detailed health check with API status |

### Core Endpoints| `POST` | `/api/generate-questions` | Generate interview questions from resume |

| `POST` | `/api/analyze-resume` | Analyze resume and provide role recommendations |

| Method | Endpoint | Description || `POST` | `/api/hiredesk-analyze` | Advanced HR analysis with fit assessment |

| ------ | ------------------------- | ----------------------------------------------- |

| `GET` | `/` | API information and health status |### Request Examples

| `GET` | `/health` | Detailed health check with API configuration |

| `POST` | `/api/analyze-resume` | Basic resume analysis with role recommendations |#### Generate Interview Questions

| `POST` | `/api/hiredesk-analyze` | Advanced HR analysis with fit assessment |

| `POST` | `/api/batch-analyze` | Batch processing for multiple resumes |```bash

| `POST` | `/api/compare-resumes` | Compare and rank multiple resumes |curl -X POST "http://localhost:8000/api/generate-questions" \

     -F "file=@resume.pdf"

### Request Examples```

#### Basic Resume Analysis#### Analyze Resume

`bash`bash

curl -X POST "http://localhost:8000/api/analyze-resume" \curl -X POST "http://localhost:8000/api/analyze-resume" \

     -F "file=@resume.pdf" \     -F "file=@resume.pdf" \

     -F "target_role=Software Engineer" \     -F "target_role=Software Engineer" \

     -F "job_description=Develop and maintain web applications..."     -F "job_description=Job description text here..."

````



#### Advanced HR Analysis#### Advanced HR Analysis



```bash```bash

curl -X POST "http://localhost:8000/api/hiredesk-analyze" \curl -X POST "http://localhost:8000/api/hiredesk-analyze" \

     -F "file=@resume.pdf" \     -F "file=@resume.pdf" \

     -F "target_role=Product Manager" \     -F "target_role=Product Manager" \

     -F "job_description=Detailed job description..."     -F "job_description=Detailed job description..."

````

#### Batch Analysis (Multiple Resumes)## 🏗️ Project Structure

`bash`

curl -X POST "http://localhost:8000/api/batch-analyze" \├── app/

     -F "files=@resume1.pdf" \│   ├── main.py                 # FastAPI application setup

     -F "files=@resume2.pdf" \│   ├── routers/

     -F "target_role=Data Scientist" \│   │   └── resume_router.py    # API route definitions

     -F "job_description=Analyze data and build ML models..."│   ├── services/

````│ │   ├── resume_parser.py    # Resume parsing logic

│   │   ├── question_generator.py # Interview question generation

#### Compare Resumes│   │   └── role_recommender.py # Job role recommendations

│   └── models/

```bash│       └── schemas.py          # Pydantic models and schemas

curl -X POST "http://localhost:8000/api/compare-resumes" \├── .env.example               # Environment variables template

     -F "files=@resume1.pdf" \├── dockerfile                 # Docker container configuration

     -F "files=@resume2.pdf" \├── docker-compose.yml         # Docker Compose setup

     -F "files=@resume3.pdf"├── pyproject.toml            # Project configuration

```├── requirements.txt          # Python dependencies

└── test_services.py          # Service testing script

## 🏗️ Project Structure```



```## 🔧 Configuration

├── app/

│   ├── main.py                 # FastAPI application setup and CORS### Environment Variables

│   ├── routers/

│   │   └── resume_router.py    # API route definitions and handlers| Variable         | Description                           | Required |

│   ├── services/| ---------------- | ------------------------------------- | -------- |

│   │   ├── resume_parser.py    # Resume parsing logic (PDF/DOCX)| `GOOGLE_API_KEY` | Google Gemini API key for AI features | Yes      |

│   │   ├── question_generator.py # Interview question generation| `HOST`           | Server host (default: localhost)      | No       |

│   │   ├── role_recommender.py # Job role recommendations| `PORT`           | Server port (default: 8000)           | No       |

│   │   └── advanced_analyzer.py # Advanced analysis (scoring, personality, career)

│   └── models/### CORS Configuration

│       └── schemas.py          # Pydantic models and response schemas

├── .env.example               # Environment variables templateThe application is configured to accept requests from:

├── dockerfile                 # Docker container configuration

├── docker-compose.yml         # Docker Compose setup- `https://jobpsych.vercel.app` (Production frontend)

├── pyproject.toml            # Project configuration and dependencies- `http://localhost:3000` (Development frontend)

├── requirements.txt          # Python dependencies (legacy)

├── test_services.py          # Service testing and validation script## 🧪 Testing

├── vercel.json               # Vercel deployment configuration

└── uv.lock                  # uv dependency lock file### Run Service Tests

````

````bash

## 🔧 Configuration# Using uv

uv run python test_services.py

### Environment Variables

# Using pip

| Variable         | Description                           | Required | Default |python test_services.py

| ---------------- | ------------------------------------- | -------- | ------- |```

| `GOOGLE_API_KEY` | Google Gemini API key for AI features | Yes      | -       |

| `HOST`           | Server host                           | No       | localhost |### API Testing

| `PORT`           | Server port                           | No       | 8000    |

```bash

### CORS Configuration# Health check

curl http://localhost:8000/

The application accepts requests from:

# Get API documentation

- `https://jobpsych.vercel.app` (Production frontend)curl http://localhost:8000/docs

- `https://hiredesk.vercel.app/` (HR Dashboard)```

- `http://localhost:3000` (Development frontend)

## 🚀 Deployment

## 🧪 Testing

### Docker Deployment

### Run Service Tests

```bash

```bash# Build the image

# Using uvdocker build -t jobpsych-backend .

uv run python test_services.py

# Run with environment variables

# Using pipdocker run -p 8000:8000 --env-file .env jobpsych-backend

python test_services.py```

````

### Docker Compose Deployment

### API Testing

````bash

```bashdocker-compose up -d

# Health check```

curl http://localhost:8000/

### Vercel Deployment

# Detailed health check

curl http://localhost:8000/healthThe application includes Vercel configuration for serverless deployment:



# Get API documentation```bash

curl http://localhost:8000/docsvercel --prod

````

## 🚀 Deployment## 🔄 CI/CD Pipeline

### Docker DeploymentThe project includes GitHub Actions for automated:

````bash- **Testing**: Runs on every push and pull request

# Build the image- **Building**: Creates Docker images

docker build -t jobpsych-ai .- **Deployment**: Pushes to Docker Hub



# Run with environment variables### Pipeline Features

docker run -p 8000:8000 --env-file .env jobpsych-ai

```- Multi-stage Docker builds

- Automated testing

### Docker Compose Deployment- Security scanning

- Production deployments

```bash

docker-compose up -d## 📦 Dependencies

````

### Core Dependencies

### Vercel Deployment

- **FastAPI**: Modern web framework for building APIs

The application includes Vercel configuration for serverless deployment:- **Uvicorn**: ASGI server for FastAPI

- **Pydantic**: Data validation and serialization

````bash- **Google Generative AI**: AI-powered text generation

# Install Vercel CLI

npm install -g vercel### Document Processing



# Deploy- **PyPDF2**: PDF file processing

vercel --prod- **python-docx**: Word document processing

```- **pdfplumber**: Advanced PDF text extraction



## 🔄 CI/CD Pipeline### Utilities



The project includes GitHub Actions for automated:- **python-dotenv**: Environment variable management

- **python-multipart**: File upload handling

- **Testing**: Runs on every push and pull request- **slowapi**: Rate limiting

- **Building**: Creates Docker images

- **Deployment**: Pushes to Docker Hub as `rafiq9323/jobpsych-ai`## 🤝 Contributing



### Pipeline Features1. Fork the repository

2. Create a feature branch: `git checkout -b feature-name`

- Multi-stage Docker builds with uv3. Make your changes and add tests

- Automated testing with service validation4. Run tests: `python test_services.py`

- Security scanning5. Commit your changes: `git commit -am 'Add new feature'`

- Production deployments to Docker Hub6. Push to the branch: `git push origin feature-name`

7. Submit a pull request

## 📦 Dependencies

## 📝 License

### Core Dependencies

This project is licensed under the MIT License - see the LICENSE file for details.

- **FastAPI**: Modern web framework for building APIs

- **Uvicorn**: ASGI server for FastAPI## 🆘 Troubleshooting

- **Pydantic**: Data validation and serialization

- **Google Generative AI**: AI-powered text generation### Common Issues



### Document Processing#### 1. "Failed to canonicalize script path" Error



- **PyPDF2**: PDF file processing```bash

- **python-docx**: Word document processing# Try running with explicit app directory

- **pdfplumber**: Advanced PDF text extractionuvicorn app.main:app --port 8000 --reload --app-dir .

````

### Utilities

#### 2. Missing Google API Key

- **python-dotenv**: Environment variable management

- **python-multipart**: File upload handling```bash

- **slowapi**: Rate limiting# Check your .env file

cat .env

#

# Clear Docker cache

## 🆘 Troubleshootingdocker system prune -a

# Rebuild

### Common Issuesdocker-compose up --build --force-recreate

`````

#### 1. "Failed to canonicalize script path" Error

## 📞 Support

````bash

# Try running with explicit app directoryFor support and questions:

uvicorn app.main:app --port 8000 --reload --app-dir .

```- Create an issue on GitHub

- Check the API documentation at `/docs`

#### 2. Missing Google API Key- Review the health endpoint at `/health`



```bash## 🔄 Recent Updates

# Check your .env file

cat .env- **v2.0.0**: Complete rewrite with FastAPI, improved AI integration

# Should contain: GOOGLE_API_KEY="your_key_here"- Removed heavy ML dependencies for better performance

```- Added comprehensive error handling and validation

- Enhanced Docker and CI/CD setup

#### 3. Port Already in Use

---

```bash

# Use a different port**Built with ❤️ for HR professionals and job seekers**</content>

uvicorn app.main:app --port 8001 --reload
````

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

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the health endpoint at `/health`

## 🔄 Recent Updates

- **v2.0.0**: Complete rewrite with FastAPI, improved AI integration
- Added batch processing for multiple resumes
- Enhanced resume comparison and ranking
- Added comprehensive scoring and personality analysis
- Improved Docker setup with uv package manager
- Added Vercel deployment support

---

**Built with ❤️ for HR professionals and job seekers**
`````
