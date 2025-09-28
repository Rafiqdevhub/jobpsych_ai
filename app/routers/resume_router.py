from fastapi import APIRouter, UploadFile, HTTPException, Request, Form, File
from app.services.resume_parser import ResumeParser
from app.services.role_recommender import RoleRecommender
from app.models.schemas import (
    ResumeAnalysisResponse, ResumeData, Question, PersonalInfo
)
from fastapi import status
from pydantic import ValidationError
from typing import Optional, List
from app.services.advanced_analyzer import AdvancedAnalyzer


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
@router.post("/generate-questions", response_model=ResumeAnalysisResponse, status_code=status.HTTP_200_OK)
async def generate_questions(
    file: UploadFile,
    request: Request
):
    try:
        parser = ResumeParser()
        resume_data = await parser.parse(file)

        from app.services.question_generator import QuestionGenerator
        question_gen = QuestionGenerator()
        raw_questions = await question_gen.generate(resume_data)
        try:
            from app.models.schemas import Question
            questions = [Question(**q) if isinstance(q, dict) else q for q in raw_questions]
        except Exception:
            questions = raw_questions

        response = ResumeAnalysisResponse(
            resumeData=ResumeData(**resume_data),
            questions=questions,
            roleRecommendations=[],
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
    job_description: str = Form(...)
):
    try:
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
        return {
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
