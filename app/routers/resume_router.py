from fastapi import APIRouter, UploadFile, HTTPException
from app.services.resume_parser import ResumeParser
from app.services.question_generator import QuestionGenerator
from app.models.schemas import ResumeAnalysisResponse
from app.models.schemas import ResumeData
from pydantic import ValidationError
from typing import Dict, Any

router = APIRouter()

def format_validation_error(error: ValidationError) -> str:
    """Format validation error into a user-friendly message."""
    error_messages = []
    for err in error.errors():
        field = err["loc"][-1] if err["loc"] else "Unknown field"
        if isinstance(field, int):
            # Handle array index errors more gracefully
            parent = err["loc"][-2] if len(err["loc"]) > 1 else "item"
            field = f"{parent} #{field + 1}"
        error_messages.append(f"{field}: {err['msg']}")
    return "Validation Error: " + "; ".join(error_messages)

@router.post("/analyze-resume", response_model=ResumeAnalysisResponse)
async def analyze_resume(file: UploadFile):
    try:
        # Parse resume
        parser = ResumeParser()
        resume_data = await parser.parse(file)

        # Generate questions
        generator = QuestionGenerator()
        questions = await generator.generate(resume_data)

        # Create response with proper typing
        return ResumeAnalysisResponse(
            resumeData=ResumeData(**resume_data),
            questions=questions
        )

    except ValidationError as e:
        # Handle validation errors with user-friendly messages
        raise HTTPException(
            status_code=422,
            detail=format_validation_error(e)
        )
    except Exception as e:
        # Handle other errors
        error_message = str(e)
        if "PDF" in error_message:
            error_message = "Error reading PDF file. Please ensure it's not corrupted or password protected."
        elif "DOCX" in error_message:
            error_message = "Error reading DOCX file. Please ensure it's a valid Word document."
        raise HTTPException(status_code=500, detail=error_message)
