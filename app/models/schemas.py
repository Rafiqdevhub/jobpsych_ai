from pydantic import BaseModel
from typing import List, Optional

class PersonalInfo(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class Experience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[List[str]] = []

class Education(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    details: Optional[List[str]] = None

class ResumeData(BaseModel):
    personalInfo: PersonalInfo
    workExperience: List[Experience]
    education: List[Education]
    skills: List[str]
    highlights: List[str]

class Question(BaseModel):
    type: str  # "technical" | "behavioral" | "experience"
    question: str
    context: str

class ResumeAnalysisResponse(BaseModel):
    resumeData: ResumeData
    questions: List[Question]
