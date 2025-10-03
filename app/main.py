from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

try:
    from dotenv import load_dotenv
    load_dotenv() 
except ImportError:
    pass  

from app.routers import resume_router

# Initialize global rate limiter for slowapi
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="JobPsych ai",
    version="2.0.0",
    description="AI-powered resume analysis and job role recommendation service and HR interview question generation for HR professionals.",
)

# Add rate limiting state to app
app.state.limiter = limiter

# Add global rate limit exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jobpsych.vercel.app",
        "https://hiredesk.vercel.app", 
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,  # Keep True for auth endpoints 
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=[
        "Accept",
        "Accept-Encoding",
        "Accept-Language", 
        "Authorization",
        "Content-Language",
        "Content-Type",
        "DNT",
        "Origin",
        "User-Agent",
        "X-Requested-With",
        "X-CSRF-Token",
        "X-CSRFToken",
    ],
    expose_headers=["*"],
)

app.include_router(resume_router.router, prefix="/api", tags=["resume"])

# Add CORS test endpoint
@app.get("/api/cors-test")
async def cors_test():
    return {
        "message": "CORS is working!",
        "status": "success",
        "timestamp": "2025-10-02T00:00:00Z"
    }

@app.get("/")
async def root():
    return {
        "app_name": "JobPsych AI - Role Suggestion and HR Intelligence Platform",
        "message": "AI-Powered Resume Analysis & Job Role Recommendation Service",
        "status": "running",
        "version": "2.0.0",
        "description": (
            "JobPsych AI is a comprehensive HR intelligence platform that leverages Google Gemini AI "
            "to provide advanced resume analysis, job role recommendations, and interview question generation. "
            "Perfect for HR professionals, recruiters, and hiring managers looking to streamline their recruitment process."
        ),
        "core_capabilities": {
            "resume_parsing": {
                "description": "Extract structured data from PDF and DOCX resume files",
                "supported_formats": ["PDF", "DOCX", "DOC"],
                "extracted_data": [
                    "Personal information and contact details",
                    "Professional experience with dates and descriptions",
                    "Educational background and certifications",
                    "Technical and soft skills",
                    "Projects and achievements"
                ]
            },
            "ai_analysis": {
                "description": "Advanced AI-powered analysis using Google Gemini 2.5 Flash",
                "features": [
                    "Job role recommendations with match percentages (0-100%)",
                    "Comprehensive resume scoring and breakdown",
                    "Personality insights and work style analysis",
                    "Career path prediction and advancement timeline",
                    "Skill gap analysis with learning recommendations",
                    "Role fit assessment for specific job positions"
                ]
            },
            "interview_assistance": {
                "description": "Generate tailored interview questions for HR professionals",
                "question_types": [
                    "Technical questions based on candidate skills",
                    "Behavioral questions aligned with work experience",
                    "Experience-based questions from resume highlights",
                    "Role-specific questions for target positions"
                ]
            },
            "batch_processing": {
                "description": "Analyze multiple candidates simultaneously",
                "capabilities": [
                    "Process up to 10 resumes in a single request",
                    "Compare and rank multiple candidates",
                    "Generate comparative analysis reports",
                    "Bulk interview question generation"
                ]
            }
        },
        "api_endpoints": {
            "analyze_resume": {
                "endpoint": "/api/analyze-resume",
                "method": "POST",
                "description": "Basic resume analysis with role recommendations",
                "rate_limit": "5 requests per day per IP address",
                "required_params": ["file (PDF/DOCX)"],
                "optional_params": ["target_role", "job_description"]
            },
            "hiredesk_analyze": {
                "endpoint": "/api/hiredesk-analyze",
                "method": "POST",
                "description": "Advanced HR analysis with complete assessment suite",
                "required_params": ["file", "target_role", "job_description"],
                "features": ["Complete analysis", "Interview questions", "Personality insights"]
            },
            "batch_analyze": {
                "endpoint": "/api/batch-analyze",
                "method": "POST",
                "description": "Batch processing for multiple resumes (max 10)",
                "required_params": ["files[]"],
                "optional_params": ["target_role", "job_description"]
            },
            "compare_resumes": {
                "endpoint": "/api/compare-resumes",
                "method": "POST",
                "description": "Compare and rank multiple candidates",
                "required_params": ["files[]"],
                "output": "Ranked comparison with detailed analysis"
            }
        },
        "workflow": {
            "step_1": " Upload resume files (PDF/DOCX format)",
            "step_2": " Optionally specify target role and job description",
            "step_3": " AI extracts and analyzes candidate data using Google Gemini",
            "step_4": " Receive comprehensive analysis with role recommendations",
            "step_5": " Get tailored interview questions for HR screening",
            "step_6": " Review personality insights and career predictions",
            "step_7": " Compare multiple candidates for final selection"
        },
        "technical_features": [
            " FastAPI framework with automatic OpenAPI documentation",
            " Google Gemini 2.5 Flash AI integration",
            " Comprehensive resume scoring (0-100 scale)",
            " Role fit analysis with percentage matching",
            " AI-powered personality and work style assessment",
            " Career path prediction with timeline forecasting",
            " Rate limiting for production stability (5 requests/day per IP)",
            "Batch processing for HR efficiency",
            " Resume comparison and candidate ranking",
            " Automated interview question generation"
        ],
        "use_cases": [
            "HR departments screening job applications",
            "Recruiters matching candidates to job roles",
            "Hiring managers preparing for interviews",
            "Talent acquisition teams analyzing candidate pools",
            "Career counselors providing job recommendations",
            "Companies building talent pipelines"
        ],
        "supported_formats": {
            "input": ["PDF", "DOCX", "DOC"],
            "output": ["JSON", "Structured API responses"],
            "max_file_size": "10MB per file",
            "batch_limit": "10 files maximum"
        },
        "example_analysis_output": {
            "resume_score": 85,
            "top_role_match": {
                "role": "Senior Software Engineer",
                "match_percentage": 92,
                "reasoning": "Strong technical skills in Python, React, and cloud technologies align perfectly with requirements"
            },
            "personality_insights": {
                "work_style": "Collaborative and analytical",
                "strengths": ["Problem-solving", "Team leadership", "Technical expertise"]
            },
            "career_prediction": {
                "next_role": "Tech Lead / Engineering Manager",
                "timeline": "1-2 years",
                "growth_path": "Technical → Leadership track"
            },
            "sample_interview_questions": [
                "Describe your experience with microservices architecture",
                "How do you handle technical debt in legacy systems?",
                "Tell me about a challenging team project you led"
            ]
        },
        "getting_started": {
            "step_1": "Visit the API documentation at /docs",
            "step_2": "Test endpoints using the interactive Swagger UI",
            "step_3": "Upload a sample resume to see the analysis in action",
            "step_4": "Integrate with your HR systems using the RESTful API"
        },
        "documentation": " Interactive API docs available at /docs",
        "health_check": "System health status available at /health",
        "rate_limiting": "Protected endpoints: 5 requests per day per IP for /analyze-resume",
        "ai_powered_by": "Google Gemini 2.5 Flash",
        "support": "Built for HR professionals and recruitment teams worldwide"
    }

@app.get("/health")
async def health_check():
    api_key = os.getenv("GOOGLE_API_KEY")
    return {
        "status": "healthy", 
        "api_configured": bool(api_key),
        "environment": os.getenv("VERCEL_ENV", "development")
    }
