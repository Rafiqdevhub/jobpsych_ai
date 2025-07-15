from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os

try:
    from dotenv import load_dotenv
    load_dotenv() 
except ImportError:
    pass  

from app.routers import resume_router

app = FastAPI(
    title="JobPsych Backend", 
    version="2.0.0",
    description="AI-powered resume analysis and job role recommendation service and HR interview question generation for HR professionals.",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jobpsych.vercel.app",
    ],
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router.router, prefix="/api", tags=["resume"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to JobPsych: AI-Powered Role Suggestion and Resume Analysis API",
        "status": "running",
        "version": "2.0.0",
        "description": (
            "Upload a candidate's resume along with a target job role and description. "
            "The system will extract resume information, analyze fit for the specified role, "
            "and suggest the best-matching job roles for the candidate, including detailed reasoning and skill gap analysis."
        ),
        "features": [
            "Resume parsing and information extraction (PDF, DOCX)",
            "Role fit analysis for candidate and job description",
            "AI-powered job role suggestions with match percentage",
            "Skill gap and reasoning for each recommendation",
            "HR interview question generation (coming soon)"
        ],
        "workflow": [
            "1. Upload resume (PDF/DOCX) and specify target role & job description.",
            "2. System extracts candidate data and analyzes fit for the target role.",
            "3. Get top job role suggestions, match scores, and skill gap insights."
        ],
        "endpoints": {
            "analyze": "/api/analyze-resume",
            "health": "/health"
        },
        "example_request": {
            "file": "<resume.pdf>",
            "target_role": "Data Scientist",
            "job_description": "Analyze data, build ML models, communicate insights..."
        },
        "example_response": {
            "roleRecommendations": [
                {
                    "roleName": "Data Scientist",
                    "matchPercentage": 87,
                    "reasoning": "Strong background in Python, statistics, and ML projects.",
                    "requiredSkills": ["Python", "Machine Learning", "Statistics"],
                    "missingSkills": ["Deep Learning"]
                },
                {
                    "roleName": "Data Analyst",
                    "matchPercentage": 80,
                    "reasoning": "Excellent data analysis and visualization skills.",
                    "requiredSkills": ["SQL", "Data Visualization"],
                    "missingSkills": ["Big Data Tools"]
                }
            ]
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
