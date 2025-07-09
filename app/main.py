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
async def root(request: Request):
    from app.services.rate_limiter import get_client_ip, get_user_id_from_request
    
    client_ip = get_client_ip(request)
    user_id = get_user_id_from_request(request)
    is_local = client_ip == "127.0.0.1" or client_ip == "localhost" or client_ip.startswith("192.168.") or client_ip.startswith("10.")
    
    return {
        "message": "Welcome to JobPsych Resume Analysis API", 
        "status": "running",
        "version": "1.0.0",
        "rate_limits": {
            "anonymous_users": {
                "limit": "unlimited" if is_local else 2,
                "limit_type": "per IP address",
                "description": "2 free analyses per location"
            },
            "authenticated_users": {
                "free_tier": "2 additional analyses after signup",
                "premium_tier": "unlimited"
            }
        },
        "authentication": {
            "required": False,
            "benefits": "Get additional free analyses and save your history"
        },
        "endpoints": {
            "analyze": "/api/analyze-resume",
            "rate_status": "/api/rate-limit-status",
            "signup_info": "/api/auth/signup-required",
            "upgrade_info": "/api/upgrade-plan"
        },
        "is_development_mode": is_local
    }

@app.get("/health")
async def health_check():
    api_key = os.getenv("GOOGLE_API_KEY")
    return {
        "status": "healthy", 
        "api_configured": bool(api_key),
        "environment": os.getenv("VERCEL_ENV", "development")
    }
