from typing import Dict, List, Any
from app.models.schemas import Question
import os

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

class QuestionGenerator:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
            
        if not GENAI_AVAILABLE or not genai:
            raise ImportError("google-generativeai package is not available")
            
        genai.configure(api_key=self.api_key)

    async def generate(self, resume_data: Dict[str, Any]) -> List[Question]:
        """Generate interview questions based on resume data"""
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = self._create_prompt(resume_data)

        response = await model.generate_content_async(prompt)

        try:
            raw_questions = self._parse_questions(response.text)
            questions = [
                Question(
                    type=q["type"],
                    question=q["question"],
                    context=q.get("context", "Generated based on resume analysis")
                )
                for q in raw_questions
            ]
            return questions
        except Exception as e:
            raise ValueError(f"Failed to generate questions: {str(e)}")

    def _create_prompt(self, resume_data: Dict[str, Any]) -> str:
        """Create a detailed and specific prompt for question generation"""
        skills = ", ".join(resume_data.get("skills", []))
        experience = "\n".join([
            f"- {exp.get('title', '')} at {exp.get('company', '')}"
            for exp in resume_data.get("workExperience", [])
        ])
        education = "\n".join([
            f"- {edu.get('degree', '')} from {edu.get('institution', '')}"
            for edu in resume_data.get("education", [])
        ])

        return f"""
You are an AI interviewer tasked with generating targeted and insightful interview questions tailored to a specific candidate's resume.

Below is the candidate’s profile:

Skills:
{skills}

Experience:
{experience}

Education:
{education}

Instructions:
1. Analyze the candidate’s resume deeply.
2. Generate 15 unique and specific interview questions, divided equally among the following categories:

   - Technical Skills (type: technical) — 5 questions based on the candidate's stated skills, tools, technologies, and any technical certifications or projects.
   - Behavioral & Cultural Fit (type: behavioral) — 5 questions aimed at understanding the candidate’s mindset, soft skills, team collaboration, adaptability, conflict resolution, and company culture fit.
   - Experience Validation (type: experience) — 5 questions derived directly from the candidate's work history, project outcomes, responsibilities, roles, achievements, or impact.

3. Questions should be deep, resume-specific, and test real-world understanding or decision-making.

Format each question as a JSON object with the following structure:
{{
  "type": "technical | behavioral | experience",
  "question": "The actual question text",
  "context": "Brief explanation of why this question is relevant based on specific parts of the resume"
}}

Return all questions as a JSON array.

Ensure the questions are:
- Diverse and non-repetitive
- Specific to the resume content
- Contextually grounded in the candidate's background
        """

    def _parse_questions(self, text: str) -> List[Dict[str, str]]:
        """Parse generated questions from the response text"""
        import json
        import re

        pattern = r'\[\s*{[\s\S]*?}\s*\]'
        matches = re.search(pattern, text)

        if not matches:
            raise ValueError("No valid question format found in response")

        try:
            questions_json = matches.group()
            questions = json.loads(questions_json)
            return questions
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse questions JSON: {str(e)}")
