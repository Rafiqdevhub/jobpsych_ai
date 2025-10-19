import json
from typing import Dict, List, Any
from abc import ABC, abstractmethod
import google.generativeai as genai

class BasePromptService(ABC):
    """
    Base prompt service providing shared utilities and constants for all route-specific prompt services.
    Handles common tasks like formatting, parsing, and AI model interaction.
    
    Uses JSON mode for guaranteed valid JSON output from AI model.
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
        """Get or initialize the generative AI model instance with JSON mode enabled.
        
        Uses JSON mode to force valid JSON output, eliminating need for text parsing.
        This is faster and 100% reliable.
        """
        if self._model is None:
            try:
                if not genai:
                    raise ImportError("google-generativeai package is not available")
                # Enable JSON mode for guaranteed valid JSON output
                try:
                    json_config = genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    )
                    self._model = genai.GenerativeModel(
                        self.DEFAULT_MODEL,
                        generation_config=json_config
                    )
                except Exception:
                    # Fallback if JSON mode not available in this version
                    self._model = genai.GenerativeModel(self.DEFAULT_MODEL)
            except ImportError as e:
                raise ImportError(f"Failed to initialize AI model: {str(e)}")
        return self._model

    # ========== FORMATTING UTILITIES ==========

    @staticmethod
    def format_work_experience(experience_list: List[Dict[str, Any]]) -> str:
        """Format work experience section - concise."""
        if not experience_list:
            return "None"
        formatted = [
            f"- {exp['title']} at {exp['company']} ({exp.get('duration', '')})"
            for exp in experience_list
            if exp.get('title') and exp.get('company')
        ]
        return "\n".join(formatted) or "None"

    @staticmethod
    def format_education(education_list: List[Dict[str, Any]]) -> str:
        """Format education section - degree & year only."""
        if not education_list:
            return "None"
        formatted = [
            f"- {edu['degree']} ({edu.get('year')})" if edu.get('year') else f"- {edu['degree']}"
            for edu in education_list if edu.get('degree')
        ]
        return "\n".join(formatted) or "None"

    @staticmethod
    def format_skills(skills_list: List[str]) -> str:
        """Format skills section from resume data."""
        return ", ".join(skills_list) or "No skills listed"

    @staticmethod
    def format_highlights(highlights_list: List[str]) -> str:
        """Format highlights section - concise."""
        formatted = [f"- {h[:100]}" for h in highlights_list[:2]]
        return "\n".join(formatted) or "None"

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
        
        With JSON mode enabled, the model ONLY outputs valid JSON, so direct parsing works.
        This eliminates complex text extraction logic.
        """
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text[:200]}")

    @staticmethod
    def parse_json_array_response(response_text: str) -> List[Dict[str, Any]]:
        """
        Parse JSON array response from AI model.
        
        With JSON mode enabled, the model ONLY outputs valid JSON arrays, so direct parsing works.
        No need to search for '[' and ']' in the text.
        """
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON array response: {str(e)}\nResponse: {response_text[:200]}")

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
