from fastapi import APIRouter, UploadFile, HTTPException, Request, Form, File, Depends
from app.services.resume_parser import ResumeParser
from app.services.role_recommender import RoleRecommender
from app.services.question_generator import QuestionGenerator
from app.models.schemas import (
    ResumeAnalysisResponse, ResumeData, Question, PersonalInfo
)
from fastapi import status
from pydantic import ValidationError
from typing import Optional, List
from app.services.advanced_analyzer import AdvancedAnalyzer
from app.dependencies.auth import get_current_user, TokenData
from app.services.rate_limit_service import rate_limit_service
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter for this router
limiter = Limiter(key_func=get_remote_address)

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
@limiter.limit("5/day")  # 5 files per IP address per day
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
            questions=[],
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
    job_description: str = Form(...),
    current_user: TokenData = Depends(get_current_user)
):
    try:
        logger.info(f"Resume analysis request from user: {current_user.email}")

        # Check rate limit before processing
        rate_limit_status = await rate_limit_service.check_user_upload_limit(current_user.email)

        if not rate_limit_status["allowed"]:
            logger.warning(f"Rate limit exceeded for user: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "success": False,
                    "message": "Upload limit reached. You can upload up to 10 files per account.",
                    "error": "RATE_LIMIT_EXCEEDED",
                    "current_count": rate_limit_status["current_count"],
                    "limit": rate_limit_status["limit"],
                    "remaining": rate_limit_status["remaining"]
                }
            )

        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "message": "No file provided.",
                    "error": "VALIDATION_ERROR"
                }
            )

        if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "message": "Invalid file format. Please upload PDF, DOC, or DOCX files only.",
                    "error": "VALIDATION_ERROR"
                }
            )

        # Check file size (max 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "message": "File too large. Maximum size is 10MB.",
                    "error": "VALIDATION_ERROR"
                }
            )

        # Reset file pointer for processing
        await file.seek(0)
        parser = ResumeParser()
        resume_data = await parser.parse(file)

        recommender = RoleRecommender()
        # Instead of only analyzing fit for the provided target_role, recommend best-fit roles from resume
        role_recommendations = await recommender.recommend_roles(resume_data)
        # Pick the top recommended role as the best fit
        best_fit_role = role_recommendations[0] if role_recommendations else target_role
        # Always use string for role name
        if isinstance(best_fit_role, str):
            best_fit_role_name = best_fit_role
        elif hasattr(best_fit_role, 'roleName'):
            best_fit_role_name = best_fit_role.roleName
        else:
            best_fit_role_name = str(best_fit_role)

        # Analyze fit for the best-fit role
        fit_result = await recommender.analyze_role_fit(resume_data, best_fit_role_name, job_description)
        if isinstance(fit_result, dict):
            fit_status = "fit" if fit_result.get("fit", False) else "not fit"
            reasoning = fit_result.get("reasoning", "No reasoning provided.")
        else:
            fit_status = "not fit"
            reasoning = "Unexpected response format."

        # Generate questions for the best-fit role and general resume
        questions = []
        try:
            from app.services.question_generator import QuestionGenerator
            question_gen = QuestionGenerator()
            # General resume-based questions
            general_questions = await question_gen.generate(resume_data)
            # Role-specific questions if candidate is fit
            role_questions = []
            if fit_status == "fit":
                role_questions = await question_gen.generate_for_role(resume_data, best_fit_role_name, job_description)
            from app.models.schemas import Question
            # Combine and deduplicate questions
            all_questions = general_questions + role_questions
            seen = set()
            questions = []
            for q in all_questions:
                q_text = q["question"] if isinstance(q, dict) else getattr(q, "question", None)
                if q_text and q_text not in seen:
                    questions.append(Question(**q) if isinstance(q, dict) else q)
                    seen.add(q_text)
        except Exception:
            questions = []

        # Generate advanced analysis
        advanced_analyzer = AdvancedAnalyzer()
        resume_score = await advanced_analyzer.calculate_resume_score(resume_data)
        personality_insights = await advanced_analyzer.analyze_personality(resume_data)
        career_path = await advanced_analyzer.predict_career_path(resume_data)

        response = ResumeAnalysisResponse(
            resumeData=ResumeData(**resume_data),
            questions=questions,
            roleRecommendations=role_recommendations,
            resumeScore=resume_score,
            personalityInsights=personality_insights,
            careerPath=career_path
        )
        # Increment upload count after successful processing
        increment_success = await rate_limit_service.increment_user_upload(current_user.email)
        if not increment_success:
            logger.warning(f"Failed to increment upload count for user: {current_user.email}")

        logger.info(f"Resume analysis completed for user: {current_user.email}")

        return {
            "success": True,
            "fit_status": fit_status,
            "reasoning": reasoning,
            "resumeData": response.resumeData,
            "roleRecommendations": response.roleRecommendations,
            "questions": response.questions,
            "best_fit_role": best_fit_role_name,
            "resumeScore": response.resumeScore,
            "personalityInsights": response.personalityInsights,
            "careerPath": response.careerPath
        }
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "message": format_validation_error(e),
                "error": "VALIDATION_ERROR"
            }
        )
    except Exception as e:
        logger.error(f"Analysis failed for user {current_user.email}: {str(e)}")
        error_message = str(e)
        if "PDF" in error_message:
            error_message = "Error reading PDF file. Please ensure it's not corrupted or password protected."
        elif "DOCX" in error_message:
            error_message = "Error reading DOCX file. Please ensure it's a valid Word document."
        else:
            error_message = "Analysis failed. Please try again."
        
        raise HTTPException(
            status_code=500, 
            detail={
                "success": False,
                "message": error_message,
                "error": "SERVER_ERROR"
            }
        )


@router.post("/batch-analyze", response_model=List[ResumeAnalysisResponse])
async def batch_analyze_resumes(
    files: List[UploadFile],
    request: Request,
    target_role: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    """Analyze multiple resumes in batch"""
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 resumes allowed per batch")

    results = []

    for file in files:
        try:
            parser = ResumeParser()
            resume_data = await parser.parse(file)

            recommender = RoleRecommender()
            if target_role:
                role_recommendations = await recommender.analyze_role_fit(resume_data, target_role, job_description)
            else:
                role_recommendations = await recommender.recommend_roles(resume_data)

            # Generate questions
            question_gen = QuestionGenerator()
            raw_questions = await question_gen.generate(resume_data)
            questions = [Question(**q) if isinstance(q, dict) else q for q in raw_questions]

            # Advanced analysis
            advanced_analyzer = AdvancedAnalyzer()
            resume_score = await advanced_analyzer.calculate_resume_score(resume_data)
            personality_insights = await advanced_analyzer.analyze_personality(resume_data)
            career_path = await advanced_analyzer.predict_career_path(resume_data)

            response = ResumeAnalysisResponse(
                resumeData=ResumeData(**resume_data),
                questions=questions,
                roleRecommendations=role_recommendations,
                resumeScore=resume_score,
                personalityInsights=personality_insights,
                careerPath=career_path
            )
            results.append(response)

        except Exception as e:
            # For batch processing, continue with other files but log errors
            error_response = ResumeAnalysisResponse(
                resumeData=ResumeData(
                    personalInfo=PersonalInfo(name=f"Error processing {file.filename}"),
                    workExperience=[],
                    education=[],
                    skills=[],
                    highlights=[f"Error: {str(e)}"]
                ),
                questions=[],
                roleRecommendations=[]
            )
            results.append(error_response)

    return results

@router.post("/compare-resumes")
async def compare_resumes(
    files: List[UploadFile] = File(...),
    request: Request = None
):
    """Compare multiple resumes and rank them"""
    if len(files) < 2 or len(files) > 5:
        raise HTTPException(status_code=400, detail="Provide 2-5 resumes for comparison")

    candidates = []

    for file in files:
        try:
            parser = ResumeParser()
            resume_data = await parser.parse(file)

            advanced_analyzer = AdvancedAnalyzer()
            score = await advanced_analyzer.calculate_resume_score(resume_data)

            candidates.append({
                "filename": file.filename,
                "resumeData": ResumeData(**resume_data),
                "score": score.overall_score,
                "strengths": score.strengths,
                "weaknesses": score.weaknesses
            })

        except Exception as e:
            candidates.append({
                "filename": file.filename,
                "error": str(e),
                "score": 0
            })

    # Rank candidates by score
    ranked_candidates = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)

    return {
        "comparison_summary": {
            "total_candidates": len(candidates),
            "highest_score": max([c.get("score", 0) for c in candidates]),
            "average_score": sum([c.get("score", 0) for c in candidates]) / len(candidates)
        },
        "ranked_candidates": ranked_candidates,
        "recommendations": [
            "Consider top 3 candidates for interviews",
            "Review candidates with scores > 80 for immediate consideration",
            "Candidates with scores < 60 may need additional training"
        ]
    }
