from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
from dotenv import load_dotenv
from .services.resume_parser import ResumeParser
from .services.question_generator import QuestionGenerator
from .models.schemas import ResumeAnalysisResponse
from app.routers import resume_router

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI(title="JobPsych Backend", version="1.0.0")

origins = [
    "https://jobpsych.vercel.app",
]

print(f"Configured CORS origins: {origins}")  # Debug logging

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

app.include_router(resume_router.router, prefix="/api", tags=["resume"])

@app.post("/api/analyze-resume")
async def analyze_resume(file: UploadFile) -> ResumeAnalysisResponse:
    try:
        # Initialize services
        resume_parser = ResumeParser()
        question_generator = QuestionGenerator()

        # Parse resume
        resume_data = await resume_parser.parse(file)

        # Generate questions
        questions = await question_generator.generate(resume_data)

        return ResumeAnalysisResponse(
            resumeData=resume_data,
            questions=questions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to Resume Analysis API"}
