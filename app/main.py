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
    version="3.0.0",
    description="AI-powered resume analysis and job role recommendation service and HR interview question generation for HR professionals.",
)

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
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"], 
    expose_headers=["*"],
)

app.include_router(resume_router.router, prefix="/api", tags=["resume"])



@app.get("/")
async def root():
    return {
        "app_name": "JobPsych AI - Role Suggestion and HR Intelligence Platform",
        "message": "AI-Powered Resume Analysis & Job Role Recommendation Service",
        "status": "running",
        "version": "3.0.0",
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
                    "Process up to 5 resumes per batch",
                    "Compare and rank multiple candidates",
                    "Generate comparative analysis reports",
                    "Bulk interview question generation",
                    "Each file counted toward account limit"
                ]
            }
        },
        "api_endpoints": {
            "analyze_resume": {
                "endpoint": "/api/analyze-resume",
                "method": "POST",
                "description": "Basic resume analysis with role recommendations",
                "rate_limit": "5 requests per day per IP address",
                "authentication": "Not required",
                "required_params": ["file (PDF/DOCX)"],
                "optional_params": ["target_role", "job_description"],
                "file_counting": "Each file increments filesUploaded by 1"
            },
            "hiredesk_analyze": {
                "endpoint": "/api/hiredesk-analyze",
                "method": "POST",
                "description": "Advanced HR analysis with complete assessment suite",
                "authentication": "Required (JWT token)",
                "rate_limit": "Part of 10 files per account limit",
                "required_params": ["file", "target_role", "job_description"],
                "features": ["Complete analysis", "Interview questions", "Personality insights"],
                "file_counting": "Each file increments filesUploaded by 1"
            },
            "batch_analyze_resumes": {
                "endpoint": "/api/batch-analyze-resumes",
                "method": "POST",
                "description": "Batch processing for multiple resumes",
                "authentication": "Required (JWT token)",
                "rate_limit": "Maximum 5 files per batch, 10 files total per account",
                "required_params": ["files[] (2-5 files)"],
                "optional_params": ["target_role", "job_description"],
                "file_counting": "Each successful file increments filesUploaded by actual count",
                "counter_tracking": "Increments batch_analysis by 1 + filesUploaded by N files"
            },
            "compare_resumes": {
                "endpoint": "/api/compare-resumes",
                "method": "POST",
                "description": "Compare and rank multiple candidates",
                "authentication": "Required (JWT token)",
                "rate_limit": "Maximum 5 files per comparison, 10 files total per account",
                "required_params": ["files[] (2-5 resumes)"],
                "output": "Ranked comparison with detailed analysis",
                "file_counting": "Each successful file increments filesUploaded by actual count",
                "counter_tracking": "Increments compare_resumes by 1 + filesUploaded by N files"
            }
        },
        "authentication": {
            "description": "JWT token-based authentication for protected endpoints",
            "protected_endpoints": [
                "/api/hiredesk-analyze",
                "/api/batch-analyze-resumes",
                "/api/compare-resumes"
            ],
            "public_endpoints": [
                "/api/analyze-resume"
            ],
            "how_to_authenticate": "Include 'Authorization: Bearer YOUR_JWT_TOKEN' in request headers"
        },
        "rate_limiting": {
            "free_tier": {
                "total_files_per_account": 10,
                "files_per_batch": 5,
                "files_per_comparison": 5,
                "warning_threshold": 8,
                "description": "Free users can process up to 10 files total across all operations"
            },
            "file_counting": {
                "description": "All files are counted exactly as they are processed",
                "examples": [
                    "Single file upload via /analyze-resume: +1 file",
                    "Batch of 3 files via /batch-analyze-resumes: +3 files + 1 batch operation",
                    "Comparison of 4 resumes via /compare-resumes: +4 files + 1 comparison operation",
                    "Total in scenario: 8 files used (80% of 10-file limit)"
                ]
            },
            "counters_tracked": {
                "filesUploaded": "Total count of all files processed across all endpoints",
                "batch_analysis": "Number of batch analysis operations performed",
                "compare_resumes": "Number of comparison operations performed"
            },
            "rate_limit_headers": [
                "/api/analyze-resume: 5 requests per day per IP (slowapi rate limiter)"
            ]
        },
        "workflow": {
            "step_1": "Upload resume files (PDF/DOCX format)",
            "step_2": "Optionally specify target role and job description",
            "step_3": "AI extracts and analyzes candidate data using Google Gemini",
            "step_4": "Receive comprehensive analysis with role recommendations",
            "step_5": "Get tailored interview questions for HR screening",
            "step_6": "Review personality insights and career predictions",
            "step_7": "Compare multiple candidates for final selection",
            "step_8": "Track usage: Each file counts toward 10-file account limit"
        },
        "technical_features": [
            "FastAPI framework with automatic OpenAPI documentation",
            "Google Gemini 2.5 Flash AI integration",
            "JWT token-based authentication for protected endpoints",
            "Comprehensive resume scoring (0-100 scale)",
            "Role fit analysis with percentage matching",
            "AI-powered personality and work style assessment",
            "Career path prediction with timeline forecasting",
            "Rate limiting with exact file counting",
            "Batch processing for HR efficiency (max 5 files per batch)",
            "Resume comparison and candidate ranking",
            "Automated interview question generation",
            "Express.js backend integration for counter tracking",
            "Fail-open strategy for graceful error handling"
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
            "batch_limit": "5 files maximum per batch",
            "account_limit": "10 files maximum per account"
        },
        "upgrade_prompts": {
            "warning_threshold": "Shown when user reaches 8 of 10 files (80%)",
            "limit_reached": "Shown when user reaches 10 of 10 files (100%)",
            "call_to_action": "Upgrade to analyze unlimited resumes"
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
            "usage_stats": {
                "files_uploaded": 8,
                "batches_processed": 2,
                "comparisons_completed": 1,
                "files_remaining": 2,
                "approaching_limit": True
            },
            "sample_interview_questions": [
                "Describe your experience with microservices architecture",
                "How do you handle technical debt in legacy systems?",
                "Tell me about a challenging team project you led"
            ]
        },
        "getting_started": {
            "step_1": "Visit the API documentation at /docs",
            "step_2": "Test public endpoints using the interactive Swagger UI",
            "step_3": "For authenticated endpoints, obtain JWT token from authentication service",
            "step_4": "Upload a sample resume to see the analysis in action",
            "step_5": "Monitor your file usage in the response stats",
            "step_6": "Integrate with your HR systems using the RESTful API"
        },
        "documentation": "Interactive API docs available at /docs (includes all updated endpoints and rate limits)",
        "health_check": "System health status available at /health",
        "backend_integration": {
            "service": "Express.js authentication and counter tracking service",
            "endpoints": [
                "GET /user-uploads/:email - Retrieve usage stats",
                "POST /increment-upload - Increment filesUploaded counter",
                "POST /increment-batch-analysis - Increment batch counter",
                "POST /increment-compare-resumes - Increment comparison counter"
            ],
            "tracking": "All counters sync with Express.js backend for accurate user tracking"
        },
        "ai_powered_by": "Google Gemini 2.5 Flash",
        "support": "Built for HR professionals and recruitment teams worldwide",
        "features_summary": {
            "authentication": "JWT token-based for secure access",
            "rate_limiting": "10 files per account, exact counting per file",
            "file_processing": "Exact count of all files, successful and total",
            "batch_operations": "Up to 5 files per batch with individual file tracking",
            "comparisons": "Compare 2-5 resumes with file count tracking",
            "counters": "Separate tracking for uploads, batches, and comparisons",
            "upgrade_system": "Warning at 80%, blocking at 100% with upgrade prompts"
        }
    }

@app.get("/health")
async def health_check():
    api_key = os.getenv("GOOGLE_API_KEY")
    return {
        "status": "healthy", 
        "api_configured": bool(api_key),
        "environment": os.getenv("VERCEL_ENV", "development")
    }
