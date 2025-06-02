from typing import Dict, List, Any
import google.generativeai as genai
from app.models.schemas import Question

class QuestionGenerator:
    async def generate(self, resume_data: Dict[str, Any]) -> List[Question]:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = await model.generate_content_async(self._create_prompt(resume_data))
        try:
            return [Question(
                type=q["type"],
                question=q["question"],
                context=q.get("context", "Based on resume")
            ) for q in self._parse_questions(response.text)]
        except Exception as e:
            raise ValueError(f"Failed to generate questions: {str(e)}")

    def _create_prompt(self, resume_data: Dict[str, Any]) -> str:
        skills = ", ".join(resume_data.get("skills", []))
        experience = "\n".join([
            f"- {exp.get('title')} at {exp.get('company')}" 
            for exp in resume_data.get("workExperience", []) if exp.get('title') and exp.get('company')
        ])
        education = "\n".join([
            f"- {edu.get('degree')} from {edu.get('institution')}"
            for edu in resume_data.get("education", []) if edu.get('degree') and edu.get('institution')
        ])
        
        return f"""
        Generate a comprehensive set of interview questions based on this candidate's profile:

        Skills: {skills}
        
        Experience:
        {experience}
        
        Education:
        {education}

        Generate 15 unique interview questions divided into these categories:
        1. Technical Skills (type: technical) - 5 questions based on their skills
        2. Behavioral & Cultural Fit (type: behavioral) - 5 questions
        3. Experience Validation (type: experience) - 5 questions based on their work history

        Format each question as JSON with these fields:
        {{
            "type": "technical|behavioral|experience",
            "question": "The actual question text",
            "context": "Why this question is relevant based on the resume"
        }}

        Return all questions in a JSON array.
        """

    def _parse_questions(self, text: str) -> List[Dict[str, str]]:
        """Parse generated questions from the response text"""
        import json
        import re
        
        # Find JSON array in the text using regex
        pattern = r'\[\s*{[\s\S]*}\s*\]'
        matches = re.search(pattern, text)
        
        if not matches:
            raise ValueError("No valid question format found in response")
            
        try:
            questions_json = matches.group()
            questions = json.loads(questions_json)
            return questions
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse questions JSON: {str(e)}")
