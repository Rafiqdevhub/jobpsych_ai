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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jobpsych.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400
)

app.include_router(resume_router.router, prefix="/api", tags=["resume"])

@app.post("/api/analyze-resume")
async def analyze_resume(file: UploadFile) -> ResumeAnalysisResponse:
    try:
        resume_data = await ResumeParser().parse(file)
        questions = await QuestionGenerator().generate(resume_data)
        return ResumeAnalysisResponse(resumeData=resume_data, questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "JobPsych API"}
