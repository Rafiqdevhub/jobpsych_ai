import os
from typing import Dict, List, Any, Optional
from app.models.schemas import RoleRecommendation
from app.services.prompts.base_prompt_service import BasePromptService

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False


class BatchAnalyzeService(BasePromptService):
    """
    Prompt service for /batch-analyze endpoint.
    
    Handles:
    - Optimized prompts for batch processing of multiple resumes
    - Faster analysis without unnecessary details
    - Role recommendations for batch context
    - Maintains consistency with single resume analysis
    - Designed for efficiency in batch operations
    
    Maintains same logic as existing batch analysis in router
    """

    def __init__(self):
        """Initialize the batch analysis service."""
        super().__init__()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        if not GENAI_AVAILABLE or not genai:
            raise ImportError("google-generativeai package is not available")
        genai.configure(api_key=self.api_key)
        self._model = None

    @property
    def model(self):
        """Get the generative AI model instance."""
        if self._model is None:
            if not GENAI_AVAILABLE or not genai:
                raise ImportError("google-generativeai package is not available")
            self._model = genai.GenerativeModel(self.DEFAULT_MODEL)
        return self._model

    async def generate(self, resume_data: Dict[str, Any], **kwargs) -> List[RoleRecommendation]:
        """
        Generate general role recommendations for batch processing.
        
        Args:
            resume_data: Parsed resume data dictionary
            **kwargs: Additional arguments (not used)
            
        Returns:
            List of RoleRecommendation objects
        """
        model = self.model
        prompt = self._create_role_prompt(resume_data)
        response = await model.generate_content_async(prompt)
        
        try:
            role_recommendations = self._parse_recommendations(response.text)
            return [
                RoleRecommendation(
                    roleName=rec["roleName"],
                    matchPercentage=rec["matchPercentage"],
                    reasoning=rec["reasoning"],
                    requiredSkills=rec.get("requiredSkills", []),
                    missingSkills=rec.get("missingSkills", [])
                ) for rec in role_recommendations
            ]
        except Exception as e:
            raise ValueError(f"Failed to generate role recommendations: {str(e)}")

    async def analyze_role_fit(
        self,
        resume_data: Dict[str, Any],
        target_role: str,
        job_description: Optional[str] = None
    ) -> List[RoleRecommendation]:
        """
        Analyze if candidate fits the target role for batch processing.
        
        Args:
            resume_data: Parsed resume data dictionary
            target_role: Target job role to analyze fit for
            job_description: Optional job description for better analysis
            
        Returns:
            List of RoleRecommendation objects with target role as primary
        """
        model = self.model
        prompt = self._create_role_fit_prompt(resume_data, target_role, job_description)
        response = await model.generate_content_async(prompt)
        
        try:
            role_recommendations = self._parse_recommendations(response.text)
            return [
                RoleRecommendation(
                    roleName=rec["roleName"],
                    matchPercentage=rec["matchPercentage"],
                    reasoning=rec["reasoning"],
                    requiredSkills=rec.get("requiredSkills", []),
                    missingSkills=rec.get("missingSkills", [])
                ) for rec in role_recommendations
            ]
        except Exception as e:
            raise ValueError(f"Failed to analyze role fit: {str(e)}")

    # ========== PROMPT CREATION METHODS ==========

    def _create_role_prompt(self, resume_data: Dict[str, Any]) -> str:
        """
        Create an optimized prompt for batch role recommendation.
        Concise but still accurate for batch context.
        
        Args:
            resume_data: Parsed resume data dictionary
            
        Returns:
            Formatted prompt string for AI model
        """
        skills = self.format_skills(resume_data.get("skills", []))
        experience_summary = self.format_work_experience(resume_data.get("workExperience", []))
        education_summary = self.format_education(resume_data.get("education", []))
        personal_info = self.extract_personal_info(resume_data)

        prompt = f"""
Analyze this resume and recommend the top 5 most suitable job roles.

CANDIDATE:
Name: {personal_info['name']}
Skills: {skills}
Experience: {experience_summary}
Education: {education_summary}

Provide 5 role recommendations with match percentage, reasoning, required skills, and missing skills.

Return ONLY valid JSON array:
[
  {{
    "roleName": "Role Title",
    "matchPercentage": 85,
    "reasoning": "Fit explanation",
    "requiredSkills": ["Skill1", "Skill2"],
    "missingSkills": ["Skill3"]
  }}
]
"""
        return prompt

    def _create_role_fit_prompt(
        self,
        resume_data: Dict[str, Any],
        target_role: str,
        job_description: Optional[str] = None
    ) -> str:
        """
        Create an optimized prompt for batch role fit analysis.
        
        Args:
            resume_data: Parsed resume data dictionary
            target_role: Target role to analyze
            job_description: Optional job description
            
        Returns:
            Formatted prompt string for AI model
        """
        skills = self.format_skills(resume_data.get("skills", []))
        experience_summary = self.format_work_experience(resume_data.get("workExperience", []))
        education_summary = self.format_education(resume_data.get("education", []))
        personal_info = self.extract_personal_info(resume_data)

        job_desc_section = ""
        if job_description:
            job_desc_section = f"\n\nJOB DESCRIPTION:\n{job_description}\n"

        prompt = f"""
Analyze this candidate's fit for the target role.

CANDIDATE:
Name: {personal_info['name']}
Skills: {skills}
Experience: {experience_summary}
Education: {education_summary}

TARGET ROLE: {target_role}{job_desc_section}

Analyze fit and provide match percentage, reasoning, required skills, and missing skills.

Return ONLY valid JSON array:
[
  {{
    "roleName": "{target_role}",
    "matchPercentage": 85,
    "reasoning": "Fit explanation",
    "requiredSkills": ["Skill1"],
    "missingSkills": ["Skill2"]
  }}
]
"""
        return prompt

    # ========== RESPONSE PARSING METHODS ==========

    def _parse_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse role recommendations from AI response."""
        recommendations = self.parse_json_array_response(response_text)
        
        # Validate structure
        if not isinstance(recommendations, list):
            raise ValueError("Response should be a JSON array of recommendations")
        
        for rec in recommendations:
            if not isinstance(rec, dict):
                raise ValueError("Each recommendation should be a JSON object")
            if "roleName" not in rec or "matchPercentage" not in rec:
                raise ValueError("Each recommendation must have roleName and matchPercentage")
        
        return recommendations
