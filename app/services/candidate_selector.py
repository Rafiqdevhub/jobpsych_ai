from typing import Dict, List, Any
from app.services.resume_parser import ResumeParser
from app.services.prompts.candidate_selection_service import CandidateSelectionService
from fastapi import UploadFile


class CandidateSelector:
    def __init__(self):
        self.parser = ResumeParser()
        self.selector_service = CandidateSelectionService()

    async def evaluate_candidates(
        self, files: List[UploadFile], job_title: str, keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate multiple candidates and return FIT/REJECT decisions.
        Args:
            files: List of resume files to evaluate
            job_title: Target job position
            keywords: List of required skills/keywords
        Returns:
            List of results with candidate name, status, and message
        """
        results = []
        
        for file in files:
            try:
                # Reset file pointer to beginning
                await file.seek(0)
                
                # Extract text from resume
                content = await self._extract_resume_text(file)
                
                # Evaluate candidate
                evaluation = await self.selector_service.evaluate_candidate(
                    content, job_title, keywords
                )
                
                result = {
                    "candidate": file.filename or "unknown",
                    "status": evaluation.get("status", "REJECT"),
                    "message": evaluation.get("message", "Evaluation completed")
                }
                results.append(result)
                
            except Exception as e:
                # If parsing fails, mark as reject
                results.append({
                    "candidate": file.filename or "unknown",
                    "status": "REJECT",
                    "message": f"Could not parse file: {str(e)[:50]}"
                })
        
        return results

    async def _extract_resume_text(self, file: UploadFile) -> str:
        """
        Extract text from resume file using ResumeParser.
        
        Args:
            file: Resume file
            
        Returns:
            Extracted text content
        """
        # Reset file pointer
        await file.seek(0)
        
        # Use existing parser to extract text
        content = await self.parser._extract_text(file)
        
        if not content or not content.strip():
            raise ValueError("No readable text found in file")
        
        return content
