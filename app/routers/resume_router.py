from fastapi import APIRouter, UploadFile, HTTPException, Request, Form
from app.services.resume_parser import ResumeParser
from app.services.role_recommender import RoleRecommender
from app.models.schemas import ResumeAnalysisResponse, ResumeData
from fastapi import status
from pydantic import ValidationError
from typing import Optional


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
    target_role: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    try:
        # Parse the resume
        parser = ResumeParser()
        resume_data = await parser.parse(file)

        # Generate role recommendations with target role analysis
        recommender = RoleRecommender()
        if target_role:
            # Analyze fit for target role + provide alternatives
            role_recommendations = await recommender.analyze_role_fit(resume_data, target_role, job_description)
        else:
            # General role recommendations
            role_recommendations = await recommender.recommend_roles(resume_data)

        # Create response with analysis results (no questions)
        response = ResumeAnalysisResponse(
            resumeData=ResumeData(**resume_data),
            questions=[],  # Empty questions array
            roleRecommendations=role_recommendations
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


@router.post("/hiredesk-analyze", response_model=ResumeAnalysisResponse, status_code=status.HTTP_200_OK)
async def hiredesk_analyze(
    file: UploadFile,
    request: Request,
    target_role: str = Form(...),
    job_description: Optional[str] = Form(None)
):
    try:
        parser = ResumeParser()
        resume_data = await parser.parse(file)

        recommender = RoleRecommender()
        # Analyze fit for the specified role
        fit_result = await recommender.analyze_role_fit(resume_data, target_role, job_description)
        # fit_result should contain: {"fit": True/False, "reasoning": str, "roleRecommendations": list}
        if isinstance(fit_result, dict):
            fit_status = "fit" if fit_result.get("fit", False) else "not fit"
            reasoning = fit_result.get("reasoning", "No reasoning provided.")
            role_recommendations = fit_result.get("roleRecommendations", [])
        else:
            fit_status = "not fit"
            reasoning = "Unexpected response format."
            role_recommendations = []

        response = ResumeAnalysisResponse(
            resumeData=ResumeData(**resume_data),
            questions=[],
            roleRecommendations=role_recommendations,
        )
        return {
            "fit_status": fit_status,
            "reasoning": reasoning,
            "resumeData": response.resumeData,
            "roleRecommendations": response.roleRecommendations,
            "questions": response.questions
        }
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
