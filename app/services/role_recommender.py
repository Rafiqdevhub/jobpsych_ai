from typing import Dict, List, Any, Optional
from app.services.prompts.base_prompt_service import BasePromptService
from app.models.schemas import RoleRecommendation

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

class RoleRecommender(BasePromptService):
    def __init__(self):
        """Initialize the recommender and configure the generative AI client."""
        super().__init__()

    async def generate(self, resume_data: Dict[str, Any], **kwargs) -> List[RoleRecommendation]:
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

RECOMMENDATION RUBRIC:
{self.MATCH_RUBRIC}
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
OUTPUT: Return ONLY the JSON array with exactly 5 role recommendations, sorted by matchPercentage descending.
"""
        return prompt

    def _create_role_fit_prompt(self, resume_data: Dict[str, Any], target_role: str, job_description: Optional[str] = None) -> str:
        """Create a role-fit analysis prompt"""
        candidate_profile_block = self.render_candidate_profile(
            resume_data,
            include_personal_info=True,
            include_highlights=True
        )
        job_context = f"\n\nJob Description:\n{job_description}" if job_description else ""

        return f"""
ROLE: Expert HR Analyst specializing in role-fit assessment and career guidance.
TASK: Analyze candidate's fit for the target role and provide alternative recommendations.
INSTRUCTIONS: Evaluate skills match, experience relevance, and potential. Be direct and concise.

CANDIDATE PROFILE:
{candidate_profile_block}

TARGET ROLE: {target_role}
{job_context}

CANDIDATE PROFILE:

TASK: Analyze this candidate's fit for the "{target_role}" position and provide role recommendations.

Requirements:
1. FIRST: Analyze the candidate's fit for the TARGET ROLE ("{target_role}")
   - Provide detailed assessment of their suitability
   - Calculate match percentage (0-100)
   - List specific skills they have that match the role
   - List specific skills they need to develop

RECOMMENDATION RUBRIC:
{self.MATCH_RUBRIC}
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

OUTPUT: Return ONLY the JSON array. Target role first, followed by 4 alternative roles sorted by matchPercentage descending.
"""

    def _parse_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse the AI response and extract role recommendations"""
        try:
            recommendations = self.parse_json_array_response(response_text)
            
            if not isinstance(recommendations, list):
                raise ValueError(f"Response must be a JSON array, got {type(recommendations).__name__}")
            
            if len(recommendations) == 0:
                raise ValueError("Response array is empty - no recommendations provided")
            
            validated_recs = []
            required_fields = ["roleName", "matchPercentage", "reasoning"]
            for i, rec in enumerate(recommendations): # type: ignore
                if not isinstance(rec, dict):
                    raise ValueError(f"Recommendation {i} is not a JSON object: {type(rec).__name__}")
                
                # Check required fields
                for field in required_fields:
                    if field not in rec:
                        raise ValueError(f"Recommendation {i} missing required field: {field}")
                
                # Validate matchPercentage is a number
                try:
                    match_pct = float(rec["matchPercentage"])
                    if not (0 <= match_pct <= 100):
                        raise ValueError(f"matchPercentage {match_pct} not in range 0-100")
                    rec["matchPercentage"] = int(match_pct)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Recommendation {i}: matchPercentage must be a number 0-100: {e!s}")
                
                # Ensure skill lists are present and are lists
                for list_field in ["requiredSkills", "missingSkills"]:
                    if list_field not in rec or not isinstance(rec[list_field], list):
                        rec[list_field] = []
                
                validated_recs.append(rec)
            
            return validated_recs[:5]  # Limit to 5 recommendations as per original logic
        except ValueError as e:
            raise ValueError(f"Error parsing or validating recommendations: {e!s}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred during recommendation parsing: {e!s}")
