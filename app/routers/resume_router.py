from fastapi import APIRouter, UploadFile, HTTPException, Request, Form, File, Depends, status
from pydantic import ValidationError
from typing import Optional, List
import logging
from app.services.resume_parser import ResumeParser
from app.services.advanced_analyzer import AdvancedAnalyzer
from app.services.rate_limit_service import rate_limit_service
from app.services.prompts import (
    AnalyzeResumeService,
    HiredeskService,
    BatchAnalyzeService,
    CompareResumesService
)
from app.models.schemas import ResumeAnalysisResponse, ResumeData, Question
from app.dependencies.auth import get_current_user, TokenData
from slowapi import Limiter
from slowapi.util import get_remote_address

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
        analyze_service = AnalyzeResumeService()
        if target_role:
            # Analyze fit for target role + provide alternatives
            role_recommendations = await analyze_service.analyze_role_fit(resume_data, target_role, job_description)
        else:
            # General role recommendations
            role_recommendations = await analyze_service.generate(resume_data)
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
    target_role: str = Form(...),
    job_description: str = Form(...),
    current_user: TokenData = Depends(get_current_user)
):
    try:
        # Check rate limit before processing
        rate_limit_status = await rate_limit_service.check_user_upload_limit(current_user.email)

        if not rate_limit_status["allowed"]:
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

        # Initialize hiredesk service for comprehensive analysis
        hiredesk_service = HiredeskService()
        
        # Get role recommendations
        role_recommendations = await hiredesk_service.generate(resume_data)
        
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
        fit_result = await hiredesk_service.analyze_role_fit(resume_data, best_fit_role_name, job_description)
        if isinstance(fit_result, dict):
            fit_status = "fit" if fit_result.get("fit", False) else "not fit"
            reasoning = fit_result.get("reasoning", "No reasoning provided.")
        else:
            fit_status = "fit" if fit_result else "not fit"
            reasoning = "Analyzed based on resume data."

        # Generate questions for the best-fit role and general resume
        questions = []
        try:
            # General resume-based questions
            general_questions_data = await hiredesk_service.generate_interview_questions(resume_data)
            
            # Role-specific questions if candidate is fit
            role_questions_data = []
            if fit_status == "fit":
                role_questions_data = await hiredesk_service.generate_interview_questions(
                    resume_data, best_fit_role_name, job_description
                )
            
            # Combine and deduplicate questions
            all_questions = general_questions_data + role_questions_data
            seen = set()
            questions = []
            for q in all_questions:
                q_text = q.get("question") if isinstance(q, dict) else getattr(q, "question", None)
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
        # Increment filesUploaded counter for single file upload
        await rate_limit_service.increment_files_uploaded(current_user.email, 1)

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


@router.post("/batch-analyze", response_model=dict, status_code=status.HTTP_200_OK)
async def batch_analyze_resumes(
    files: List[UploadFile],
    request: Request,
    target_role: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Analyze multiple resumes in batch with rate limiting
    
    Requirements:
    - Authentication required (JWT token)
    - Maximum 5 files per batch
    - Maximum 10 files per account (free tier)
    - Tracks: batch_analysis counter and filesUploaded counter
    
    Response includes batch summary and updated usage statistics
    """
    try:
        user_email = current_user.email

        # ========== STEP 1: VALIDATE BATCH SIZE ==========
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "message": "No files provided",
                    "error": "VALIDATION_ERROR"
                }
            )

        if len(files) > rate_limit_service.batch_size_limit:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "message": f"Maximum {rate_limit_service.batch_size_limit} files per batch. You submitted {len(files)}.",
                    "error": "BATCH_SIZE_EXCEEDED",
                    "batch_limit": rate_limit_service.batch_size_limit,
                    "submitted": len(files)
                }
            )

        # ========== STEP 2: CHECK RATE LIMIT ==========
        rate_limit_check = await rate_limit_service.check_batch_analysis_limit(
            user_email,
            len(files)
        )

        if not rate_limit_check["allowed"]:

            if rate_limit_check["reason"] == "batch_size_exceeded":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "success": False,
                        "message": rate_limit_check["message"],
                        "error": "BATCH_SIZE_EXCEEDED",
                        "batch_limit": rate_limit_service.batch_size_limit,
                        "submitted": rate_limit_check["submitted"]
                    }
                )
            else:  # file_limit_exceeded
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "success": False,
                        "message": rate_limit_check["message"],
                        "error": "RATE_LIMIT_EXCEEDED",
                        "current_count": rate_limit_check["current_files_uploaded"],
                        "batch_size": rate_limit_check["batch_size"],
                        "limit": rate_limit_check["files_limit"],
                        "would_exceed_by": rate_limit_check["would_exceed_by"],
                        "upgrade_required": True,
                        "upgrade_message": f"You've reached your free limit of {rate_limit_check['files_limit']} files. Upgrade to analyze more resumes."
                    }
                )

        # ========== STEP 3: PROCESS FILES ==========
        results = []
        successful_files = []
        failed_files = []
        batch_service = BatchAnalyzeService()

        for file in files:
            try:
                # Validate file
                if not file.filename:
                    raise ValueError("No filename provided")

                if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
                    raise ValueError("Invalid file format. Please upload PDF, DOC, or DOCX files only.")

                # Check file size (max 10MB)
                file_content = await file.read()
                if len(file_content) > 10 * 1024 * 1024:
                    raise ValueError("File too large. Maximum size is 10MB.")

                # Reset file pointer for processing
                await file.seek(0)

                # Parse resume
                parser = ResumeParser()
                resume_data = await parser.parse(file)

                # Generate role recommendations using batch service
                if target_role:
                    role_recommendations = await batch_service.analyze_role_fit(
                        resume_data, target_role, job_description
                    )
                else:
                    role_recommendations = await batch_service.generate(resume_data)

                # Advanced analysis
                advanced_analyzer = AdvancedAnalyzer()
                resume_score = await advanced_analyzer.calculate_resume_score(resume_data)
                personality_insights = await advanced_analyzer.analyze_personality(resume_data)
                career_path = await advanced_analyzer.predict_career_path(resume_data)

                # Build response
                response = ResumeAnalysisResponse(
                    resumeData=ResumeData(**resume_data),
                    questions=[],  # No questions for batch analysis
                    roleRecommendations=role_recommendations,
                    resumeScore=resume_score,
                    personalityInsights=personality_insights,
                    careerPath=career_path
                )

                results.append({
                    "file_name": file.filename,
                    "status": "success",
                    "data": response,
                    "error": None
                })
                successful_files.append(file.filename)

            except ValueError as e:
                results.append({
                    "file_name": file.filename,
                    "status": "validation_error",
                    "data": None,
                    "error": str(e)
                })
                failed_files.append((file.filename, str(e)))

            except Exception as e:
                error_message = str(e)
                if "PDF" in error_message:
                    error_message = "Error reading PDF file. Please ensure it's not corrupted."
                elif "DOCX" in error_message:
                    error_message = "Error reading DOCX file. Please ensure it's a valid document."
                else:
                    error_message = "Analysis failed. Please try again."

                results.append({
                    "file_name": file.filename,
                    "status": "error",
                    "data": None,
                    "error": error_message
                })
                failed_files.append((file.filename, error_message))

        # ========== STEP 4: TRACK UPLOADS ==========
        successful_count = len(successful_files)

        if successful_count > 0:
            # Increment batch_analysis counter by the number of files uploaded
            # Example: 3 files uploaded → batch_analysis +3
            await rate_limit_service.increment_batch_counter(user_email, successful_count)

        # ========== STEP 5: GET UPDATED STATS ==========
        updated_usage = await rate_limit_service.get_feature_usage(user_email)
        if updated_usage is None:
            updated_usage = {
                "files_uploaded": 0,
                "batch_analysis": 0,
                "compare_resumes": 0
            }

        # For batch_analyze, only show batch_analysis counter
        warning_at_batches = 10  # Warning threshold for batch operations
        approaching_limit = updated_usage["batch_analysis"] >= warning_at_batches

        # ========== STEP 6: BUILD RESPONSE ==========
        batch_response = {
            "success": True,
            "message": f"Batch analysis completed. {successful_count} of {len(files)} files processed successfully.",
            "batch_summary": {
                "total_submitted": len(files),
                "successful": successful_count,
                "failed": len(failed_files),
                "success_rate": f"{(successful_count / len(files) * 100):.1f}%" if len(files) > 0 else "0%"
            },
            "usage_stats": {
                "batches_processed": updated_usage["batch_analysis"],
                "approaching_limit": approaching_limit,
                "approaching_limit_threshold": warning_at_batches
            },
            "results": results
        }

        # Add upgrade prompt if approaching batch limit
        if approaching_limit:
            batch_response["upgrade_prompt"] = {
                "show": True,
                "message": f"You've processed {updated_usage['batch_analysis']} batch operations.",
                "cta": "Upgrade now to process unlimited batches",
                "batches_processed": updated_usage['batch_analysis']
            }

        # Add failed files details if any
        if failed_files:
            batch_response["failed_files_details"] = [
                {"filename": fname, "error": error}
                for fname, error in failed_files
            ]

        return batch_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Batch analysis failed. Please try again.",
                "error": "SERVER_ERROR"
            }
        )


@router.post("/compare-resumes")
async def compare_resumes(
    files: List[UploadFile] = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Compare multiple resumes and rank them.
    
    Requires: 2-5 resumes
    Rate Limit: 1 comparison per batch (same as batch analysis)
    Authentication: Required (JWT token)
    """
    try:
        user_email = current_user.email

        # ========== STEP 1: VALIDATE FILE COUNT ==========
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "message": "No files provided",
                    "error": "VALIDATION_ERROR"
                }
            )

        if len(files) < 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "message": "Minimum 2 resumes required for comparison",
                    "error": "VALIDATION_ERROR"
                }
            )

        if len(files) > 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "message": f"Maximum 5 resumes allowed for comparison. You submitted {len(files)}.",
                    "error": "VALIDATION_ERROR",
                    "limit": 5,
                    "submitted": len(files)
                }
            )

        # ========== STEP 2: CHECK RATE LIMIT ==========
        # Treat comparison as batch operation
        rate_limit_check = await rate_limit_service.check_batch_analysis_limit(
            user_email,
            len(files)
        )

        if not rate_limit_check["allowed"]:
            if rate_limit_check["reason"] == "batch_size_exceeded":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "success": False,
                        "message": rate_limit_check["message"],
                        "error": "BATCH_SIZE_EXCEEDED",
                        "batch_limit": rate_limit_service.batch_size_limit,
                        "submitted": rate_limit_check["submitted"]
                    }
                )
            else:  # file_limit_exceeded
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "success": False,
                        "message": rate_limit_check["message"],
                        "error": "RATE_LIMIT_EXCEEDED",
                        "current_count": rate_limit_check["current_files_uploaded"],
                        "files_submitted": len(files),
                        "limit": rate_limit_check["files_limit"],
                        "would_exceed_by": rate_limit_check["would_exceed_by"],
                        "upgrade_required": True,
                        "upgrade_message": f"You've reached your free limit of {rate_limit_check['files_limit']} files. Upgrade to compare more resumes."
                    }
                )

        # ========== STEP 3: PROCESS & ANALYZE RESUMES ==========
        candidates = []
        failed_files = []
        compare_service = CompareResumesService()

        for file in files:
            try:
                # Validate file
                if not file.filename:
                    raise ValueError("No filename provided")

                if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
                    raise ValueError("Invalid file format. Please upload PDF, DOC, or DOCX files only.")

                # Check file size (max 10MB)
                file_content = await file.read()
                if len(file_content) > 10 * 1024 * 1024:
                    raise ValueError("File too large. Maximum size is 10MB.")

                # Reset file pointer for processing
                await file.seek(0)

                # Parse resume
                parser = ResumeParser()
                resume_data = await parser.parse(file)

                # Calculate score using compare service
                advanced_analyzer = AdvancedAnalyzer()
                score = await advanced_analyzer.calculate_resume_score(resume_data)

                candidates.append({
                    "filename": file.filename,
                    "resumeData": ResumeData(**resume_data),
                    "score": score.overall_score,
                    "strengths": score.strengths,
                    "weaknesses": score.weaknesses,
                    "status": "success"
                })

            except ValueError as e:
                failed_files.append((file.filename, str(e)))
                candidates.append({
                    "filename": file.filename,
                    "error": str(e),
                    "score": 0,
                    "status": "validation_error"
                })

            except Exception as e:
                error_message = str(e)
                if "PDF" in error_message:
                    error_message = "Error reading PDF file. Please ensure it's not corrupted."
                elif "DOCX" in error_message:
                    error_message = "Error reading DOCX file. Please ensure it's a valid document."
                else:
                    error_message = "Analysis failed. Please try again."

                failed_files.append((file.filename, error_message))
                candidates.append({
                    "filename": file.filename,
                    "error": error_message,
                    "score": 0,
                    "status": "error"
                })

        # Check if we have at least 2 successful analyses
        successful_candidates = [c for c in candidates if c["status"] == "success"]
        if len(successful_candidates) < 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "message": "Failed to analyze enough resumes. Need at least 2 valid resumes for comparison.",
                    "error": "INSUFFICIENT_VALID_FILES",
                    "failed_files": [{"filename": fname, "error": error} for fname, error in failed_files]
                }
            )

        # ========== STEP 4: TRACK COMPARISON ==========
        # Only increment compare_resumes counter (NOT filesUploaded)
        await rate_limit_service.increment_compare_resumes_counter(user_email)

        # ========== STEP 5: GET UPDATED STATS ==========
        updated_usage = await rate_limit_service.get_feature_usage(user_email)
        if updated_usage is None:
            updated_usage = {
                "files_uploaded": 0,
                "batch_analysis": 0,
                "compare_resumes": 0
            }

        # For compare_resumes, only show compare_resumes counter
        warning_at_comparisons = 10  # Warning threshold for comparison operations
        approaching_limit = updated_usage["compare_resumes"] >= warning_at_comparisons

        # ========== STEP 6: RANK & RETURN RESULTS ==========
        # Rank candidates by score
        ranked_candidates = sorted(
            [c for c in candidates if c["status"] == "success"],
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        comparison_response = {
            "success": True,
            "message": f"Comparison completed. {len(successful_candidates)} resumes analyzed successfully.",
            "comparison_summary": {
                "total_submitted": len(files),
                "successful": len(successful_candidates),
                "failed": len(failed_files),
                "highest_score": max([c.get("score", 0) for c in successful_candidates]) if successful_candidates else 0,
                "average_score": sum([c.get("score", 0) for c in successful_candidates]) / len(successful_candidates) if successful_candidates else 0
            },
            "usage_stats": {
                "comparisons_completed": updated_usage["compare_resumes"],
                "approaching_limit": approaching_limit,
                "approaching_limit_threshold": warning_at_comparisons
            },
            "ranked_candidates": ranked_candidates,
            "recommendations": [
                "Consider top 3 candidates for interviews",
                "Review candidates with scores > 80 for immediate consideration",
                "Candidates with scores < 60 may need additional training"
            ]
        }

        # Add upgrade prompt if approaching comparison limit
        if approaching_limit:
            comparison_response["upgrade_prompt"] = {
                "show": True,
                "message": f"You've completed {updated_usage['compare_resumes']} comparisons.",
                "cta": "Upgrade now to compare unlimited resumes",
                "comparisons_completed": updated_usage['compare_resumes']
            }

        # Add failed files details if any
        if failed_files:
            comparison_response["failed_files_details"] = [
                {"filename": fname, "error": error}
                for fname, error in failed_files
            ]

        return comparison_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Unexpected error during comparison",
                "error": str(e)
            }
        )

