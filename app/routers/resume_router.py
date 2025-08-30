from fastapi import APIRouter, UploadFile, HTTPException, Request, Form
from app.services.resume_parser import ResumeParser
from app.services.role_recommender import RoleRecommender
from app.models.schemas import (
    ResumeAnalysisResponse, ResumeData, HiringCandidateResponse,
    JobDescriptionData, HiringCandidateAnalysis, SkillsRecommendation
)
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

        response = ResumeAnalysisResponse(
            resumeData=ResumeData(**resume_data),
            questions=questions,
            roleRecommendations=role_recommendations,
        )
        return {
            "fit_status": fit_status,
            "reasoning": reasoning,
            "resumeData": response.resumeData,
            "roleRecommendations": response.roleRecommendations,
            "questions": response.questions,
            "best_fit_role": best_fit_role_name
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


@router.post("/hiring-candidate", response_model=HiringCandidateResponse, status_code=status.HTTP_200_OK)
async def hiring_candidate_analysis(
    resume_file: UploadFile,
    job_description: str = Form(...),
    request: Request = None
):
    """
    Advanced hiring candidate analysis using AI-powered resume and job description parsing.

    This endpoint provides:
    - Comprehensive resume parsing with AI entity recognition
    - Job description analysis and requirements extraction
    - Similarity scoring between resume and job requirements
    - Skills gap analysis and personalized learning recommendations
    - Career path suggestions and development timeline
    """
    import time
    start_time = time.time()

    try:
        # Step 1: Parse the resume using our advanced parser
        from app.services.advanced_resume_parser import AdvancedResumeParser
        resume_parser = AdvancedResumeParser()
        resume_data = await resume_parser.parse(resume_file)

        # Convert to the expected format for compatibility
        formatted_resume_data = {
            'personalInfo': {
                'name': resume_data.get('name', 'Unknown'),
                'email': resume_data.get('email'),
                'phone': resume_data.get('phone'),
                'location': resume_data.get('location')
            },
            'workExperience': resume_data.get('experience', []),
            'education': resume_data.get('education', []),
            'skills': resume_data.get('skills', []),
            'highlights': resume_data.get('highlights', [])
        }

        # Step 2: Parse the job description
        from app.services.job_description_parser import JobDescriptionParser
        job_parser = JobDescriptionParser()
        job_data = job_parser.parse(job_description)

        # Step 3: Calculate similarity scores
        from app.services.similarity_scorer import SimilarityScorer
        similarity_scorer = SimilarityScorer()
        similarity_results = similarity_scorer.calculate_similarity(resume_data, job_data)

        # Step 4: Generate skills recommendations
        from app.services.skills_recommender import SkillsRecommender
        skills_recommender = SkillsRecommender()
        skills_recommendations = skills_recommender.recommend_skills(
            resume_data, job_data, similarity_results
        )

        # Step 5: Prepare the response
        processing_time = time.time() - start_time

        # Convert similarity analysis to expected format
        analysis_data = similarity_results.get('analysis', {})
        formatted_analysis = {
            'strengths': analysis_data.get('strengths', []),
            'weaknesses': analysis_data.get('weaknesses', []),
            'skill_gaps': analysis_data.get('skill_gaps', []),
            'experience_alignment': analysis_data.get('experience_alignment', ''),
            'overall_assessment': analysis_data.get('overall_assessment', '')
        }

        similarity_analysis = {
            'overall_score': similarity_results.get('overall_score', 0.0),
            'semantic_similarity': similarity_results.get('semantic_similarity', 0.0),
            'skills_match': similarity_results.get('skills_match', 0.0),
            'experience_match': similarity_results.get('experience_match', 0.0),
            'text_similarity': similarity_results.get('text_similarity', 0.0),
            'analysis': formatted_analysis,
            'recommendations': similarity_results.get('recommendations', [])
        }

        # Format skills recommendations
        formatted_skills_rec = {
            'skill_gaps': skills_recommendations.get('skill_gaps', []),
            'learning_plan': skills_recommendations.get('learning_plan', {}),
            'prioritized_skills': skills_recommendations.get('prioritized_skills', []),
            'timeline': skills_recommendations.get('timeline', {}),
            'estimated_time': skills_recommendations.get('estimated_time', ''),
            'career_path_suggestions': skills_recommendations.get('career_path_suggestions', [])
        }

        response = {
            'resume_data': formatted_resume_data,
            'job_data': job_data,
            'similarity_analysis': similarity_analysis,
            'skills_recommendations': formatted_skills_rec,
            'processing_time_seconds': round(processing_time, 2)
        }

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
        elif "transformers" in error_message.lower():
            error_message = "AI model loading error. Please try again or contact support."
        elif "torch" in error_message.lower():
            error_message = "Machine learning framework error. Please ensure all dependencies are installed."
        else:
            error_message = f"Analysis failed: {error_message}"

        raise HTTPException(status_code=500, detail=error_message)
