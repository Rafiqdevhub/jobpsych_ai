"""
Prompt services for AI-powered resume analysis.

This package contains specialized prompt services for each route endpoint:
- AnalyzeResumeService: For /analyze-resume endpoint
- HiredeskService: For /hiredesk-analyze endpoint
- BatchAnalyzeService: For /batch-analyze endpoint
- CompareResumesService: For /compare-resumes endpoint
- BasePromptService: Shared utilities and base class for all services
"""

from app.services.prompts.base_prompt_service import BasePromptService
from app.services.prompts.analyze_resume_service import AnalyzeResumeService
from app.services.prompts.hiredesk_service import HiredeskService
from app.services.prompts.batch_analyze_service import BatchAnalyzeService
from app.services.prompts.compare_resumes_service import CompareResumesService

__all__ = [
    "BasePromptService",
    "AnalyzeResumeService",
    "HiredeskService",
    "BatchAnalyzeService",
    "CompareResumesService",
]
