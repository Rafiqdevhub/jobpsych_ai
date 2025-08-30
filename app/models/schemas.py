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

class RoleRecommendation(BaseModel):
    roleName: str
    matchPercentage: int
    reasoning: str
    requiredSkills: List[str] = []
    missingSkills: List[str] = []
    careerLevel: str = "Mid-level"
    industryFit: str = "Good"

class ResumeAnalysisResponse(BaseModel):
    resumeData: ResumeData
    questions: List[Question]
    roleRecommendations: List[RoleRecommendation]

# New schemas for hiring candidate analysis
class SkillGap(BaseModel):
    skill: str
    type: str  # "required" | "preferred" | "responsibility-based"
    priority: str  # "high" | "medium" | "low"
    reason: str
    category: str

class LearningResource(BaseModel):
    skill: str
    courses: List[str]
    platforms: List[str]
    difficulty: str

class ProjectSuggestion(BaseModel):
    skill: str
    project: str
    difficulty: str
    estimated_time: str

class LearningPlan(BaseModel):
    immediate_actions: List[dict]
    short_term_goals: List[dict]
    long_term_goals: List[dict]
    resources: List[LearningResource]
    projects: List[ProjectSuggestion]

class TimelineMilestone(BaseModel):
    week: Optional[int] = None
    month: Optional[int] = None
    achievement: str

class LearningTimeline(BaseModel):
    week_1_2: List[str]
    month_1_2: List[str]
    month_3_6: List[str]
    milestones: List[TimelineMilestone]

class CareerPathSuggestion(BaseModel):
    path: str
    reason: str
    next_steps: List[str]

class SkillsRecommendation(BaseModel):
    skill_gaps: List[SkillGap]
    learning_plan: LearningPlan
    prioritized_skills: List[SkillGap]
    timeline: LearningTimeline
    estimated_time: str
    career_path_suggestions: List[CareerPathSuggestion]

class SimilarityAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    skill_gaps: List[str]
    experience_alignment: str
    overall_assessment: str

class HiringCandidateAnalysis(BaseModel):
    overall_score: float
    semantic_similarity: float
    skills_match: float
    experience_match: float
    text_similarity: float
    analysis: SimilarityAnalysis
    recommendations: List[str]

class JobDescriptionData(BaseModel):
    job_title: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str
    qualifications: List[str]
    responsibilities: List[str]
    benefits: List[str]

class HiringCandidateResponse(BaseModel):
    resume_data: ResumeData
    job_data: JobDescriptionData
    similarity_analysis: HiringCandidateAnalysis
    skills_recommendations: SkillsRecommendation
    processing_time_seconds: float
