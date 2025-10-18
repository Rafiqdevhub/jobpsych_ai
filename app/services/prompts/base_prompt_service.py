import json
from typing import Dict, List, Any
from abc import ABC, abstractmethod
import google.generativeai as genai

class BasePromptService(ABC):
    """
    Base prompt service providing shared utilities and constants for all route-specific prompt services.
    Handles common tasks like formatting, parsing, and AI model interaction.
    """

    # ========== MODEL CONFIGURATIONS ==========
    DEFAULT_MODEL = "gemini-2.5-flash"
    ADVANCED_MODEL = "gemini-2.5-pro"
    
    # ========== FILE FORMAT VALIDATION ==========
    SUPPORTED_FORMATS = ('.pdf', '.doc', '.docx')
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    # ========== RATE LIMITING THRESHOLDS ==========
    WARNING_THRESHOLD_BATCHES = 10
    WARNING_THRESHOLD_COMPARISONS = 10

    def __init__(self):
        """Initialize base prompt service."""
        self._model = None

    @property
    def model(self):
        """Get or initialize the generative AI model instance."""
        if self._model is None:
            try:
                if not genai:
                    raise ImportError("google-generativeai package is not available")
                self._model = genai.GenerativeModel(self.DEFAULT_MODEL)
            except ImportError as e:
                raise ImportError(f"Failed to initialize AI model: {str(e)}")
        return self._model

    # ========== FORMATTING UTILITIES ==========

    @staticmethod
    def format_work_experience(experience_list: List[Dict[str, Any]]) -> str:
        """Format work experience section from resume data."""
        if not experience_list:
            return "No work experience listed"
        
        formatted = []
        for exp in experience_list:
            if exp.get('title') and exp.get('company'):
                duration = exp.get('duration', 'Unknown duration')
                line = f"- {exp['title']} at {exp['company']} ({duration})"
                formatted.append(line)
        
        return "\n".join(formatted) if formatted else "No work experience listed"

    @staticmethod
    def format_education(education_list: List[Dict[str, Any]]) -> str:
        """Format education section from resume data."""
        if not education_list:
            return "No education information"
        
        formatted = []
        for edu in education_list:
            if edu.get('degree'):
                institution = edu.get('institution', 'Unknown institution')
                year = edu.get('year', 'Unknown year')
                line = f"- {edu['degree']} from {institution} ({year})"
                formatted.append(line)
        
        return "\n".join(formatted) if formatted else "No education information"

    @staticmethod
    def format_skills(skills_list: List[str]) -> str:
        """Format skills section from resume data."""
        if not skills_list:
            return "No skills listed"
        return ", ".join(skills_list)

    @staticmethod
    def format_highlights(highlights_list: List[str]) -> str:
        """Format highlights section from resume data."""
        if not highlights_list:
            return "No highlights listed"
        formatted = [f"- {highlight}" for highlight in highlights_list]
        return "\n".join(formatted)

    @staticmethod
    def extract_personal_info(resume_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract personal information from resume data."""
        personal_info = resume_data.get("personalInfo", {})
        return {
            "name": personal_info.get("name", "Candidate"),
            "email": personal_info.get("email", "Not provided"),
            "phone": personal_info.get("phone", "Not provided"),
            "location": personal_info.get("location", "Not provided")
        }

    # ========== PARSING UTILITIES ==========

    @staticmethod
    def parse_json_response(response_text: str, start_marker: str = "{", end_marker: str = "}") -> Dict[str, Any]:
        """
        Parse JSON response from AI model.
        Handles cases where JSON is embedded in text.
        """
        try:
            # Try direct JSON parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response text
            start_idx = response_text.rfind(start_marker)
            end_idx = response_text.rfind(end_marker)
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_str = response_text[start_idx:end_idx + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    raise ValueError(f"Failed to parse JSON response: {response_text[:200]}")
            raise ValueError(f"No valid JSON found in response: {response_text[:200]}")

    @staticmethod
    def parse_json_array_response(response_text: str) -> List[Dict[str, Any]]:
        """
        Parse JSON array response from AI model.
        Handles cases where JSON array is embedded in text.
        """
        try:
            # Try direct JSON parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON array from response text
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]")
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_str = response_text[start_idx:end_idx + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    raise ValueError(f"Failed to parse JSON array response: {response_text[:200]}")
            raise ValueError(f"No valid JSON array found in response: {response_text[:200]}")

    # ========== VALIDATION UTILITIES ==========

    @staticmethod
    def validate_file_format(filename: str) -> bool:
        """Validate if file has supported format."""
        if not filename:
            return False
        return filename.lower().endswith(BasePromptService.SUPPORTED_FORMATS)

    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate if file is within size limit."""
        return file_size <= BasePromptService.MAX_FILE_SIZE

    # ========== ERROR HANDLING ==========

    @staticmethod
    def handle_file_error(error_message: str) -> str:
        """Convert error messages to user-friendly messages."""
        if "PDF" in error_message:
            return "Error reading PDF file. Please ensure it's not corrupted or password protected."
        elif "DOCX" in error_message or "DOC" in error_message:
            return "Error reading document file. Please ensure it's a valid Word document."
        else:
            return "Analysis failed. Please try again."

    # ========== ABSTRACT METHODS ==========

    @abstractmethod
    async def generate(self, resume_data: Dict[str, Any], **kwargs) -> Any:
        """Generate output based on prompt service logic. Must be implemented by subclasses."""
        pass
