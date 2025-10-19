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


class HiredeskService(BasePromptService):
    """
    Prompt service for /hiredesk-analyze endpoint.
    
    Handles:
    - Comprehensive resume analysis
    - Role recommendations with best fit detection
    - Role fit analysis with target role and job description
    - Question generation for interviews
    - Resume scoring and personality analysis
    - Career path prediction
    
    Maintains same logic as existing services combined (RoleRecommender, QuestionGenerator, AdvancedAnalyzer)
    """

    def __init__(self):
        """Initialize the hiredesk analysis service."""
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
        """Get the generative AI model instance with JSON mode enabled."""
        if self._model is None:
            if not GENAI_AVAILABLE or not genai:
                raise ImportError("google-generativeai package is not available")
            # Force JSON output from the model
            try:
                json_config = genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
                self._model = genai.GenerativeModel(
                    self.DEFAULT_MODEL,
                    generation_config=json_config
                )
            except Exception:
                # Fallback if JSON mode is not available
                self._model = genai.GenerativeModel(self.DEFAULT_MODEL)
        return self._model

    async def generate(self, resume_data: Dict[str, Any], **kwargs) -> List[RoleRecommendation]:
        """
        Generate general role recommendations for comprehensive analysis.
        
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
        Analyze if candidate fits the target role.
        
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

    async def generate_interview_questions(
        self,
        resume_data: Dict[str, Any],
        target_role: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Generate interview questions tailored to the candidate and role.
        
        Args:
            resume_data: Parsed resume data dictionary
            target_role: Optional target role for role-specific questions
            job_description: Optional job description for better questions
            
        Returns:
            List of question dictionaries with type, question, and context
        """
        model = self.model
        
        if target_role:
            prompt = self._create_role_specific_questions_prompt(
                resume_data, target_role, job_description
            )
        else:
            prompt = self._create_general_questions_prompt(resume_data)
        
        response = await model.generate_content_async(prompt)
        
        try:
            questions = self._parse_questions(response.text)
            return questions
        except Exception as e:
            raise ValueError(f"Failed to generate interview questions: {str(e)}")

    # ========== PROMPT CREATION METHODS ==========

    def _create_role_prompt(self, resume_data: Dict[str, Any]) -> str:
        """Create optimized structured prompt for role recommendations."""
        skills = self.format_skills(resume_data.get("skills", []))
        experience_summary = self.format_work_experience(resume_data.get("workExperience", []))
        education_summary = self.format_education(resume_data.get("education", []))
        highlights = self.format_highlights(resume_data.get("highlights", []))

        prompt = f"""ROLE: Expert Career Advisor & Technical Recruiter.

TASK: Recommend 5 best-fit job roles for this candidate.

CANDIDATE_PROFILE:
Skills: {skills}
Work_Experience: {experience_summary}
Education: {education_summary}
Highlights: {highlights}

INSTRUCTIONS:
1. Generate top 5 most suitable roles.
2. For matchPercentage use this rubric:
   - 90-100: Perfect fit, all key skills match
   - 75-89: Strong fit, most key skills match
   - 60-74: Good fit, some skills match, some missing
   - <60: Potential fit, significant skill gaps
3. reasoning: 1-2 sentence justification only
4. requiredSkills: Skills candidate HAS for this role
5. missingSkills: Critical skills candidate LACKS

RESPONSE SCHEMA (MUST FOLLOW):
You MUST output a valid JSON array with exactly this structure. EVERY object MUST have roleName and matchPercentage:
[
  {{
    "roleName": "string (required)",
    "matchPercentage": "number 0-100 (required)",
    "reasoning": "string (required)",
    "requiredSkills": ["string"],
    "missingSkills": ["string"]
  }}
]

OUTPUT: Return ONLY the JSON array. No additional text before or after."""
        return prompt

    def _create_role_fit_prompt(
        self,
        resume_data: Dict[str, Any],
        target_role: str,
        job_description: Optional[str] = None
    ) -> str:
        """Create optimized structured prompt for role fit analysis."""
        skills = self.format_skills(resume_data.get("skills", []))
        experience_summary = self.format_work_experience(resume_data.get("workExperience", []))
        education_summary = self.format_education(resume_data.get("education", []))
        highlights = self.format_highlights(resume_data.get("highlights", []))

        job_section = f"Job_Description: {job_description[:300]}\n" if job_description else ""

        prompt = f"""ROLE: Expert Recruiter & Career Analyst.

TASK: Analyze candidate fit for {target_role}.

CANDIDATE_PROFILE:
Skills: {skills}
Work_Experience: {experience_summary}
Education: {education_summary}
Highlights: {highlights}

{job_section}
INSTRUCTIONS:
1. Provide primary analysis for {target_role}.
2. For matchPercentage use this rubric:
   - 90-100: Perfect fit, all key skills match
   - 75-89: Strong fit, most key skills match
   - 60-74: Good fit, some skills match, some missing
   - <60: Potential fit, significant skill gaps
3. reasoning: 1-2 sentence justification only
4. requiredSkills: Skills candidate HAS for this role
5. missingSkills: Critical skills candidate LACKS

RESPONSE SCHEMA (MUST FOLLOW):
You MUST output a valid JSON array with exactly this structure. EVERY object MUST have roleName and matchPercentage:
[
  {{
    "roleName": "string (required)",
    "matchPercentage": "number 0-100 (required)",
    "reasoning": "string (required)",
    "requiredSkills": ["string"],
    "missingSkills": ["string"]
  }}
]

OUTPUT: Return ONLY the JSON array. No additional text before or after."""
        return prompt

    def _create_general_questions_prompt(self, resume_data: Dict[str, Any]) -> str:
        """Create optimized structured prompt for general interview questions."""
        skills = self.format_skills(resume_data.get("skills", []))
        experience_summary = self.format_work_experience(resume_data.get("workExperience", []))
        education_summary = self.format_education(resume_data.get("education", []))

        prompt = f"""ROLE: Senior AI Hiring Manager.

TASK: Generate 8-10 insightful interview questions for this candidate.

CANDIDATE_PROFILE:
Skills: {skills}
Work_Experience: {experience_summary}
Education: {education_summary}

INSTRUCTIONS:
1. Generate 8-10 questions probing skills, experience, and gaps.
2. Include mix of "technical", "behavioral", and "problem-solving" types.
3. context: 1-sentence explanation of WHY this question is asked.
4. Questions must target specific skills or experiences from resume.

RESPONSE SCHEMA (MUST FOLLOW):
You MUST output a valid JSON array with exactly this structure:
[
  {{
    "type": "string (required: 'technical'|'behavioral'|'problem-solving')",
    "question": "string (required)",
    "context": "string (required: 1-2 sentence reason for asking)"
  }}
]

OUTPUT: Return ONLY the JSON array. No additional text before or after."""
        return prompt

    def _create_role_specific_questions_prompt(
        self,
        resume_data: Dict[str, Any],
        target_role: str,
        job_description: Optional[str] = None
    ) -> str:
        """Create optimized structured prompt for role-specific questions."""
        skills = self.format_skills(resume_data.get("skills", []))
        experience_summary = self.format_work_experience(resume_data.get("workExperience", []))
        education_summary = self.format_education(resume_data.get("education", []))

        job_section = f"Job_Description: {job_description[:300]}\n" if job_description else ""

        prompt = f"""ROLE: Expert Technical Interviewer for {target_role}.

TASK: Generate 8-10 role-specific interview questions.

CANDIDATE_PROFILE:
Skills: {skills}
Work_Experience: {experience_summary}
Education: {education_summary}

{job_section}
INSTRUCTIONS:
1. Generate 8-10 questions specific to {target_role} position.
2. Include role requirements, scenario-based, fit assessment questions.
3. Focus on how candidate skills translate to {target_role}.
4. Include mix of "role-specific", "technical", "behavioral", "scenario-based".
5. context: 1-sentence explanation of WHY this question matters for {target_role}.

RESPONSE SCHEMA (MUST FOLLOW):
You MUST output a valid JSON array with exactly this structure:
[
  {{
    "type": "string (required: 'role-specific'|'technical'|'behavioral'|'scenario-based')",
    "question": "string (required)",
    "context": "string (required: 1-2 sentence reason for asking)"
  }}
]

OUTPUT: Return ONLY the JSON array. No additional text before or after."""
        return prompt

    # ========== RESPONSE PARSING METHODS ==========

    def _parse_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse role recommendations from AI response with validation."""
        recommendations = self.parse_json_array_response(response_text)
        
        # Validate structure
        if not isinstance(recommendations, list):
            raise ValueError(f"Response must be a JSON array, got {type(recommendations).__name__}")
        
        if len(recommendations) == 0:
            raise ValueError("Response array is empty - no recommendations provided")
        
        validated_recs = []
        for i, rec in enumerate(recommendations):
            if not isinstance(rec, dict):
                raise ValueError(f"Recommendation {i} is not a JSON object: {type(rec).__name__}")
            
            # Check required fields
            if "roleName" not in rec:
                raise ValueError(f"Recommendation {i} missing required field: roleName")
            if "matchPercentage" not in rec:
                raise ValueError(f"Recommendation {i} missing required field: matchPercentage")
            if "reasoning" not in rec:
                raise ValueError(f"Recommendation {i} missing required field: reasoning")
            
            # Validate matchPercentage is a number
            try:
                match_pct = float(rec["matchPercentage"])
                if not (0 <= match_pct <= 100):
                    raise ValueError(f"matchPercentage {match_pct} not in range 0-100")
                rec["matchPercentage"] = int(match_pct)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Recommendation {i}: matchPercentage must be a number 0-100: {str(e)}")
            
            validated_recs.append(rec)
        
        return validated_recs

    def _parse_questions(self, response_text: str) -> List[Dict[str, str]]:
        """Parse interview questions from AI response with validation."""
        questions = self.parse_json_array_response(response_text)
        
        # Validate structure
        if not isinstance(questions, list):
            raise ValueError(f"Response must be a JSON array, got {type(questions).__name__}")
        
        if len(questions) == 0:
            raise ValueError("Response array is empty - no questions generated")
        
        validated_qs = []
        for i, q in enumerate(questions):
            if not isinstance(q, dict):
                raise ValueError(f"Question {i} is not a JSON object: {type(q).__name__}")
            
            # Check required fields
            if "type" not in q:
                raise ValueError(f"Question {i} missing required field: type")
            if "question" not in q:
                raise ValueError(f"Question {i} missing required field: question")
            if "context" not in q:
                raise ValueError(f"Question {i} missing required field: context")
            
            validated_qs.append(q)
        
        return validated_qs
