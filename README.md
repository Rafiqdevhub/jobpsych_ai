# JobPsych AI - Resume Analysis & HR Intelligence Platform

AI-powered resume analysis and job role recommendation service for HR professionals. This FastAPI application provides comprehensive resume parsing, job role recommendations, skill gap analysis, interview question generation, and advanced HR analytics.AI-powered resume analysis and job role recommendation service for HR professionals. This FastAPI application provides comprehensive resume parsing, job role recommendations, skill gap analysis, and interview question generation.

[![CI/CD Pipeline](https://github.com/Rafiqdevhub/AI-Resume-Analayzer_Backend/actions/workflows/tests.yml/badge.svg)](https://github.com/Rafiqdevhub/AI-Resume-Analayzer_Backend/actions/workflows/tests.yml)

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

AI-powered resume analysis and job role recommendation service for HR professionals. This FastAPI application provides comprehensive resume parsing, job role recommendations, skill gap analysis, interview question generation, and advanced HR analytics using Google Gemini AI.

- **Resume Parsing**: Extract information from PDF and DOCX resume files

## Features

AI-powered resume analysis and job role recommendation service for HR professionals. This FastAPI application provides comprehensive resume parsing, job role recommendations, skill gap analysis, interview question generation, and advanced HR analytics using Google Gemini AI.- **Job Role Recommendations**: AI-powered suggestions for best-fitting job roles with match percentages

### Core Functionality

- **📄 Resume Parsing**: Extract information from PDF and DOCX resume files## 🚀 Features- **Skill Gap Analysis**: Identify missing skills and provide learning recommendations

- **🎯 Job Role Recommendations**: AI-powered suggestions for best-fitting job roles with match percentages

- **📊 Skill Gap Analysis**: Identify missing skills and provide learning recommendations- **Interview Question Generation**: Generate tailored interview questions (technical, behavioral, experience-based)

- **❓ Interview Question Generation**: Generate tailored interview questions (technical, behavioral, experience-based)

- **📈 Resume Scoring**: Comprehensive scoring (0-100) with breakdown by technical, experience, education, and communication skills### Core Functionality

### Advanced Features- **📄 Resume Parsing**: Extract information from PDF and DOCX resume files- **Role Fit Analysis**: Analyze candidate fit for specific job roles with detailed reasoning

- **🧠 Personality Insights**: AI-powered personality analysis and work style assessment

- **📈 Career Path Prediction**: Predict career advancement and timeline- **🎯 Job Role Recommendations**: AI-powered suggestions for best-fitting job roles with match percentages- **Resume Scoring**: Comprehensive scoring (0-100) with breakdown by technical, experience, education, and communication skills

- **🔄 Batch Processing**: Analyze multiple resumes simultaneously

- **⚖️ Resume Comparison**: Compare and rank multiple candidates- **📊 Skill Gap Analysis**: Identify missing skills and provide learning recommendations- **RESTful API**: Clean, documented API endpoints

- **🎯 Role Fit Analysis**: Analyze candidate fit for specific job roles with detailed reasoning

- **❓ Interview Question Generation**: Generate tailored interview questions (technical, behavioral, experience-based)

### Technical Features

- **⚡ RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation- **📈 Resume Scoring**: Comprehensive scoring (0-100) with breakdown by technical, experience, education, and communication skills- **Personality Insights**: AI-powered personality analysis and work style assessment

- **🐳 Docker Support**: Containerized deployment with Docker Compose

- **☁️ Vercel Ready**: Serverless deployment configuration### Advanced Features- **Career Path Prediction**: Predict career advancement and timeline

- **🧪 Comprehensive Testing**: Automated testing with pytest, coverage reporting

- **🔒 Type Safety**: Full type hints with mypy validation- **🧠 Personality Insights**: AI-powered personality analysis and work style assessment

- **🎨 Code Quality**: Ruff linting and formatting

- **📈 Career Path Prediction**: Predict career advancement and timeline- **Batch Processing**: Analyze multiple resumes simultaneously

## 🛠️ Tech Stack

- **🔄 Batch Processing**: Analyze multiple resumes simultaneously

- **Backend**: FastAPI (Python web framework)

- **AI Engine**: Google Gemini AI- **⚖️ Resume Comparison**: Compare and rank multiple candidates- **Resume Comparison**: Compare and rank multiple candidates- Python 3.9 or higher

- **Document Processing**: PyPDF2, pdfplumber, python-docx

- **Data Validation**: Pydantic- **🎯 Role Fit Analysis**: Analyze candidate fit for specific job roles with detailed reasoning

- **Package Management**: uv (modern Python package manager)

- **Testing**: pytest, pytest-cov, pytest-asyncio- **RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation- Google Gemini API key (for AI features)

- **Code Quality**: ruff, mypy, safety

- **Deployment**: Docker, Docker Compose, Vercel### Technical Features

- **CI/CD**: GitHub Actions

- **⚡ RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation- uv package manager (recommended) or pip

## 📋 Prerequisites

- **🐳 Docker Support**: Containerized deployment with Docker Compose

- Python 3.9 or higher

- Google Gemini API key (for AI features)- **☁️ Vercel Ready**: Serverless deployment configuration## 🛠️ Installation

- uv package manager (recommended) or pip

- Docker & Docker Compose (for containerized deployment)- **🧪 Comprehensive Testing**: Automated testing with pytest, coverage reporting

## 🛠️ Installation- **🔒 Type Safety**: Full type hints with mypy validation- Python 3.9 or higher

### 1. Clone the Repository- **🎨 Code Quality**: Ruff linting and formatting

```bash- Google Gemini API key (for AI features)

git clone https://github.com/Rafiqdevhub/AI-Resume-Analayzer_Backend.git

cd AI-Resume-Analayzer_Backend## 🛠️ Tech Stack

```

### 1. Clone the Repository

### 2. Set Up Environment Variables

- **Backend**: FastAPI (Python web framework)

````bash

# Copy the environment template- **AI Engine**: Google Gemini AI- uv package manager (recommended) or pip

cp .env.example .env

```- **Document Processing**: PyPDF2, pdfplumber, python-docx



Edit `.env` and add your Google Gemini API key:- **Data Validation**: Pydantic ```bash



```bash- **Package Management**: uv (modern Python package manager)

# Google Gemini API Key (Required)

GOOGLE_API_KEY="your_actual_api_key_here"- **Testing**: pytest, pytest-cov, pytest-asyncio ```



# FastAPI Settings (Optional)- **Code Quality**: ruff, mypy, safety

HOST="localhost"

PORT="8000"- **Deployment**: Docker, Docker Compose, Vercel## 🛠️ Installation

````

- **CI/CD**: GitHub Actions

### 3. Install Dependencies

### 1. Clone the Repository

#### Using uv (Recommended)

## 📋 Prerequisites

````````bash

# Install uv if you don't have it```````bash

pip install uv

- Python 3.9 or highergit clone https://github.com/Rafiqdevhub/jobpsych_ai.git

# Install dependencies

uv sync- Google Gemini API key (for AI features)



# For development with all tools- uv package manager (recommended) or pipcd jobpsych_ai```bash

uv sync --dev

```- Docker & Docker Compose (for containerized deployment)



#### Using pip (Alternative)```# Copy the environment template



```bash## 🛠️ Installation

# Create virtual environment

python -m venv .venvcp .env.example .env



# Activate virtual environment### 1. Clone the Repository

# On Windows:

.venv\Scripts\activate### 2. Set Up Environment Variables

# On macOS/Linux:

source .venv/bin/activate```bash



# Install dependenciesgit clone https://github.com/Rafiqdevhub/AI-Resume-Analayzer_Backend.git# Edit .env and add your Google Gemini API key

pip install -r requirements.txt

```cd AI-Resume-Analayzer_Backend



## 🚀 Running the Application``````bashGOOGLE_API_KEY="your_actual_api_key_here"



### Development Mode



#### Using uv### 2. Set Up Environment Variables# Copy the environment templateHOST="localhost"

```bash

uv run uvicorn app.main:app --port 8000 --reload

````````

`````bashcp .env.example .envPORT="8000"

#### Using pip

```bash# Copy the environment template

# Activate virtual environment first

.venv\Scripts\activate  # Windowscp .env.example .env````

source .venv/bin/activate  # macOS/Linux

`````

uvicorn app.main:app --port 8000 --reload

````# Edit .env and add your Google Gemini API key



### Production ModeEdit `.env` and add your Google Gemini API key:



#### Using uvGOOGLE_API_KEY="your_actual_api_key_here"### 3. Install Dependencies

```bash

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000```bash

````

# Google Gemini API Key (Required)HOST="localhost"

#### Using pip

`````bashGOOGLE_API_KEY="your_actual_api_key_here"

uvicorn app.main:app --host 0.0.0.0 --port 8000

```PORT="8000"#### Using uv (Recommended)



### Using Docker# FastAPI Settings (Optional)



#### Build and Run with Docker ComposeHOST="localhost"````

```bash

docker-compose up --buildPORT="8000"

`````

```````bash

#### Build and Run with Docker

```bash

# Build the image

docker build -t jobpsych-backend .### 3. Install Dependencies### 3. Install Dependencies# Install uv if you don't have it



# Run the container

docker run -p 8000:8000 --env-file .env jobpsych-backend

```#### Using uv (Recommended)pip install uv



## 📖 API Documentation



Once the application is running, visit:```bash#### Using uv (Recommended)



- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs# Install uv if you don't have it

- **ReDoc Documentation**: http://localhost:8000/redoc

- **Health Check**: http://localhost:8000/pip install uv# Install dependencies

- **Detailed Health Check**: http://localhost:8000/health



## 🔌 API Endpoints

# Install dependencies```bashuv sync

### Core Endpoints

uv sync

| Method | Endpoint | Description |

| ------ | ------------------------- | ----------------------------------------------- |# Install uv if you don't have it```

| `GET` | `/` | API information and health status |

| `GET` | `/health` | Detailed health check with API configuration |# For development with all tools

| `POST` | `/api/analyze-resume` | Basic resume analysis with role recommendations |

| `POST` | `/api/hiredesk-analyze` | Advanced HR analysis with fit assessment |uv sync --devpip install uv

| `POST` | `/api/batch-analyze` | Batch processing for multiple resumes |

| `POST` | `/api/compare-resumes` | Compare and rank multiple resumes |```



### Request Examples#### Using pip



#### Basic Resume Analysis#### Using pip

```bash

curl -X POST "http://localhost:8000/api/analyze-resume" \# Install dependencies

     -F "file=@resume.pdf" \

     -F "target_role=Software Engineer" \```bash

     -F "job_description=Develop and maintain web applications using Python, React, and cloud technologies..."

```# Create virtual environmentuv sync```bash



#### Advanced HR Analysispython -m venv .venv

```bash

curl -X POST "http://localhost:8000/api/hiredesk-analyze" \```# Create virtual environment

     -F "file=@resume.pdf" \

     -F "target_role=Product Manager" \# Activate virtual environment

     -F "job_description=Detailed job description with requirements..."

```# On Windows:python -m venv .venv



#### Batch Analysis (Multiple Resumes).venv\Scripts\activate

```bash

curl -X POST "http://localhost:8000/api/batch-analyze" \# On macOS/Linux:#### Using pip

     -F "files=@resume1.pdf" \

     -F "files=@resume2.pdf" \source .venv/bin/activate

     -F "target_role=Data Scientist" \

     -F "job_description=Analyze data and build ML models..."# Activate virtual environment

```

# Install dependencies

#### Compare Resumes

```bashpip install -r requirements.txt```bash# On Windows:

curl -X POST "http://localhost:8000/api/compare-resumes" \

     -F "files=@resume1.pdf" \```

     -F "files=@resume2.pdf" \

     -F "files=@resume3.pdf"# Create virtual environment.venv\Scripts\activate

```

## 🚀 Running the Application

## 🏗️ Project Structure

python -m venv .venv# On macOS/Linux:

```

├── app/### Development Mode

│   ├── main.py                 # FastAPI application setup and CORS configuration

│   ├── routers/source .venv/bin/activate

│   │   └── resume_router.py    # API route definitions and request handlers

│   ├── services/#### Using uv

│   │   ├── resume_parser.py    # Resume parsing logic (PDF/DOCX processing)

│   │   ├── question_generator.py # AI-powered interview question generation```bash# Activate virtual environment

│   │   ├── role_recommender.py # Job role recommendations and fit analysis

│   │   └── advanced_analyzer.py # Advanced analysis (scoring, personality, career)uv run uvicorn app.main:app --port 8000 --reload

│   └── models/

│       └── schemas.py          # Pydantic models and API response schemas```# On Windows:# Install dependencies

├── .github/

│   └── workflows/

│       └── tests.yml           # GitHub Actions CI/CD pipeline

├── .env.example               # Environment variables template#### Using pip.venv\Scripts\activatepip install -r requirements.txt

├── dockerfile                 # Docker container configuration

├── docker-compose.yml         # Docker Compose setup```bash

├── pyproject.toml            # Project configuration and dependencies

├── requirements.txt          # Python dependencies (legacy support)# Activate virtual environment first# On macOS/Linux:```

├── test_services.py          # Service testing and validation script

├── vercel.json               # Vercel deployment configuration.venv\Scripts\activate  # Windows

└── uv.lock                  # uv dependency lock file

```source .venv/bin/activate  # macOS/Linuxsource .venv/bin/activate



## 🔧 Configuration



### Environment Variablesuvicorn app.main:app --port 8000 --reload## 🚀 Running the Application



| Variable | Description | Required | Default |```

| -------- | ----------- | -------- | ------- |

| `GOOGLE_API_KEY` | Google Gemini API key for AI features | Yes | - |# Install dependencies

| `HOST` | Server host | No | localhost |

| `PORT` | Server port | No | 8000 |### Production Mode



### CORS Configurationpip install -r requirements.txt### Development Mode



The application accepts requests from:#### Using uv

- `https://jobpsych.vercel.app` (Production frontend)

- `https://hiredesk.vercel.app/` (HR Dashboard)```bash````

- `http://localhost:3000` (Development frontend)

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

## 🧪 Testing

```#### Using uv

### Run Service Tests



#### Using uv

```bash#### Using pip## 🚀 Running the Application

uv run python test_services.py

``````bash



#### Using pipuvicorn app.main:app --host 0.0.0.0 --port 8000```bash

```bash

python test_services.py```

```

### Development Modeuv run uvicorn app.main:app --port 8000 --reload

### Run Full Test Suite

### Using Docker

#### Using uv

```bash```

# Run all tests with coverage

uv run pytest test_services.py --cov=app --cov-report=term-missing#### Build and Run with Docker Compose



# Run specific test class```bash````bash

uv run pytest test_services.py::TestFastAPIApp -v

```docker-compose up --build



### API Testing```uv run uvicorn app.main:app --port 8000 --reload```bash



```bash

# Health check

curl http://localhost:8000/#### Build and Run with Docker```# Activate virtual environment first



# Detailed health check```bash

curl http://localhost:8000/health

# Build the image.venv\Scripts\activate  # Windows

# Get API documentation

curl http://localhost:8000/docsdocker build -t jobpsych-backend .

```

#### Using pipsource .venv/bin/activate  # macOS/Linux

## 🚀 Deployment

# Run the container

### Docker Deployment

docker run -p 8000:8000 --env-file .env jobpsych-backend

```bash

# Build the image```

docker build -t jobpsych-backend .

```bashuvicorn app.main:app --port 8000 --reload

# Run with environment variables

docker run -p 8000:8000 --env-file .env jobpsych-backend## 📖 API Documentation

```

# Activate virtual environment first```

### Docker Compose Deployment

Once the application is running, visit:

```bash

docker-compose up -d.venv\Scripts\activate  # Windows

```

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs

### Vercel Deployment

- **ReDoc Documentation**: http://localhost:8000/redocsource .venv/bin/activate  # macOS/Linux### Production Mode

The application includes Vercel configuration for serverless deployment:

- **Health Check**: http://localhost:8000/

```bash

# Install Vercel CLI- **Detailed Health Check**: http://localhost:8000/health

npm install -g vercel



# Deploy

vercel --prod## 🔌 API Endpointsuvicorn app.main:app --port 8000 --reload#### Using uv

```



## 🔄 CI/CD Pipeline

### Core Endpoints````

The project includes GitHub Actions for automated:



- **Testing**: Runs on every push and pull request

- **Code Quality**: Linting, type checking, and security scanning| Method | Endpoint | Description |```bash

- **Multi-Python Support**: Tests across Python 3.9, 3.10, and 3.11

| ------ | ------------------------- | ----------------------------------------------- |

### Pipeline Features

| `GET` | `/` | API information and health status |### Production Modeuv run uvicorn app.main:app --host 0.0.0.0 --port 8000

- Multi-version Python testing

- Automated testing with service validation| `GET` | `/health` | Detailed health check with API configuration |

- Code quality checks (ruff, mypy)

- Security vulnerability scanning| `POST` | `/api/analyze-resume` | Basic resume analysis with role recommendations |```

- Coverage reporting with Codecov

| `POST` | `/api/hiredesk-analyze` | Advanced HR analysis with fit assessment |

## 📦 Dependencies

| `POST` | `/api/batch-analyze` | Batch processing for multiple resumes |#### Using uv

### Core Dependencies

| `POST` | `/api/compare-resumes` | Compare and rank multiple resumes |

- **FastAPI**: Modern web framework for building APIs

- **Uvicorn**: ASGI server for FastAPI#### Using pip

- **Pydantic**: Data validation and serialization

- **Google Generative AI**: AI-powered text generation### Request Examples



### Document Processing````bash



- **PyPDF2**: PDF file processing#### Basic Resume Analysis

- **python-docx**: Word document processing

- **pdfplumber**: Advanced PDF text extraction```bashuv run uvicorn app.main:app --host 0.0.0.0 --port 8000```bash



### Utilitiescurl -X POST "http://localhost:8000/api/analyze-resume" \



- **python-dotenv**: Environment variable management     -F "file=@resume.pdf" \```uvicorn app.main:app --host 0.0.0.0 --port 8000

- **python-multipart**: File upload handling

- **slowapi**: Rate limiting     -F "target_role=Software Engineer" \



### Development Dependencies     -F "job_description=Develop and maintain web applications using Python, React, and cloud technologies..."````



- **pytest**: Testing framework```

- **pytest-cov**: Coverage reporting

- **ruff**: Fast Python linter and formatter#### Using pip

- **mypy**: Static type checking

- **safety**: Security vulnerability scanning#### Advanced HR Analysis



## 🤝 Contributing```bash### Using Docker



1. Fork the repositorycurl -X POST "http://localhost:8000/api/hiredesk-analyze" \

2. Create a feature branch: `git checkout -b feature-name`

3. Make your changes and add tests     -F "file=@resume.pdf" \```bash

4. Run tests: `uv run python test_services.py`

5. Commit your changes: `git commit -am 'Add new feature'`     -F "target_role=Product Manager" \

6. Push to the branch: `git push origin feature-name`

7. Submit a pull request     -F "job_description=Detailed job description with requirements..."uvicorn app.main:app --host 0.0.0.0 --port 8000#### Build and Run with Docker Compose



## 📝 License```



This project is licensed under the MIT License - see the LICENSE file for details.```



## 🆘 Troubleshooting#### Batch Analysis (Multiple Resumes)



### Common Issues```bash```bash



#### 1. "Failed to canonicalize script path" Errorcurl -X POST "http://localhost:8000/api/batch-analyze" \



```bash     -F "files=@resume1.pdf" \### Using Dockerdocker-compose up --build

# Try running with explicit app directory

uvicorn app.main:app --port 8000 --reload --app-dir .     -F "files=@resume2.pdf" \

```

     -F "target_role=Data Scientist" \```

#### 2. Missing Google API Key

     -F "job_description=Analyze data and build ML models..."

```bash

# Check your .env file```#### Build and Run with Docker Compose

cat .env

# Should contain: GOOGLE_API_KEY="your_key_here"

```

#### Compare Resumes#### Build and Run with Docker

#### 3. Port Already in Use

```bash

```bash

# Use a different portcurl -X POST "http://localhost:8000/api/compare-resumes" \````bash

uvicorn app.main:app --port 8001 --reload

```     -F "files=@resume1.pdf" \



#### 4. Docker Build Issues     -F "files=@resume2.pdf" \docker-compose up --build```bash



```bash     -F "files=@resume3.pdf"

# Clear Docker cache

docker system prune -a``````# Build the image



# Rebuild

docker-compose up --build --force-recreate

```## 🏗️ Project Structuredocker build -t jobpsych-backend .



#### 5. Import Errors



```bash```#### Build and Run with Docker

# Ensure you're in the correct directory

cd /path/to/AI-Resume-Analayzer_Backend├── app/



# Install dependencies│   ├── main.py                 # FastAPI application setup and CORS configuration# Run the container

uv sync

│   ├── routers/

# Run with proper Python path

PYTHONPATH=. uvicorn app.main:app --reload│   │   └── resume_router.py    # API route definitions and request handlers```bashdocker run -p 8000:8000 --env-file .env jobpsych-backend

```

│   ├── services/

## 📞 Support

│   │   ├── resume_parser.py    # Resume parsing logic (PDF/DOCX processing)# Build the image```

For support and questions:

│   │   ├── question_generator.py # AI-powered interview question generation

- Create an issue on GitHub

- Check the API documentation at `/docs`│   │   ├── role_recommender.py # Job role recommendations and fit analysisdocker build -t jobpsych-ai .

- Review the health endpoint at `/health`

│   │   └── advanced_analyzer.py # Advanced analysis (scoring, personality, career)

## 🔄 Recent Updates

│   └── models/## 📖 API Documentation

- **v2.0.0**: Complete rewrite with FastAPI, improved AI integration

- Added batch processing for multiple resumes│       └── schemas.py          # Pydantic models and API response schemas

- Enhanced resume comparison and ranking

- Added comprehensive scoring and personality analysis├── .github/# Run the container

- Improved Docker setup with uv package manager

- Added Vercel deployment support│   └── workflows/

- Comprehensive CI/CD pipeline with GitHub Actions

│       └── tests.yml           # GitHub Actions CI/CD pipelinedocker run -p 8000:8000 --env-file .env jobpsych-aiOnce the application is running, visit:

---

├── .env.example               # Environment variables template

**Built with ❤️ for HR professionals and job seekers**
├── dockerfile                 # Docker container configuration````

├── docker-compose.yml         # Docker Compose setup

├── pyproject.toml            # Project configuration and dependencies- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs

├── requirements.txt          # Python dependencies (legacy support)

├── test_services.py          # Service testing and validation script## 📖 API Documentation- **ReDoc Documentation**: http://localhost:8000/redoc

├── vercel.json               # Vercel deployment configuration

└── uv.lock                  # uv dependency lock file- **Health Check**: http://localhost:8000/

```

Once the application is running, visit:

## 🔧 Configuration

## 🔌 API Endpoints

### Environment Variables

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs

| Variable | Description | Required | Default |

| -------- | ----------- | -------- | ------- |- **ReDoc Documentation**: http://localhost:8000/redoc### Core Endpoints

| `GOOGLE_API_KEY` | Google Gemini API key for AI features | Yes | - |

| `HOST` | Server host | No | localhost |- **Health Check**: http://localhost:8000/health

| `PORT` | Server port | No | 8000 |

- **API Info**: http://localhost:8000/| Method | Endpoint | Description |

### CORS Configuration

| ------ | ------------------------- | ----------------------------------------------- |

The application accepts requests from:

- `https://jobpsych.vercel.app` (Production frontend)## 🔌 API Endpoints| `GET` | `/` | Health check and API information |

- `https://hiredesk.vercel.app/` (HR Dashboard)

- `http://localhost:3000` (Development frontend)| `GET` | `/health` | Detailed health check with API status |



## 🧪 Testing### Core Endpoints| `POST` | `/api/generate-questions` | Generate interview questions from resume |



### Run Service Tests| `POST` | `/api/analyze-resume` | Analyze resume and provide role recommendations |



#### Using uv| Method | Endpoint | Description || `POST` | `/api/hiredesk-analyze` | Advanced HR analysis with fit assessment |

```bash

uv run python test_services.py| ------ | ------------------------- | ----------------------------------------------- |

```

| `GET` | `/` | API information and health status |### Request Examples

#### Using pip

```bash| `GET` | `/health` | Detailed health check with API configuration |

python test_services.py

```| `POST` | `/api/analyze-resume` | Basic resume analysis with role recommendations |#### Generate Interview Questions



### Run Full Test Suite| `POST` | `/api/hiredesk-analyze` | Advanced HR analysis with fit assessment |



#### Using uv| `POST` | `/api/batch-analyze` | Batch processing for multiple resumes |```bash

```bash

# Run all tests with coverage| `POST` | `/api/compare-resumes` | Compare and rank multiple resumes |curl -X POST "http://localhost:8000/api/generate-questions" \

uv run pytest test_services.py --cov=app --cov-report=term-missing

     -F "file=@resume.pdf"

# Run specific test class

uv run pytest test_services.py::TestFastAPIApp -v### Request Examples```

```

#### Basic Resume Analysis#### Analyze Resume

### API Testing

`bash`bash

```bash

# Health checkcurl -X POST "http://localhost:8000/api/analyze-resume" \curl -X POST "http://localhost:8000/api/analyze-resume" \

curl http://localhost:8000/

     -F "file=@resume.pdf" \     -F "file=@resume.pdf" \

# Detailed health check

curl http://localhost:8000/health     -F "target_role=Software Engineer" \     -F "target_role=Software Engineer" \



# Get API documentation     -F "job_description=Develop and maintain web applications..."     -F "job_description=Job description text here..."

curl http://localhost:8000/docs

```````

## 🚀 Deployment

### Docker Deployment#### Advanced HR Analysis#### Advanced HR Analysis

````bash

# Build the image

docker build -t jobpsych-backend .```bash```bash



# Run with environment variablescurl -X POST "http://localhost:8000/api/hiredesk-analyze" \curl -X POST "http://localhost:8000/api/hiredesk-analyze" \

docker run -p 8000:8000 --env-file .env jobpsych-backend

```     -F "file=@resume.pdf" \     -F "file=@resume.pdf" \



### Docker Compose Deployment     -F "target_role=Product Manager" \     -F "target_role=Product Manager" \



```bash     -F "job_description=Detailed job description..."     -F "job_description=Detailed job description..."

docker-compose up -d

````

### Vercel Deployment#### Batch Analysis (Multiple Resumes)## 🏗️ Project Structure

The application includes Vercel configuration for serverless deployment:`bash`

`````bashcurl -X POST "http://localhost:8000/api/batch-analyze" \├── app/

# Install Vercel CLI

npm install -g vercel     -F "files=@resume1.pdf" \│   ├── main.py                 # FastAPI application setup



# Deploy     -F "files=@resume2.pdf" \│   ├── routers/

vercel --prod

```     -F "target_role=Data Scientist" \│   │   └── resume_router.py    # API route definitions



## 🔄 CI/CD Pipeline     -F "job_description=Analyze data and build ML models..."│   ├── services/



The project includes GitHub Actions for automated:````│ │   ├── resume_parser.py    # Resume parsing logic



- **Testing**: Runs on every push and pull request│   │   ├── question_generator.py # Interview question generation

- **Code Quality**: Linting, type checking, and security scanning

- **Multi-Python Support**: Tests across Python 3.9, 3.10, and 3.11#### Compare Resumes│   │   └── role_recommender.py # Job role recommendations



### Pipeline Features│   └── models/



- Multi-version Python testing```bash│       └── schemas.py          # Pydantic models and schemas

- Automated testing with service validation

- Code quality checks (ruff, mypy)curl -X POST "http://localhost:8000/api/compare-resumes" \├── .env.example               # Environment variables template

- Security vulnerability scanning

- Coverage reporting with Codecov     -F "files=@resume1.pdf" \├── dockerfile                 # Docker container configuration



## 📦 Dependencies     -F "files=@resume2.pdf" \├── docker-compose.yml         # Docker Compose setup



### Core Dependencies     -F "files=@resume3.pdf"├── pyproject.toml            # Project configuration



- **FastAPI**: Modern web framework for building APIs```├── requirements.txt          # Python dependencies

- **Uvicorn**: ASGI server for FastAPI

- **Pydantic**: Data validation and serialization└── test_services.py          # Service testing script

- **Google Generative AI**: AI-powered text generation

## 🏗️ Project Structure```

### Document Processing



- **PyPDF2**: PDF file processing

- **python-docx**: Word document processing```## 🔧 Configuration

- **pdfplumber**: Advanced PDF text extraction

├── app/

### Utilities

│   ├── main.py                 # FastAPI application setup and CORS### Environment Variables

- **python-dotenv**: Environment variable management

- **python-multipart**: File upload handling│   ├── routers/

- **slowapi**: Rate limiting

│   │   └── resume_router.py    # API route definitions and handlers| Variable         | Description                           | Required |

### Development Dependencies

│   ├── services/| ---------------- | ------------------------------------- | -------- |

- **pytest**: Testing framework

- **pytest-cov**: Coverage reporting│   │   ├── resume_parser.py    # Resume parsing logic (PDF/DOCX)| `GOOGLE_API_KEY` | Google Gemini API key for AI features | Yes      |

- **ruff**: Fast Python linter and formatter

- **mypy**: Static type checking│   │   ├── question_generator.py # Interview question generation| `HOST`           | Server host (default: localhost)      | No       |

- **safety**: Security vulnerability scanning

│   │   ├── role_recommender.py # Job role recommendations| `PORT`           | Server port (default: 8000)           | No       |

## 🤝 Contributing

│   │   └── advanced_analyzer.py # Advanced analysis (scoring, personality, career)

1. Fork the repository

2. Create a feature branch: `git checkout -b feature-name`│   └── models/### CORS Configuration

3. Make your changes and add tests

4. Run tests: `uv run python test_services.py`│       └── schemas.py          # Pydantic models and response schemas

5. Commit your changes: `git commit -am 'Add new feature'`

6. Push to the branch: `git push origin feature-name`├── .env.example               # Environment variables templateThe application is configured to accept requests from:

7. Submit a pull request

├── dockerfile                 # Docker container configuration

## 📝 License

├── docker-compose.yml         # Docker Compose setup- `https://jobpsych.vercel.app` (Production frontend)

This project is licensed under the MIT License - see the LICENSE file for details.

├── pyproject.toml            # Project configuration and dependencies- `http://localhost:3000` (Development frontend)

## 🆘 Troubleshooting

├── requirements.txt          # Python dependencies (legacy)

### Common Issues

├── test_services.py          # Service testing and validation script## 🧪 Testing

#### 1. "Failed to canonicalize script path" Error

├── vercel.json               # Vercel deployment configuration

```bash

# Try running with explicit app directory└── uv.lock                  # uv dependency lock file### Run Service Tests

uvicorn app.main:app --port 8000 --reload --app-dir .

`````

#### 2. Missing Google API Key````bash

````bash## 🔧 Configuration# Using uv

# Check your .env file

cat .envuv run python test_services.py

# Should contain: GOOGLE_API_KEY="your_key_here"

```### Environment Variables



#### 3. Port Already in Use# Using pip



```bash| Variable         | Description                           | Required | Default |python test_services.py

# Use a different port

uvicorn app.main:app --port 8001 --reload| ---------------- | ------------------------------------- | -------- | ------- |```

````

| `GOOGLE_API_KEY` | Google Gemini API key for AI features | Yes | - |

#### 4. Docker Build Issues

| `HOST` | Server host | No | localhost |### API Testing

````bash

# Clear Docker cache| `PORT`           | Server port                           | No       | 8000    |

docker system prune -a

```bash

# Rebuild

docker-compose up --build --force-recreate### CORS Configuration# Health check

````

curl http://localhost:8000/

#### 5. Import Errors

The application accepts requests from:

`````bash

# Ensure you're in the correct directory# Get API documentation

cd /path/to/AI-Resume-Analayzer_Backend

- `https://jobpsych.vercel.app` (Production frontend)curl http://localhost:8000/docs

# Install dependencies

uv sync- `https://hiredesk.vercel.app/` (HR Dashboard)```



# Run with proper Python path- `http://localhost:3000` (Development frontend)

PYTHONPATH=. uvicorn app.main:app --reload

```## 🚀 Deployment



## 📞 Support## 🧪 Testing



For support and questions:### Docker Deployment



- Create an issue on GitHub### Run Service Tests

- Check the API documentation at `/docs`

- Review the health endpoint at `/health````bash



## 🔄 Recent Updates```bash# Build the image



- **v2.0.0**: Complete rewrite with FastAPI, improved AI integration# Using uvdocker build -t jobpsych-backend .

- Added batch processing for multiple resumes

- Enhanced resume comparison and rankinguv run python test_services.py

- Added comprehensive scoring and personality analysis

- Improved Docker setup with uv package manager# Run with environment variables

- Added Vercel deployment support

- Comprehensive CI/CD pipeline with GitHub Actions# Using pipdocker run -p 8000:8000 --env-file .env jobpsych-backend



---python test_services.py```



**Built with ❤️ for HR professionals and job seekers**````

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

`````

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
