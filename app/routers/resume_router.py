from fastapi import APIRouter, UploadFile, HTTPException, Depends, Request
from app.services.resume_parser import ResumeParser
from app.services.question_generator import QuestionGenerator
from app.services.rate_limiter import check_upload_rate_limit, rate_limiter, get_client_ip
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
    status = rate_limiter.get_remaining_requests(client_ip, max_requests=2)
    
    return {
        "ip": client_ip,
        "daily_limit": 2,
        "remaining_uploads": status["remaining"],
        "uploads_used": status["used"],
        "reset_time": status["reset_time"]
    }
