from typing import Dict, List, Any, Set
import re
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class JobDescriptionParser:
    """
    Advanced job description parser using Hugging Face Transformers.
    Extracts required skills, qualifications, and job requirements.
    """

    def __init__(self):
        # Initialize models
        self._initialize_models()

        # Skills database (same as resume parser for consistency)
        self.skills_database = self._load_skills_database()

        # Job-specific keywords
        self.job_keywords = self._load_job_keywords()

    def _initialize_models(self):
        """Initialize Hugging Face models."""
        try:
            # Use a lightweight model for keyword extraction
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            self.model = AutoModel.from_pretrained("distilbert-base-uncased")

            # Keyword extraction pipeline
            self.keyword_pipeline = pipeline(
                "feature-extraction",
                model=self.model,
                tokenizer=self.tokenizer
            )

            print("✅ Job description parser models initialized successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize job description models: {e}")
            self.keyword_pipeline = None

    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load comprehensive skills database."""
        return {
            "programming_languages": [
                "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby", "go", "rust",
                "swift", "kotlin", "scala", "perl", "r", "matlab", "shell", "bash", "powershell"
            ],
            "web_technologies": [
                "html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask",
                "spring", "asp.net", "jquery", "bootstrap", "sass", "less", "webpack", "babel"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle", "sql server",
                "sqlite", "cassandra", "dynamodb", "firebase", "couchdb"
            ],
            "cloud_platforms": [
                "aws", "azure", "google cloud", "heroku", "digitalocean", "linode", "vercel",
                "netlify", "firebase", "cloudflare"
            ],
            "devops_tools": [
                "docker", "kubernetes", "jenkins", "gitlab ci", "github actions", "terraform",
                "ansible", "puppet", "chef", "nginx", "apache", "linux", "ubuntu", "centos"
            ],
            "data_science": [
                "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "jupyter",
                "matplotlib", "seaborn", "tableau", "power bi", "apache spark", "hadoop"
            ],
            "soft_skills": [
                "leadership", "communication", "problem solving", "teamwork", "project management",
                "agile", "scrum", "kanban", "time management", "analytical thinking"
            ]
        }

    def _load_job_keywords(self) -> Dict[str, List[str]]:
        """Load job-specific keywords and requirements."""
        return {
            "required": [
                "required", "must have", "essential", "mandatory", "need to have",
                "should have", "preferable", "preferred", "nice to have"
            ],
            "experience": [
                "experience", "years of experience", "proven experience", "demonstrated experience",
                "background in", "familiarity with", "knowledge of", "understanding of"
            ],
            "qualifications": [
                "qualification", "degree", "certificate", "certification", "diploma",
                "bachelor", "master", "phd", "education"
            ],
            "responsibilities": [
                "responsibility", "duty", "role", "task", "function", "objective",
                "deliverable", "outcome", "goal"
            ]
        }

    def parse(self, job_description: str) -> Dict[str, Any]:
        """
        Parse job description and extract structured information.

        Args:
            job_description (str): The job description text

        Returns:
            Dict containing:
            - required_skills: List of required technical skills
            - preferred_skills: List of preferred skills
            - experience_level: Estimated experience level
            - qualifications: List of required qualifications
            - responsibilities: List of key responsibilities
            - job_title: Extracted job title
        """
        if not job_description or not job_description.strip():
            return self._get_empty_result()

        # Clean and preprocess text
        cleaned_text = self._preprocess_text(job_description)

        # Extract job components
        result = {
            "job_title": self._extract_job_title(cleaned_text),
            "required_skills": self._extract_required_skills(cleaned_text),
            "preferred_skills": self._extract_preferred_skills(cleaned_text),
            "experience_level": self._extract_experience_level(cleaned_text),
            "qualifications": self._extract_qualifications(cleaned_text),
            "responsibilities": self._extract_responsibilities(cleaned_text),
            "benefits": self._extract_benefits(cleaned_text)
        }

        return result

    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess the job description text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', ' ', text)

        return text.strip()

    def _extract_job_title(self, text: str) -> str:
        """Extract job title from the description."""
        # Look for common job title patterns at the beginning
        lines = text.split('\n')[:5]  # Check first 5 lines

        for line in lines:
            line = line.strip()
            if len(line) < 100 and len(line) > 3:  # Reasonable title length
                # Skip lines that are clearly not titles
                if not any(word in line.lower() for word in [
                    'company', 'location', 'salary', 'about', 'we are', 'join', 'looking for'
                ]):
                    return line.title()

        # Fallback: look for common job title patterns
        title_patterns = [
            r'(?:Job Title|Position|Role):\s*([^\n]+)',
            r'(?:We are hiring|We\'re looking for)\s+(?:a|an)?\s*([^\n]+)',
            r'^([A-Z][^.\n]{10,50})(?:\n|\.)'
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip().title()

        return "Position Title Not Found"

    def _extract_required_skills(self, text: str) -> List[str]:
        """Extract required technical skills."""
        required_skills = set()
        text_lower = text.lower()

        # Find sections that indicate requirements
        requirement_sections = self._find_requirement_sections(text)

        for section in requirement_sections:
            section_lower = section.lower()

            # Check against skills database
            for category, skills in self.skills_database.items():
                for skill in skills:
                    if skill.lower() in section_lower:
                        # Check if it's in a "required" context
                        if self._is_required_context(section):
                            required_skills.add(skill.title())

            # Extract additional skills using patterns
            skill_patterns = [
                r'\b(proficient|experienced|skilled|strong)\s+in\s+([a-zA-Z\s+#]+)',
                r'\b([a-zA-Z\s+#]+)\s+(?:experience|knowledge|skills?)',
                r'\b(?:using|with|knowledge of)\s+([a-zA-Z\s+#]+)'
            ]

            for pattern in skill_patterns:
                matches = re.findall(pattern, section, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        skill = match[1] if len(match) > 1 else match[0]
                    else:
                        skill = match

                    skill = skill.strip().title()
                    if len(skill) > 2 and self._is_technical_skill(skill):
                        required_skills.add(skill)

        return list(required_skills)

    def _extract_preferred_skills(self, text: str) -> List[str]:
        """Extract preferred/nice-to-have skills."""
        preferred_skills = set()
        text_lower = text.lower()

        # Look for "preferred" or "nice to have" sections
        preferred_sections = self._find_preferred_sections(text)

        for section in preferred_sections:
            section_lower = section.lower()

            # Check against skills database
            for category, skills in self.skills_database.items():
                for skill in skills:
                    if skill.lower() in section_lower:
                        preferred_skills.add(skill.title())

        return list(preferred_skills)

    def _extract_experience_level(self, text: str) -> str:
        """Extract experience level requirements."""
        text_lower = text.lower()

        # Look for experience indicators
        if re.search(r'\b(5\+|6\+|7\+|8\+|9\+|10\+)\s+years?\b', text_lower):
            return "Senior/Lead"
        elif re.search(r'\b(3\+|4\+)\s+years?\b', text_lower):
            return "Mid-level"
        elif re.search(r'\b(1\+|2\+)\s+years?\b', text_lower):
            return "Junior"
        elif re.search(r'\b(entry[- ]level|graduate|fresh)\b', text_lower):
            return "Entry-level"
        elif re.search(r'\b(senior|lead|principal|architect)\b', text_lower):
            return "Senior/Lead"
        else:
            return "Mid-level"  # Default assumption

    def _extract_qualifications(self, text: str) -> List[str]:
        """Extract educational and certification requirements."""
        qualifications = []
        text_lower = text.lower()

        # Education requirements
        education_patterns = [
            r'\b(bachelor|master|phd|doctorate|mba|msc|bsc|ba|ma)\b.*?[^\n]*',
            r'\b(degree|diploma|certificate)\s+in\s+[^\n]*',
            r'\b(?:computer science|engineering|business|mathematics|physics|chemistry)\b.*?[^\n]*'
        ]

        for pattern in education_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 5:
                    qualifications.append(match.strip().title())

        # Certification requirements
        cert_patterns = [
            r'\b(?:aws|azure|gcp|google cloud|microsoft|compTIA|cisco|red hat)\s+(?:certified|certification)\b',
            r'\b(?:pmp|csm|cspo|cissp|ceh|ccna|ccnp)\b'
        ]

        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                qualifications.append(match.upper())

        return list(set(qualifications))

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities."""
        responsibilities = []

        # Look for responsibility sections
        resp_sections = self._find_responsibility_sections(text)

        for section in resp_sections:
            # Split into bullet points or sentences
            items = re.split(r'[•\-\*\+\n]', section)

            for item in items:
                item = item.strip()
                if len(item) > 20 and len(item) < 200:  # Reasonable length
                    # Clean up the item
                    item = re.sub(r'^[•\-\*\+\s]*', '', item)
                    if item:
                        responsibilities.append(item)

        return responsibilities[:10]  # Limit to top 10

    def _extract_benefits(self, text: str) -> List[str]:
        """Extract job benefits and perks."""
        benefits = []
        text_lower = text.lower()

        # Common benefit keywords
        benefit_keywords = [
            'health insurance', 'dental', 'vision', '401k', 'retirement',
            'remote work', 'flexible hours', 'vacation', 'pto', 'bonus',
            'stock options', 'professional development', 'training',
            'gym membership', 'free lunch', 'catered meals'
        ]

        for keyword in benefit_keywords:
            if keyword in text_lower:
                benefits.append(keyword.title())

        return benefits

    def _find_requirement_sections(self, text: str) -> List[str]:
        """Find sections that contain requirements."""
        sections = []

        # Split text into sections based on headers
        section_headers = [
            r'requirements?', r'qualifications?', r'skills?', r'experience',
            r'what you\'ll need', r'what we\'re looking for', r'must have'
        ]

        lines = text.split('\n')
        current_section = []
        in_requirements = False

        for line in lines:
            line_lower = line.lower().strip()

            # Check if this is a requirements header
            if any(re.search(header, line_lower) for header in section_headers):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_requirements = True
            elif in_requirements and line.strip():
                current_section.append(line)
            elif in_requirements and not line.strip():
                # Empty line might indicate end of section
                if len(current_section) > 1:
                    sections.append('\n'.join(current_section))
                    in_requirements = False
                    current_section = []

        # Add the last section if it exists
        if current_section:
            sections.append('\n'.join(current_section))

        return sections

    def _find_preferred_sections(self, text: str) -> List[str]:
        """Find sections that contain preferred skills."""
        sections = []

        # Look for "preferred", "nice to have", etc.
        preferred_headers = [
            r'preferred', r'nice to have', r'plus', r'bonus', r'additional'
        ]

        lines = text.split('\n')
        current_section = []
        in_preferred = False

        for line in lines:
            line_lower = line.lower().strip()

            if any(header in line_lower for header in preferred_headers):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_preferred = True
            elif in_preferred and line.strip():
                current_section.append(line)

        if current_section:
            sections.append('\n'.join(current_section))

        return sections

    def _find_responsibility_sections(self, text: str) -> List[str]:
        """Find sections that contain responsibilities."""
        sections = []

        resp_headers = [
            r'responsibilities?', r'duties', r'role', r'what you\'ll do',
            r'job description', r'tasks'
        ]

        lines = text.split('\n')
        current_section = []
        in_responsibilities = False

        for line in lines:
            line_lower = line.lower().strip()

            if any(re.search(header, line_lower) for header in resp_headers):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_responsibilities = True
            elif in_responsibilities and line.strip():
                current_section.append(line)

        if current_section:
            sections.append('\n'.join(current_section))

        return sections

    def _is_required_context(self, text: str) -> bool:
        """Check if text is in a required context."""
        required_words = ['required', 'must', 'essential', 'mandatory', 'need']
        text_lower = text.lower()

        return any(word in text_lower for word in required_words)

    def _is_technical_skill(self, skill: str) -> bool:
        """Check if a skill is technical."""
        non_technical = [
            'the', 'and', 'for', 'are', 'but', 'not', 'with', 'from',
            'this', 'that', 'will', 'have', 'been', 'were', 'they',
            'team', 'work', 'project', 'management', 'communication'
        ]

        skill_lower = skill.lower()
        return skill_lower not in non_technical and len(skill) > 2

    def _get_empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "job_title": "",
            "required_skills": [],
            "preferred_skills": [],
            "experience_level": "Unknown",
            "qualifications": [],
            "responsibilities": [],
            "benefits": []
        }
