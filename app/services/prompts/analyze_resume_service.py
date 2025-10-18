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


class AnalyzeResumeService(BasePromptService):
    """
    Prompt service for /analyze-resume endpoint.
    
    Handles:
    - General role recommendations without target role
    - Role fit analysis with target role and job description
    - Maintains same logic as existing RoleRecommender service
    """

    def __init__(self):
        """Initialize the analyze resume service."""
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
        Generate general role recommendations based on resume data.
        
        Args:
            resume_data: Parsed resume data dictionary
            **kwargs: Additional arguments (not used in this method)
            
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
        Analyze if candidate fits the target role and provide alternatives.
        
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
        Create a detailed prompt for general role recommendation.
        
        Args:
            resume_data: Parsed resume data dictionary
            
        Returns:
            Formatted prompt string for AI model
        """
        skills = self.format_skills(resume_data.get("skills", []))
        experience_summary = self.format_work_experience(resume_data.get("workExperience", []))
        education_summary = self.format_education(resume_data.get("education", []))
        highlights = self.format_highlights(resume_data.get("highlights", []))
        personal_info = self.extract_personal_info(resume_data)

        prompt = f"""
As an expert career advisor and recruitment specialist, analyze the following resume and recommend the top 5 most suitable job roles for this candidate.

CANDIDATE PROFILE:
Name: {personal_info['name']}
Skills: {skills}

WORK EXPERIENCE:
{experience_summary}

EDUCATION:
{education_summary}

KEY HIGHLIGHTS:
{highlights}

Based on the candidate's profile, provide 5 role recommendations in JSON format.

For each recommendation include:
1. roleName: The recommended job title/role
2. matchPercentage: Match percentage (0-100)
3. reasoning: Detailed explanation of why this role fits
4. requiredSkills: Array of skills required for this role that the candidate has
5. missingSkills: Array of skills required for this role that the candidate lacks

Return ONLY valid JSON array format:
[
  {{
    "roleName": "Senior Developer",
    "matchPercentage": 85,
    "reasoning": "Strong technical background with 5+ years experience",
    "requiredSkills": ["Python", "Django", "PostgreSQL"],
    "missingSkills": ["Kubernetes", "AWS"]
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
        Create a detailed prompt for analyzing fit with target role.
        
        Args:
            resume_data: Parsed resume data dictionary
            target_role: Target role to analyze
            job_description: Optional job description for detailed analysis
            
        Returns:
            Formatted prompt string for AI model
        """
        skills = self.format_skills(resume_data.get("skills", []))
        experience_summary = self.format_work_experience(resume_data.get("workExperience", []))
        education_summary = self.format_education(resume_data.get("education", []))
        highlights = self.format_highlights(resume_data.get("highlights", []))
        personal_info = self.extract_personal_info(resume_data)

        job_desc_section = ""
        if job_description:
            job_desc_section = f"\n\nJOB DESCRIPTION:\n{job_description}\n"

        prompt = f"""
As an expert recruiter and career analyst, analyze the fit between this candidate and the target role.

CANDIDATE PROFILE:
Name: {personal_info['name']}
Skills: {skills}

WORK EXPERIENCE:
{experience_summary}

EDUCATION:
{education_summary}

KEY HIGHLIGHTS:
{highlights}

TARGET ROLE: {target_role}{job_desc_section}

Analyze the candidate's fit for the target role and provide:
1. Primary fit analysis for the target role
2. 2-3 alternative roles that might be a good fit
3. For each role, include match percentage, reasoning, required skills, and missing skills

Return ONLY valid JSON array format with target role first, then alternatives:
[
  {{
    "roleName": "{target_role}",
    "matchPercentage": 85,
    "reasoning": "Clear fit for this role based on experience and skills",
    "requiredSkills": ["Skill1", "Skill2"],
    "missingSkills": ["Skill3"]
  }},
  {{
    "roleName": "Alternative Role",
    "matchPercentage": 78,
    "reasoning": "Good alternative based on transferable skills",
    "requiredSkills": ["Skill1"],
    "missingSkills": ["Skill4"]
  }}
]
"""
        return prompt

    # ========== RESPONSE PARSING METHODS ==========

    def _parse_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse role recommendations from AI response.
        
        Args:
            response_text: Raw response text from AI model
            
        Returns:
            List of parsed recommendation dictionaries
        """
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
