from fastapi import FastAPI
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
    version="1.0.0",
    description="Resume Analysis and Interview Question Generation API"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jobpsych.vercel.app" 
    ],
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router.router, prefix="/api", tags=["resume"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to JobPsych Resume Analysis API", 
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    api_key = os.getenv("GOOGLE_API_KEY")
    return {
        "status": "healthy", 
        "api_configured": bool(api_key),
        "environment": os.getenv("VERCEL_ENV", "development")
    }
