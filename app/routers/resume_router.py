from fastapi import APIRouter, UploadFile, HTTPException, Depends, Request
from app.services.resume_parser import ResumeParser
from app.services.question_generator import QuestionGenerator
from app.services.rate_limiter import check_upload_rate_limit, rate_limiter, get_client_ip, get_user_id_from_request, is_premium_user
from app.models.schemas import ResumeAnalysisResponse
from app.models.schemas import ResumeData
from pydantic import ValidationError


router = APIRouter()

def format_validation_error(error: ValidationError) -> str:
    error_messages = []
    for err in error.errors():
        field = err["loc"][-1] if err["loc"] else "Unknown field"
        if isinstance(field, int):
            parent = err["loc"][-2] if len(err["loc"]) > 1 else "item"
            field = f"{parent} #{field + 1}"
        error_messages.append(f"{field}: {err['msg']}")
    return "Validation Error: " + "; ".join(error_messages)

@router.post("/analyze-resume", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    file: UploadFile,
    request: Request,
    _: None = Depends(check_upload_rate_limit) 
):
    try:
        parser = ResumeParser()
        resume_data = await parser.parse(file)

        generator = QuestionGenerator()
        questions = await generator.generate(resume_data)

        response = ResumeAnalysisResponse(
            resumeData=ResumeData(**resume_data),
            questions=questions
        )
        
        return response

    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=format_validation_error(e)
        )
    except Exception as e:
        error_message = str(e)
        if "PDF" in error_message:
            error_message = "Error reading PDF file. Please ensure it's not corrupted or password protected."
        elif "DOCX" in error_message:
            error_message = "Error reading DOCX file. Please ensure it's a valid Word document."
        raise HTTPException(status_code=500, detail=error_message)

@router.get("/rate-limit-status")
async def get_rate_limit_status(request: Request):
    client_ip = get_client_ip(request)
    user_id = get_user_id_from_request(request)
    
    # For local development, return unlimited status
    if client_ip == "127.0.0.1" or client_ip == "localhost" or client_ip.startswith("192.168.") or client_ip.startswith("10."):
        return {
            "ip": client_ip,
            "user_id": user_id if user_id else None,
            "limit": "unlimited",
            "remaining_uploads": "unlimited",
            "uploads_used": 0,
            "is_development": True,
            "tier": "development"
        }
    
    if user_id:
        # Authenticated user
        is_premium = is_premium_user(user_id)
        user_status = rate_limiter.get_user_remaining_requests(user_id, is_premium=is_premium)
        
        return {
            "ip": client_ip,
            "user_id": user_id,
            "authenticated": True,
            "limit": user_status["remaining"] if user_status["tier"] != "premium" else "unlimited",
            "limit_type": user_status["limit_type"],
            "remaining_uploads": user_status["remaining"],
            "uploads_used": user_status["used"],
            "is_development": False,
            "tier": user_status["tier"],
            "first_upload": user_status.get("first_upload"),
            "upgrade_url": "/api/upgrade-plan" if user_status["tier"] == "free" and user_status["remaining"] <= 0 else None
        }
    else:
        # Anonymous user
        ip_status = rate_limiter.get_ip_remaining_requests(client_ip)
        
        return {
            "ip": client_ip,
            "user_id": None,
            "authenticated": False,
            "limit": 2,
            "limit_type": ip_status["limit_type"],
            "remaining_uploads": ip_status["remaining"],
            "uploads_used": ip_status["used"],
            "is_development": False,
            "tier": ip_status["tier"],
            "first_upload": ip_status.get("first_upload"),
            "signup_url": "/auth/signup" if ip_status["remaining"] <= 0 else None,
            "upgrade_url": "/api/upgrade-plan"
        }

@router.get("/upgrade-plan")
async def upgrade_plan_info():
    """Endpoint with information about upgrading to premium plan"""
    return {
        "message": "Upgrade to Premium",
        "description": "Get unlimited resume analyses and advanced features",
        "limit_info": {
            "anonymous_limit": "2 analyses per location",
            "free_account_limit": "2 additional analyses after signup",
            "premium_limit": "Unlimited analyses"
        },
        "pricing": {
            "monthly": "$9.99",
            "yearly": "$99.99",
            "one_time": "$19.99"
        },
        "features": [
            "Unlimited resume uploads",
            "Priority processing",
            "Advanced question generation",
            "Resume improvement suggestions",
            "Interview coaching",
            "Export to PDF",
            "Resume comparison tool"
        ],
        "flow": {
            "step1": "Create account (if not authenticated)",
            "step2": "Choose subscription plan",
            "step3": "Complete payment",
            "step4": "Enjoy unlimited access"
        },
        "payment_url": "/api/payment"
    }

@router.get("/auth/signup-required")
async def signup_required_info():
    """Information shown when anonymous users hit their limit"""
    return {
        "message": "Create Account to Continue",
        "description": "You've used all 2 free analyses from this location. Create an account to get 2 more free analyses!",
        "benefits": [
            "Get 2 additional free resume analyses",
            "Save your analysis history",
            "Track your progress",
            "Access from any device"
        ],
        "next_steps": [
            "Create a free account",
            "Get 2 more free analyses",
            "Upgrade to premium for unlimited access"
        ],
        "signup_url": "/auth/signup",
        "upgrade_url": "/api/upgrade-plan"
    }
