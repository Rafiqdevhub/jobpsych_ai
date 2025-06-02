from typing import Dict, List, Any
import google.generativeai as genai
from app.models.schemas import Question

class QuestionGenerator:
    async def generate(self, resume_data: Dict[str, Any]) -> List[Question]:
        """Generate interview questions based on resume data"""
        # Get the most capable model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create a detailed prompt using resume data
        prompt = self._create_prompt(resume_data)
        
        # Generate questions using Gemini
        response = await model.generate_content_async(prompt)
        
        # Parse and format the response
        try:
            raw_questions = self._parse_questions(response.text)
            # Convert to Question objects
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
        """Create a detailed prompt for question generation"""
        skills = ", ".join(resume_data.get("skills", []))
        experience = "\n".join([
            f"- {exp['title']} at {exp['company']}" 
            for exp in resume_data.get("workExperience", [])
        ])
        education = "\n".join([
            f"- {edu['degree']} from {edu['institution']}"
            for edu in resume_data.get("education", [])
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
