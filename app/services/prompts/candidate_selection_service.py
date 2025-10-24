import json
from typing import Dict, Any, List
from app.services.prompts.base_prompt_service import BasePromptService


class CandidateSelectionService(BasePromptService):
    def __init__(self):
        super().__init__()

    async def generate(self, resume_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Required implementation of abstract method.
        For candidate selection, use evaluate_candidate directly.
        """
        raise NotImplementedError(
            "Use evaluate_candidate method directly for candidate selection"
        )

    def _create_fit_evaluation_prompt(
        self, resume_content: str, job_title: str, keywords: List[str]
    ) -> str:
        """
        Create a prompt to evaluate if a candidate fits the job based on keywords.
        Returns JSON with status and brief message.
        """
        keywords_str = ", ".join(keywords)
        
        prompt = f"""You are a recruitment expert evaluating candidates for a position.

Job Title: {job_title}
Required Keywords/Skills: {keywords_str}

Resume Content:
{resume_content}

Evaluate if this candidate is a FIT or REJECT based on whether their resume contains the required keywords/skills.

Respond ONLY with valid JSON in this exact format:
{{
    "status": "FIT" or "REJECT",
    "message": "Brief one-line reason (max 100 characters)"
}}

Rules:
- FIT: Candidate has most/all required keywords/skills mentioned in their resume
- REJECT: Candidate is missing most required keywords/skills
- Message should be concise and actionable
- Do NOT include any text outside the JSON"""

        return prompt

    async def evaluate_candidate(
        self, resume_content: str, job_title: str, keywords: List[str]
    ) -> Dict[str, str]:
        """
        Evaluate a single candidate and return FIT/REJECT decision with message.
        
        Args:
            resume_content: Extracted text from resume
            job_title: Target job position
            keywords: List of required skills/keywords
            
        Returns:
            Dict with 'status' ("FIT" or "REJECT") and 'message' (brief reason)
        """
        try:
            model = self.model
            prompt = self._create_fit_evaluation_prompt(resume_content, job_title, keywords)
            
            response = await model.generate_content_async(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from AI model")

            result = self._parse_selection_response(response.text)
            return result
        except Exception as e:
            raise ValueError(f"Failed to evaluate candidate: {str(e)}")

    def _parse_selection_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse AI response to extract status and message.
        
        Args:
            response_text: Raw response from Gemini AI
            
        Returns:
            Dict with 'status' and 'message' keys
        """
        try:
            # Try to extract JSON from response
            json_str = response_text.strip()
            
            # If response is wrapped in markdown code blocks, extract the JSON
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            data = json.loads(json_str)
            
            # Validate required fields
            status = data.get("status", "").upper()
            if status not in ["FIT", "REJECT"]:
                status = "REJECT"  # Default to reject if invalid
            
            message = data.get("message", "Could not evaluate")
            
            return {
                "status": status,
                "message": message[:100]  # Limit to 100 chars
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            if "reject" in response_text.lower():
                return {"status": "REJECT", "message": "Could not fully evaluate"}
            return {"status": "FIT", "message": "Could not fully evaluate"}
        except Exception as e:
            return {"status": "REJECT", "message": "Evaluation error"}
