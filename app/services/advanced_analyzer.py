from typing import Dict, List, Any, Optional
import os
from app.models.schemas import ResumeScore, PersonalityInsights, CareerPathPrediction

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

class AdvancedAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        if not GENAI_AVAILABLE or not genai:
            raise ImportError("google-generativeai package is not available")

        genai.configure(api_key=self.api_key)

    async def calculate_resume_score(self, resume_data: Dict[str, Any]) -> ResumeScore:
        """Calculate comprehensive resume score with detailed breakdown"""
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = self._create_scoring_prompt(resume_data)
        response = await model.generate_content_async(prompt)

        try:
            score_data = self._parse_score_response(response.text)
            return ResumeScore(**score_data)
        except Exception as e:
            raise ValueError(f"Failed to calculate resume score: {str(e)}")

    async def analyze_personality(self, resume_data: Dict[str, Any]) -> PersonalityInsights:
        """Analyze personality traits from resume content"""
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = self._create_personality_prompt(resume_data)
        response = await model.generate_content_async(prompt)

        try:
            personality_data = self._parse_personality_response(response.text)
            return PersonalityInsights(**personality_data)
        except Exception as e:
            raise ValueError(f"Failed to analyze personality: {str(e)}")

    async def predict_career_path(self, resume_data: Dict[str, Any]) -> CareerPathPrediction:
        """Predict career progression and next steps"""
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = self._create_career_prompt(resume_data)
        response = await model.generate_content_async(prompt)

        try:
            career_data = self._parse_career_response(response.text)
            return CareerPathPrediction(**career_data)
        except Exception as e:
            raise ValueError(f"Failed to predict career path: {str(e)}")

    def _create_scoring_prompt(self, resume_data: Dict[str, Any]) -> str:
        skills = ", ".join(resume_data.get("skills", []))
        experience = "\n".join([
            f"- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})"
            for exp in resume_data.get("workExperience", [])
        ])
        education = "\n".join([
            f"- {edu.get('degree', '')} from {edu.get('institution', '')}"
            for edu in resume_data.get("education", [])
        ])

        return f"""
You are an expert HR analyst and resume evaluator. Analyze this resume and provide a comprehensive scoring breakdown.

CANDIDATE RESUME:
Skills: {skills}
Experience: {experience}
Education: {education}

Calculate scores (0-100) for:
- Technical Skills: Based on relevance, depth, and currency of technical skills
- Experience: Quality and relevance of work experience, career progression
- Education: Relevance of education to career goals, academic achievements
- Communication: Clarity of resume writing, presentation skills evident

Overall Score: Weighted average (Technical 30%, Experience 35%, Education 20%, Communication 15%)

Provide detailed reasoning and specific suggestions for improvement.

Return in JSON format:
{{
  "overall_score": 85.5,
  "technical_score": 88.2,
  "experience_score": 82.7,
  "education_score": 90.1,
  "communication_score": 78.4,
  "reasoning": "Detailed explanation of scoring methodology and overall assessment",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "weaknesses": ["Weakness 1", "Weakness 2"],
  "improvement_suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
}}
"""

    def _create_personality_prompt(self, resume_data: Dict[str, Any]) -> str:
        # Extract text content for personality analysis
        highlights = " ".join(resume_data.get("highlights", []))
        experience_desc = " ".join([
            " ".join(exp.get("description", []))
            for exp in resume_data.get("workExperience", [])
        ])

        content = f"{highlights} {experience_desc}"

        return f"""
Analyze the following resume content and infer personality traits and work style preferences.

RESUME CONTENT: {content}

Assess these personality dimensions (0-100 scale):
- Extraversion: Outgoing vs reserved
- Conscientiousness: Organized vs spontaneous
- Openness: Curious vs practical
- Agreeableness: Cooperative vs competitive
- Emotional Stability: Calm vs anxious

Also determine:
- Work Style: "Independent", "Collaborative", "Leadership", "Analytical", "Creative"
- Leadership Potential (0-100)
- Team Player Score (0-100)

Provide analysis explaining how you derived these insights from the resume content.

Return in JSON format:
{{
  "traits": {{
    "extraversion": 75.3,
    "conscientiousness": 82.1,
    "openness": 68.7,
    "agreeableness": 79.4,
    "emotional_stability": 71.2
  }},
  "work_style": "Collaborative",
  "leadership_potential": 78.5,
  "team_player_score": 85.2,
  "analysis": "Detailed explanation of personality assessment based on resume content"
}}
"""

    def _create_career_prompt(self, resume_data: Dict[str, Any]) -> str:
        skills = ", ".join(resume_data.get("skills", []))
        experience = resume_data.get("workExperience", [])
        education = resume_data.get("education", [])

        current_role = experience[0].get("title", "Entry Level") if experience else "Entry Level"
        years_exp = len(experience) * 2  # Rough estimate

        return f"""
You are a career development expert. Based on this candidate's background, predict their career progression.

CURRENT PROFILE:
Skills: {skills}
Current Role Level: {current_role}
Years of Experience: Approximately {years_exp}
Education: {[edu.get('degree', '') for edu in education]}

Predict:
1. Current career level: "Entry Level", "Mid Level", "Senior Level", "Executive"
2. Next 3 potential career roles they could progress to
3. Timeline for advancement (1-3 years, 3-5 years, etc.)
4. Key skills/developments needed for next level


Consider industry trends, skill requirements, and typical career paths.

Return in JSON format:
{{
  "current_level": "Mid Level",
  "next_roles": ["Senior Developer", "Tech Lead", "Engineering Manager"],
  "timeline": "2-4 years for next advancement",
  "required_development": ["Leadership skills", "Advanced technical expertise", "Project management"],
 
}}
"""

    def _parse_score_response(self, text: str) -> Dict[str, Any]:
        import json
        import re

        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in score response")

        return json.loads(json_match.group())

    def _parse_personality_response(self, text: str) -> Dict[str, Any]:
        import json
        import re

        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in personality response")

        return json.loads(json_match.group())

    def _parse_career_response(self, text: str) -> Dict[str, Any]:
        import json
        import re

        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in career response")

        return json.loads(json_match.group())