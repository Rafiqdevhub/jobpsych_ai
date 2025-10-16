import os
import json
from typing import Dict, List, Any, Optional
from app.models.schemas import RoleRecommendation

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

class RoleRecommender:
    def __init__(self):
        """Initialize the recommender and configure the generative AI client."""
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
            self._model = genai.GenerativeModel('gemini-2.5-pro')
        return self._model

    async def recommend_roles(self, resume_data: Dict[str, Any]) -> List[RoleRecommendation]:
        """Recommend suitable job roles based on resume data."""
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

    async def analyze_role_fit(self, resume_data: Dict[str, Any], target_role: str, job_description: Optional[str] = None) -> List[RoleRecommendation]:
        """Analyze if candidate fits the target role and provide alternatives."""
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

    def _create_role_prompt(self, resume_data: Dict[str, Any]) -> str:
        """Create a detailed prompt for role recommendation."""
        skills = ", ".join(resume_data.get("skills", []))
        experience_summary = [
            f"- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})"
            for exp in resume_data.get("workExperience", []) if exp.get('title') and exp.get('company')
        ]
        education_summary = [
            f"- {edu.get('degree', '')} from {edu.get('institution', '')}"
            for edu in resume_data.get("education", []) if edu.get('degree') and edu.get('institution')
        ]
        highlights = "\n".join([f"- {highlight}" for highlight in resume_data.get("highlights", [])])
        personal_info = resume_data.get("personalInfo", {})
        name = personal_info.get("name", "Candidate")
        prompt = f"""
As an expert career advisor and recruitment specialist, analyze the following resume and recommend the top 5 most suitable job roles for this candidate.

CANDIDATE PROFILE:
Name: {name}
Skills: {skills}

WORK EXPERIENCE:
{chr(10).join(experience_summary) if experience_summary else "No work experience listed"}

EDUCATION:
{chr(10).join(education_summary) if education_summary else "No education information"}

KEY HIGHLIGHTS:
{highlights if highlights else "No highlights listed"}

INSTRUCTIONS:
Provide exactly 5 job role recommendations in valid JSON format. For each role, analyze:
1. How well the candidate matches (percentage)
2. Detailed reasoning for the recommendation
3. Required skills for the role
4. Skills the candidate might be missing

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "roleName": "Specific Job Title",
    "matchPercentage": 85,
    "reasoning": "Detailed explanation of why this role fits, mentioning specific skills and experience",
    "requiredSkills": ["Skill1", "Skill2", "Skill3"],
    "missingSkills": ["Skill4", "Skill5"]
  }}
]

Focus on realistic, current job market roles. Consider the candidate's experience level, technical skills, and career progression. Ensure match percentages are realistic (60-95% range).
"""
        return prompt

    def _create_role_fit_prompt(self, resume_data: Dict[str, Any], target_role: str, job_description: Optional[str] = None) -> str:
        """Create a role-fit analysis prompt"""
        skills = ", ".join(resume_data.get("skills", []))
        experience = "\n".join([
            f"- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})"
            for exp in resume_data.get("workExperience", [])
        ])
        education = "\n".join([
            f"- {edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('year', '')})"
            for edu in resume_data.get("education", [])
        ])
        job_context = f"\n\nJob Description:\n{job_description}" if job_description else ""
        return f"""
You are an expert HR analyst specializing in role-fit assessment and career guidance.

TARGET ROLE ANALYSIS: {target_role}
{job_context}

CANDIDATE PROFILE:
Skills: {skills}

Work Experience:
{experience}

Education:
{education}

TASK: Analyze this candidate's fit for the "{target_role}" position and provide role recommendations.

Requirements:
1. FIRST: Analyze the candidate's fit for the TARGET ROLE ("{target_role}")
   - Provide detailed assessment of their suitability
   - Calculate match percentage (0-100)
   - List specific skills they have that match the role
   - List specific skills they need to develop

2. THEN: Recommend 4 alternative roles they might be better suited for
   - Focus on roles that better match their current skill set
   - Include emerging opportunities based on their background
   - Consider career progression paths

For each role recommendation, provide:
- roleName: The job title
- matchPercentage: 0-100 numeric score
- reasoning: Detailed explanation of fit and recommendations
- requiredSkills: Array of skills they already have that match
- missingSkills: Array of skills they need to develop

Return response as a JSON array with the target role analysis FIRST, followed by alternative recommendations.

Example format:
[
  {{
    "roleName": "{target_role}",
    "matchPercentage": 75,
    "reasoning": "Detailed analysis of fit for target role...",
    "requiredSkills": ["skill1", "skill2"],
    "missingSkills": ["skill3", "skill4"]
  }},
  // ... 4 alternative role recommendations
]

Focus on providing actionable insights and realistic assessments.
"""

    def _parse_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse the AI response and extract role recommendations"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            # Find JSON content between brackets
            start_idx = cleaned_text.find('[')
            end_idx = cleaned_text.rfind(']') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No valid JSON array found in response")
            json_text = cleaned_text[start_idx:end_idx]
            # Parse JSON
            recommendations = json.loads(json_text)
            # Validate structure
            if not isinstance(recommendations, list):
                raise ValueError("Response is not a list")
            # Validate each recommendation
            required_fields = ["roleName", "matchPercentage", "reasoning"]
            for i, rec in enumerate(recommendations):
                if not isinstance(rec, dict):
                    raise ValueError(f"Recommendation {i} is not a dictionary")
                for field in required_fields:
                    if field not in rec:
                        raise ValueError(f"Missing required field '{field}' in recommendation {i}")
                # Ensure match percentage is valid
                if not isinstance(rec.get("matchPercentage"), (int, float)) or not (0 <= rec["matchPercentage"] <= 100):
                    rec["matchPercentage"] = 75  # Default fallback
                # Ensure lists are actually lists
                for list_field in ["requiredSkills", "missingSkills"]:
                    if list_field in rec and not isinstance(rec[list_field], list):
                        rec[list_field] = []
                # Remove unwanted fields if present
                for remove_field in ["careerLevel", "salaryRange", "industryFit"]:
                    if remove_field in rec:
                        rec.pop(remove_field)
            return recommendations[:5]  # Limit to 5 recommendations
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in AI response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing recommendations: {str(e)}")
