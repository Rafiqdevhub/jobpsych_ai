import os
from typing import Dict, List, Any, Optional
from app.models.schemas import RoleRecommendation, ResumeScore, PersonalityInsights, CareerPathPrediction
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
        """Get the generative AI model instance with JSON mode enabled."""
        if self._model is None:
            if not GENAI_AVAILABLE or not genai:
                raise ImportError("google-generativeai package is not available")
            try:
                json_config = genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
                self._model = genai.GenerativeModel(
                    self.DEFAULT_MODEL,
                    generation_config=json_config
                )
            except Exception:
                # Fallback for older API versions
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

    async def calculate_resume_score(self, resume_data: Dict[str, Any]) -> ResumeScore:
        """
        Calculate comprehensive resume score across multiple dimensions.
        
        Args:
            resume_data: Parsed resume data dictionary
            
        Returns:
            ResumeScore object with detailed breakdown
        """
        model = self.model
        prompt = self._create_scoring_prompt(resume_data)
        response = await model.generate_content_async(prompt)
        
        try:
            score_data = self._parse_score_response(response.text)
            return ResumeScore(**score_data)
        except Exception as e:
            raise ValueError(f"Failed to calculate resume score: {str(e)}")

    async def analyze_personality(self, resume_data: Dict[str, Any]) -> PersonalityInsights:
        """
        Analyze personality traits and work style preferences from resume.
        
        Args:
            resume_data: Parsed resume data dictionary
            
        Returns:
            PersonalityInsights object with trait analysis
        """
        model = self.model
        prompt = self._create_personality_prompt(resume_data)
        response = await model.generate_content_async(prompt)
        
        try:
            personality_data = self._parse_personality_response(response.text)
            return PersonalityInsights(**personality_data)
        except Exception as e:
            raise ValueError(f"Failed to analyze personality: {str(e)}")

    async def predict_career_path(self, resume_data: Dict[str, Any]) -> CareerPathPrediction:
        """
        Predict career progression and next opportunities.
        
        Args:
            resume_data: Parsed resume data dictionary
            
        Returns:
            CareerPathPrediction object with progression analysis
        """
        model = self.model
        prompt = self._create_career_prompt(resume_data)
        response = await model.generate_content_async(prompt)
        
        try:
            career_data = self._parse_career_response(response.text)
            return CareerPathPrediction(**career_data)
        except Exception as e:
            raise ValueError(f"Failed to predict career path: {str(e)}")

    async def generate_role_preparation_plan(
        self,
        resume_data: Dict[str, Any],
        target_role: str,
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive preparation plan for a specific target role.
        Analyzes resume against job requirements and provides actionable guidance.
        
        Args:
            resume_data: Parsed resume data dictionary
            target_role: Target job role to prepare for
            job_description: Optional job description for detailed analysis
            
        Returns:
            Dictionary with role-specific preparation plan including:
            - Role fit score
            - Key skill gaps
            - Personality alignment
            - Preparation tips (specific to role)
            - Timeline estimates
            - Success metrics
        """
        model = self.model
        prompt = self._create_preparation_plan_prompt(resume_data, target_role, job_description)
        response = await model.generate_content_async(prompt)
        
        try:
            preparation_plan = self._parse_preparation_plan_response(response.text)
            return preparation_plan
        except Exception as e:
            raise ValueError(f"Failed to generate preparation plan: {str(e)}")

    # ========== PROMPT CREATION METHODS ==========

    def _build_candidate_profile(self, resume_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Build a consolidated candidate profile to avoid repetition in prompts.
        
        Args:
            resume_data: Parsed resume data dictionary
            
        Returns:
            Dictionary with formatted profile sections
        """
        return {
            "skills": self.format_skills(resume_data.get("skills", [])),
            "experience": self.format_work_experience(resume_data.get("workExperience", [])),
            "education": self.format_education(resume_data.get("education", [])),
            "highlights": self.format_highlights(resume_data.get("highlights", [])),
            "personal_info": self.extract_personal_info(resume_data)
        }

    def _create_role_prompt(self, resume_data: Dict[str, Any]) -> str:
        """
        Create a focused prompt for general role recommendation.
        Uses structured ROLE/TASK/INSTRUCTIONS format.
        JSON mode ensures valid JSON output without extra tokens.
        """
        profile = self._build_candidate_profile(resume_data)

        return f"""
ROLE: Expert Career Advisor and Recruitment Specialist
TASK: Recommend top 5 most suitable job roles for this candidate
INSTRUCTIONS: Analyze the candidate's skills, experience, and background. Provide concise, accurate matches.

CANDIDATE PROFILE:
Name: {profile['personal_info']['name']}
Skills: {profile['skills']}
Experience: {profile['experience']}
Education: {profile['education']}
Highlights: {profile['highlights']}

RECOMMENDATION RUBRIC:
- 90-100: Excellent fit, minimal skill gaps
- 75-89: Strong fit, some valuable experience
- 60-74: Good fit, notable skill gaps
- <60: Potential role, significant development needed

RESPONSE_SCHEMA:
[
  {{
    "roleName": "<job title>",
    "matchPercentage": <0-100>,
    "reasoning": "<1-2 sentences: why this role fits>",
    "requiredSkills": ["<skill 1>", "<skill 2>"],
    "missingSkills": ["<gap 1>", "<gap 2>"]
  }}
]

OUTPUT: Return ONLY the JSON array with exactly 5 role recommendations, sorted by matchPercentage descending.
"""

    def _create_role_fit_prompt(
        self,
        resume_data: Dict[str, Any],
        target_role: str,
        job_description: Optional[str] = None
    ) -> str:
        """
        Create a focused prompt for analyzing target role fit.
        Uses structured ROLE/TASK/INSTRUCTIONS format.
        JSON mode ensures valid JSON output without extra tokens.
        """
        profile = self._build_candidate_profile(resume_data)
        
        job_desc_section = f"\n\nJOB DESCRIPTION:\n{job_description}" if job_description else ""

        return f"""
ROLE: Senior Recruiter and Career Analyst
TASK: Analyze candidate fit for target role and recommend alternatives
INSTRUCTIONS: Evaluate skills match, experience relevance, and potential. Be direct and concise.

CANDIDATE PROFILE:
Name: {profile['personal_info']['name']}
Skills: {profile['skills']}
Experience: {profile['experience']}
Education: {profile['education']}
Highlights: {profile['highlights']}

TARGET ROLE: {target_role}{job_desc_section}

RECOMMENDATION RUBRIC:
- 90-100: Excellent fit, ready to start
- 75-89: Strong fit, minimal onboarding needed
- 60-74: Good fit, some training required
- <60: Potential role, significant development needed

RESPONSE_SCHEMA:
[
  {{
    "roleName": "{target_role}",
    "matchPercentage": <0-100>,
    "reasoning": "<1-2 sentences: fit analysis>",
    "requiredSkills": ["<skill 1>", "<skill 2>"],
    "missingSkills": ["<gap 1>", "<gap 2>"]
  }},
  {{
    "roleName": "<alternative role>",
    "matchPercentage": <0-100>,
    "reasoning": "<1-2 sentences>",
    "requiredSkills": ["<skill 1>"],
    "missingSkills": ["<gap 1>"]
  }}
]

OUTPUT: Return ONLY the JSON array. Target role first, followed by 2-3 alternative roles sorted by matchPercentage descending.
"""

    def _create_scoring_prompt(self, resume_data: Dict[str, Any]) -> str:
        """
        Create a concise prompt for resume scoring across dimensions.
        Uses structured ROLE/TASK/INSTRUCTIONS format.
        """
        profile = self._build_candidate_profile(resume_data)

        return f"""
ROLE: Expert Resume Evaluator
TASK: Score resume across 5 dimensions with concise assessment
INSTRUCTIONS: Reasoning MUST be 1-2 sentences max. Strengths/weaknesses top 3 only. Be direct and concise.

CANDIDATE RESUME:
Skills: {profile['skills']}
Experience: {profile['experience']}
Education: {profile['education']}

SCORING RUBRIC:
- Technical Skills (0-100): Relevance, depth, and currency
- Experience (0-100): Quality, relevance, career progression
- Education (0-100): Relevance to goals, academic achievements
- Communication (0-100): Clarity of writing, presentation
- Overall Score: Weighted (Tech 30%, Exp 35%, Edu 20%, Comm 15%)

RESPONSE_SCHEMA:
{{
  "overall_score": <float>,
  "technical_score": <float>,
  "experience_score": <float>,
  "education_score": <float>,
  "communication_score": <float>,
  "reasoning": "<1-2 sentences max: key assessment>",
  "strengths": ["<top strength>", "<second>", "<third>"],
  "weaknesses": ["<top weakness>", "<second>", "<third>"],
  "improvement_suggestions": ["<actionable step 1>", "<step 2>", "<step 3>"]
}}

OUTPUT: Return ONLY valid JSON. Concise only.
"""

    def _create_personality_prompt(self, resume_data: Dict[str, Any]) -> str:
        """
        Create a concise prompt for personality analysis from resume indicators.
        Uses structured ROLE/TASK/INSTRUCTIONS format.
        """
        profile = self._build_candidate_profile(resume_data)

        return f"""
ROLE: Personality and Work Style Analyst
TASK: Infer personality traits and work preferences from resume
INSTRUCTIONS: Use resume indicators (achievements, roles, skills) to score traits. Analysis MUST be 2-3 sentences max.

RESUME SUMMARY:
Experience: {profile['experience']}
Education: {profile['education']}
Skills: {profile['skills']}

PERSONALITY DIMENSIONS (0-100 scale):
- Extraversion: Social orientation, outgoing vs reserved
- Conscientiousness: Organization, discipline, reliability
- Openness: Curiosity, innovation, comfort with change
- Agreeableness: Cooperation, empathy, teamwork
- Emotional Stability: Resilience, calm under pressure

WORK PREFERENCES:
- Work Style: "Independent", "Collaborative", "Leadership", "Analytical", "Creative"
- Leadership Potential: 0-100 based on track record
- Team Player Score: 0-100 based on collaboration indicators

RESPONSE_SCHEMA:
{{
  "traits": {{
    "extraversion": <0-100>,
    "conscientiousness": <0-100>,
    "openness": <0-100>,
    "agreeableness": <0-100>,
    "emotional_stability": <0-100>
  }},
  "work_style": "<one of the 5 options>",
  "leadership_potential": <0-100>,
  "team_player_score": <0-100>,
  "analysis": "<2-3 sentences: key personality insights derived from resume>"
}}

OUTPUT: Return ONLY valid JSON. Be concise and direct.
"""

    def _create_career_prompt(self, resume_data: Dict[str, Any]) -> str:
        """
        Create a concise prompt for career path prediction.
        Uses structured ROLE/TASK/INSTRUCTIONS format.
        """
        profile = self._build_candidate_profile(resume_data)
        experience = resume_data.get("workExperience", [])
        years_exp = len(experience) * 2  # Rough estimate

        return f"""
ROLE: Career Development Expert
TASK: Predict career progression and next opportunities
INSTRUCTIONS: Identify current level, top 3 next roles, timeline, and key skill gaps. Be direct and actionable.

CANDIDATE PROFILE:
Skills: {profile['skills']}
Current Role: {experience[0].get('title', 'Entry Level') if experience else 'Entry Level'}
Years of Experience: Approximately {years_exp}
Education: {profile['education']}

ANALYSIS REQUIREMENTS:
1. Current career level: "Entry Level", "Mid Level", "Senior Level", or "Executive"
2. Next 3 potential roles (top opportunity first)
3. Advancement timeline based on skill/experience gaps
4. Key skill developments needed for progression

RESPONSE_SCHEMA:
{{
  "current_level": "<one of the 4 levels>",
  "next_roles": ["<top opportunity>", "<second option>", "<third option>"],
  "timeline": "<e.g., '2-3 years' for next advancement>",
  "required_development": ["<skill gap 1>", "<skill gap 2>", "<skill gap 3>"]
}}

OUTPUT: Return ONLY valid JSON. Be specific and actionable.
"""

    def _create_preparation_plan_prompt(
        self,
        resume_data: Dict[str, Any],
        target_role: str,
        job_description: Optional[str] = None
    ) -> str:
        """
        Create a comprehensive prompt for generating role-specific preparation plan.
        Combines resume analysis, job requirements, and skill gap analysis.
        """
        profile = self._build_candidate_profile(resume_data)
        experience = resume_data.get("workExperience", [])
        
        job_desc_section = f"\n\nJOB DESCRIPTION:\n{job_description}" if job_description else ""
        current_role = experience[0].get('title', 'Entry Level') if experience else 'Entry Level'

        return f"""
ROLE: Professional Career Coach and Interview Preparation Specialist
TASK: Generate a comprehensive preparation plan for the target role
INSTRUCTIONS: Analyze candidate's current profile, identify skill gaps, and provide specific, actionable preparation tips for success.

CANDIDATE CURRENT PROFILE:
Name: {profile['personal_info']['name']}
Current Role: {current_role}
Skills: {profile['skills']}
Experience: {profile['experience']}
Education: {profile['education']}

TARGET ROLE: {target_role}{job_desc_section}

PREPARATION ANALYSIS REQUIREMENTS:
1. Role Fit Assessment: Evaluate how well candidate's background matches target role
2. Critical Skill Gaps: Identify top 3-5 skills needed for success that candidate lacks
3. Personality Alignment: Assess if candidate's personality traits suit the role
4. Strength Leverage: Identify top 3 existing strengths to highlight
5. Development Areas: Specific weaknesses to address before applying
6. Preparation Timeline: Realistic timeline for getting role-ready
7. Specific Tips: Actionable steps for the next 30/60/90 days
8. Interview Preparation: Key points to emphasize
9. Resume Improvements: Specific resume updates for target role
10. Success Metrics: How to know candidate is ready for the role

RESPONSE_SCHEMA:
{{
  "role_fit_score": <0-100>,
  "role_fit_assessment": "<1-2 sentences: overall fit evaluation>",
  "critical_skill_gaps": [
    {{
      "skill": "<skill name>",
      "importance": "Critical|High|Medium",
      "how_to_develop": "<specific action>"
    }}
  ],
  "personality_alignment": {{
    "aligned_traits": ["<trait 1>", "<trait 2>"],
    "traits_to_develop": ["<trait 1>", "<trait 2>"],
    "personality_tips": "<1-2 sentences on personality preparation>"
  }},
  "strengths_to_leverage": [
    {{
      "strength": "<strength name>",
      "how_to_highlight": "<specific way to emphasize in interview/resume>"
    }}
  ],
  "development_areas": [
    {{
      "weakness": "<weakness or gap>",
      "action_plan": "<specific improvement steps>"
    }}
  ],
  "preparation_timeline": {{
    "immediate_30_days": ["<action 1>", "<action 2>", "<action 3>"],
    "next_60_days": ["<action 1>", "<action 2>"],
    "final_30_days": ["<action 1>", "<action 2>"]
  }},
  "interview_preparation": {{
    "key_points_to_emphasize": ["<point 1>", "<point 2>", "<point 3>"],
    "common_interview_questions": ["<question 1>", "<question 2>"],
    "best_answers_outline": "<brief outline for answering>"
  }},
  "resume_improvements": [
    {{
      "section": "<Resume Section>",
      "current_gap": "<what's missing>",
      "improvement": "<specific update to add>"
    }}
  ],
  "success_metrics": {{
    "skill_readiness": "<specific criteria to demonstrate mastery>",
    "experience_requirements": "<how to frame existing experience>",
    "confidence_checklist": ["<item 1>", "<item 2>", "<item 3>"]
  }},
  "estimated_readiness_timeline": "<e.g., '3-4 months of consistent preparation'>",
  "motivation_summary": "<2-3 sentences: encouraging message with realistic goals>"
}}

OUTPUT: Return ONLY valid JSON. Be specific, actionable, and encouraging while realistic about requirements.
"""

    # ========== RESPONSE PARSING METHODS ==========

    def _parse_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse role recommendations from AI response.
        JSON mode guarantees valid JSON, so just parse and return.
        Pydantic validation in generate() method will catch any structural issues.
        
        Args:
            response_text: Raw response text from AI model (guaranteed valid JSON)
            
        Returns:
            List of parsed recommendation dictionaries
        """
        return self.parse_json_array_response(response_text)

    def _parse_score_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse resume score response using base class JSON parsing.
        JSON mode guarantees valid JSON structure.
        
        Args:
            response_text: Raw response text from AI model
            
        Returns:
            Parsed score dictionary
        """
        return self.parse_json_response(response_text)

    def _parse_personality_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse personality insights response using base class JSON parsing.
        JSON mode guarantees valid JSON structure.
        
        Args:
            response_text: Raw response text from AI model
            
        Returns:
            Parsed personality dictionary
        """
        return self.parse_json_response(response_text)

    def _parse_career_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse career path prediction response using base class JSON parsing.
        JSON mode guarantees valid JSON structure.
        
        Args:
            response_text: Raw response text from AI model
            
        Returns:
            Parsed career path dictionary
        """
        return self.parse_json_response(response_text)

    def _parse_preparation_plan_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse role-specific preparation plan response using base class JSON parsing.
        JSON mode guarantees valid JSON structure.
        
        Args:
            response_text: Raw response text from AI model
            
        Returns:
            Parsed preparation plan dictionary with comprehensive role guidance
        """
        return self.parse_json_response(response_text)
