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


class CompareResumesService(BasePromptService):
    """
    Prompt service for /compare-resumes endpoint.
    
    Handles:
    - Comparative analysis prompts for multiple resumes
    - Ranking and scoring logic for resume comparison
    - Identification of strengths and weaknesses for each candidate
    - Comparative insights across all candidates
    - Designed for fast and efficient resume comparison
    
    Maintains same logic as existing compare resumes in router
    """

    def __init__(self):
        """Initialize the compare resumes service."""
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
        Generate role recommendations for comparison context.
        Not typically used in compare-resumes flow.
        
        Args:
            resume_data: Parsed resume data dictionary
            **kwargs: Additional arguments
            
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

    async def generate_comparison_analysis(
        self,
        resumes_data: List[Dict[str, Any]],
        target_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comparative analysis across multiple resumes.
        
        Args:
            resumes_data: List of parsed resume data dictionaries
            target_role: Optional target role for comparison context
            
        Returns:
            Dictionary containing comparative analysis and insights
        """
        model = self.model
        prompt = self._create_comparison_prompt(resumes_data, target_role)
        response = await model.generate_content_async(prompt)
        
        try:
            analysis = self._parse_comparison_analysis(response.text)
            return analysis
        except Exception as e:
            raise ValueError(f"Failed to generate comparison analysis: {str(e)}")

    async def generate_detailed_comparison(
        self,
        resumes_data: List[Dict[str, Any]],
        target_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate detailed pairwise comparison of resumes with strengths/weaknesses.
        
        Args:
            resumes_data: List of parsed resume data dictionaries
            target_role: Optional target role for comparison context
            
        Returns:
            Dictionary containing detailed comparison insights
        """
        model = self.model
        prompt = self._create_detailed_comparison_prompt(resumes_data, target_role)
        response = await model.generate_content_async(prompt)
        
        try:
            analysis = self._parse_detailed_comparison(response.text)
            return analysis
        except Exception as e:
            raise ValueError(f"Failed to generate detailed comparison: {str(e)}")

    # ========== PROMPT CREATION METHODS ==========

    def _create_role_prompt(self, resume_data: Dict[str, Any]) -> str:
        """Create a prompt for single resume role recommendation."""
        skills = self.format_skills(resume_data.get("skills", []))
        experience_summary = self.format_work_experience(resume_data.get("workExperience", []))
        education_summary = self.format_education(resume_data.get("education", []))
        personal_info = self.extract_personal_info(resume_data)

        prompt = f"""
Analyze this resume and recommend the top 3 most suitable job roles.

CANDIDATE:
Name: {personal_info['name']}
Skills: {skills}
Experience: {experience_summary}
Education: {education_summary}

Provide 3 role recommendations with match percentage, reasoning, required skills, and missing skills.

Return ONLY valid JSON array:
[
  {{
    "roleName": "Role Title",
    "matchPercentage": 85,
    "reasoning": "Fit explanation",
    "requiredSkills": ["Skill1"],
    "missingSkills": ["Skill2"]
  }}
]
"""
        return prompt

    def _create_comparison_prompt(
        self,
        resumes_data: List[Dict[str, Any]],
        target_role: Optional[str] = None
    ) -> str:
        """
        Create a prompt for high-level comparison of resumes.
        
        Args:
            resumes_data: List of resume data dictionaries
            target_role: Optional target role for comparison context
            
        Returns:
            Formatted prompt string
        """
        candidates_section = self._format_candidates_section(resumes_data)
        target_section = ""
        if target_role:
            target_section = f"\nTARGET ROLE: {target_role}\n"

        prompt = f"""
Compare these candidates and provide high-level insights.

{candidates_section}{target_section}

For comparison, provide:
1. Overall assessment: Brief summary of how these candidates compare
2. Key differentiators: What sets each candidate apart
3. Top performer: Which candidate stands out and why
4. Relative strengths: Key strengths of each candidate relative to others
5. Recommendations: Which candidates to prioritize for interviews

Return ONLY valid JSON object:
{{
  "overall_assessment": "Summary of comparison",
  "top_performer": "Candidate name",
  "top_performer_reason": "Why this candidate stands out",
  "key_differentiators": {{
    "Candidate1": "Key differentiator",
    "Candidate2": "Key differentiator"
  }},
  "relative_strengths": {{
    "Candidate1": ["Strength1", "Strength2"],
    "Candidate2": ["Strength1", "Strength2"]
  }},
  "recommendations": "Interview recommendations"
}}
"""
        return prompt

    def _create_detailed_comparison_prompt(
        self,
        resumes_data: List[Dict[str, Any]],
        target_role: Optional[str] = None
    ) -> str:
        """
        Create a prompt for detailed comparison with strengths/weaknesses analysis.
        
        Args:
            resumes_data: List of resume data dictionaries
            target_role: Optional target role for comparison context
            
        Returns:
            Formatted prompt string
        """
        candidates_section = self._format_candidates_section(resumes_data)
        target_section = ""
        if target_role:
            target_section = f"\nTARGET ROLE: {target_role}\n"

        prompt = f"""
Provide detailed comparison of these candidates with strengths and weaknesses analysis.

{candidates_section}{target_section}

For each candidate, provide:
1. Overall fit score (0-100)
2. Key strengths (list 3-4)
3. Key weaknesses (list 2-3)
4. Technical proficiency assessment
5. Experience level assessment
6. Growth potential

Return ONLY valid JSON object:
{{
  "candidates": [
    {{
      "name": "Candidate Name",
      "overall_fit_score": 85,
      "strengths": ["Strength1", "Strength2"],
      "weaknesses": ["Weakness1"],
      "technical_proficiency": "High",
      "experience_level": "Mid-level",
      "growth_potential": "High"
    }}
  ],
  "comparative_insights": "Overall insights comparing all candidates"
}}
"""
        return prompt

    # ========== HELPER METHODS ==========

    def _format_candidates_section(self, resumes_data: List[Dict[str, Any]]) -> str:
        """Format candidates section for prompt."""
        candidates_section = "CANDIDATES:\n"
        for idx, resume in enumerate(resumes_data, 1):
            personal_info = self.extract_personal_info(resume)
            skills = self.format_skills(resume.get("skills", []))
            experience = self.format_work_experience(resume.get("workExperience", []))
            
            candidates_section += f"""
Candidate {idx}: {personal_info['name']}
Skills: {skills}
Experience: {experience}

"""
        return candidates_section

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

    def _parse_comparison_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse high-level comparison analysis from AI response."""
        analysis = self.parse_json_response(response_text)
        
        # Validate structure
        if not isinstance(analysis, dict):
            raise ValueError("Comparison analysis should be a JSON object")
        
        required_fields = ["overall_assessment", "top_performer"]
        for field in required_fields:
            if field not in analysis:
                raise ValueError(f"Analysis must include {field} field")
        
        return analysis

    def _parse_detailed_comparison(self, response_text: str) -> Dict[str, Any]:
        """Parse detailed comparison analysis from AI response."""
        analysis = self.parse_json_response(response_text)
        
        # Validate structure
        if not isinstance(analysis, dict):
            raise ValueError("Detailed comparison should be a JSON object")
        
        if "candidates" not in analysis or not isinstance(analysis["candidates"], list):
            raise ValueError("Detailed comparison must include candidates array")
        
        return analysis
