from typing import Dict, List, Any, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import re


class SimilarityScorer:
    """
    Advanced similarity scorer for resume-job matching using multiple approaches:
    1. Semantic similarity using transformers
    2. TF-IDF based text similarity
    3. Skills matching
    4. Experience level matching
    """

    def __init__(self):
        self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models for similarity scoring."""
        try:
            # Use a sentence transformer for semantic similarity
            self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

            # TF-IDF vectorizer for traditional text similarity
            self.tfidf_vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=1000,
                ngram_range=(1, 2)
            )

            print("✅ Similarity scorer models initialized successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize similarity models: {e}")
            self.model = None
            self.tfidf_vectorizer = None

    def calculate_similarity(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive similarity score between resume and job description.

        Args:
            resume_data: Parsed resume data
            job_data: Parsed job description data

        Returns:
            Dict containing various similarity scores and analysis
        """
        if not resume_data or not job_data:
            return self._get_empty_similarity_result()

        # Calculate different types of similarity
        semantic_score = self._calculate_semantic_similarity(resume_data, job_data)
        skills_score = self._calculate_skills_similarity(resume_data, job_data)
        experience_score = self._calculate_experience_similarity(resume_data, job_data)
        text_similarity = self._calculate_text_similarity(resume_data, job_data)

        # Calculate overall weighted score
        overall_score = self._calculate_overall_score(
            semantic_score, skills_score, experience_score, text_similarity
        )

        # Generate detailed analysis
        analysis = self._generate_similarity_analysis(
            resume_data, job_data, semantic_score, skills_score, experience_score
        )

        return {
            "overall_score": round(overall_score, 2),
            "semantic_similarity": round(semantic_score, 2),
            "skills_match": round(skills_score, 2),
            "experience_match": round(experience_score, 2),
            "text_similarity": round(text_similarity, 2),
            "analysis": analysis,
            "recommendations": self._generate_recommendations(resume_data, job_data)
        }

    def _calculate_semantic_similarity(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate semantic similarity using transformer embeddings."""
        if not self.model:
            return 0.5  # Default neutral score

        try:
            # Extract text content from resume and job
            resume_text = self._extract_resume_text(resume_data)
            job_text = self._extract_job_text(job_data)

            if not resume_text or not job_text:
                return 0.5

            # Get embeddings
            resume_embedding = self._get_embedding(resume_text)
            job_embedding = self._get_embedding(job_text)

            if resume_embedding is None or job_embedding is None:
                return 0.5

            # Calculate cosine similarity
            similarity = cosine_similarity(
                resume_embedding.reshape(1, -1),
                job_embedding.reshape(1, -1)
            )[0][0]

            return float(similarity)

        except Exception as e:
            print(f"⚠️  Error calculating semantic similarity: {e}")
            return 0.5

    def _calculate_skills_similarity(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate skills matching score."""
        resume_skills = set()
        job_required_skills = set()
        job_preferred_skills = set()

        # Extract resume skills
        if 'skills' in resume_data:
            resume_skills = set(skill.lower() for skill in resume_data['skills'])

        # Extract job skills
        if 'required_skills' in job_data:
            job_required_skills = set(skill.lower() for skill in job_data['required_skills'])
        if 'preferred_skills' in job_data:
            job_preferred_skills = set(skill.lower() for skill in job_data['preferred_skills'])

        if not job_required_skills:
            return 0.5  # Neutral if no required skills specified

        # Calculate matching scores
        required_matches = len(resume_skills.intersection(job_required_skills))
        preferred_matches = len(resume_skills.intersection(job_preferred_skills))

        # Weighted score: required skills are more important
        required_score = min(required_matches / len(job_required_skills), 1.0) if job_required_skills else 1.0
        preferred_score = min(preferred_matches / len(job_preferred_skills), 1.0) if job_preferred_skills else 0.0

        # Overall skills score (70% required, 30% preferred)
        skills_score = (required_score * 0.7) + (preferred_score * 0.3)

        return skills_score

    def _calculate_experience_similarity(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate experience level matching score."""
        resume_experience = self._extract_resume_experience_level(resume_data)
        job_experience = job_data.get('experience_level', 'Mid-level')

        # Experience level mapping
        experience_levels = {
            'Entry-level': 1,
            'Junior': 2,
            'Mid-level': 3,
            'Senior': 4,
            'Senior/Lead': 4,
            'Lead': 5,
            'Principal': 5,
            'Executive': 6
        }

        resume_level = experience_levels.get(resume_experience, 3)
        job_level = experience_levels.get(job_experience, 3)

        # Calculate compatibility score
        level_diff = abs(resume_level - job_level)

        if level_diff == 0:
            return 1.0  # Perfect match
        elif level_diff == 1:
            return 0.8  # Good match
        elif level_diff == 2:
            return 0.6  # Acceptable match
        else:
            return 0.3  # Poor match

    def _calculate_text_similarity(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate TF-IDF based text similarity."""
        if not self.tfidf_vectorizer:
            return 0.5

        try:
            resume_text = self._extract_resume_text(resume_data)
            job_text = self._extract_job_text(job_data)

            if not resume_text or not job_text:
                return 0.5

            # Create TF-IDF vectors
            texts = [resume_text, job_text]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            return float(similarity)

        except Exception as e:
            print(f"⚠️  Error calculating text similarity: {e}")
            return 0.5

    def _calculate_overall_score(self, semantic: float, skills: float,
                               experience: float, text: float) -> float:
        """Calculate weighted overall similarity score."""
        # Weights: skills are most important, then semantic, then experience, then text
        weights = {
            'semantic': 0.25,
            'skills': 0.40,
            'experience': 0.20,
            'text': 0.15
        }

        overall = (
            semantic * weights['semantic'] +
            skills * weights['skills'] +
            experience * weights['experience'] +
            text * weights['text']
        )

        return overall

    def _generate_similarity_analysis(self, resume_data: Dict, job_data: Dict,
                                   semantic_score: float, skills_score: float,
                                   experience_score: float) -> Dict[str, Any]:
        """Generate detailed analysis of the similarity scores."""
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "skill_gaps": [],
            "experience_alignment": "",
            "overall_assessment": ""
        }

        # Analyze skills
        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        job_required = set(skill.lower() for skill in job_data.get('required_skills', []))
        job_preferred = set(skill.lower() for skill in job_data.get('preferred_skills', []))

        matching_required = resume_skills.intersection(job_required)
        missing_required = job_required - resume_skills
        matching_preferred = resume_skills.intersection(job_preferred)

        # Strengths
        if matching_required:
            analysis["strengths"].append(f"Strong match in required skills: {', '.join(matching_required)}")
        if matching_preferred:
            analysis["strengths"].append(f"Good match in preferred skills: {', '.join(matching_preferred)}")
        if semantic_score > 0.7:
            analysis["strengths"].append("High semantic alignment between resume and job requirements")
        if experience_score > 0.8:
            analysis["strengths"].append("Experience level well-aligned with job requirements")

        # Weaknesses
        if missing_required:
            analysis["weaknesses"].append(f"Missing required skills: {', '.join(missing_required)}")
        if skills_score < 0.5:
            analysis["weaknesses"].append("Low skills matching score")
        if semantic_score < 0.5:
            analysis["weaknesses"].append("Low semantic similarity with job description")
        if experience_score < 0.6:
            analysis["weaknesses"].append("Experience level may not meet job requirements")

        # Skill gaps
        analysis["skill_gaps"] = list(missing_required)

        # Experience alignment
        resume_exp = self._extract_resume_experience_level(resume_data)
        job_exp = job_data.get('experience_level', 'Mid-level')
        analysis["experience_alignment"] = f"Resume: {resume_exp} vs Job: {job_exp}"

        # Overall assessment
        overall_score = self._calculate_overall_score(semantic_score, skills_score, experience_score, 0.5)
        if overall_score > 0.8:
            analysis["overall_assessment"] = "Excellent match - strong candidate"
        elif overall_score > 0.6:
            analysis["overall_assessment"] = "Good match - consider for interview"
        elif overall_score > 0.4:
            analysis["overall_assessment"] = "Moderate match - may need additional training"
        else:
            analysis["overall_assessment"] = "Poor match - significant gaps to address"

        return analysis

    def _generate_recommendations(self, resume_data: Dict, job_data: Dict) -> List[str]:
        """Generate recommendations for improving the match."""
        recommendations = []

        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        job_required = set(skill.lower() for skill in job_data.get('required_skills', []))
        job_preferred = set(skill.lower() for skill in job_data.get('preferred_skills', []))

        missing_required = job_required - resume_skills
        missing_preferred = job_preferred - resume_skills

        if missing_required:
            recommendations.append(f"Consider acquiring these required skills: {', '.join(list(missing_required)[:3])}")

        if missing_preferred:
            recommendations.append(f"Consider learning these preferred skills: {', '.join(list(missing_preferred)[:3])}")

        # Experience recommendations
        resume_exp = self._extract_resume_experience_level(resume_data)
        job_exp = job_data.get('experience_level', 'Mid-level')

        exp_levels = ['Entry-level', 'Junior', 'Mid-level', 'Senior', 'Lead']
        try:
            resume_idx = exp_levels.index(resume_exp)
            job_idx = exp_levels.index(job_exp)

            if resume_idx < job_idx:
                recommendations.append(f"Consider gaining more experience to reach {job_exp} level")
        except ValueError:
            pass

        # Semantic similarity recommendations
        resume_text = self._extract_resume_text(resume_data)
        job_text = self._extract_job_text(job_data)

        if len(resume_text.split()) < 200:
            recommendations.append("Consider expanding resume content to better demonstrate capabilities")

        return recommendations

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get sentence embedding for text."""
        try:
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True,
                                  padding=True, max_length=512)

            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)

            return embeddings.numpy()
        except Exception as e:
            print(f"⚠️  Error getting embedding: {e}")
            return None

    def _extract_resume_text(self, resume_data: Dict) -> str:
        """Extract text content from resume data."""
        text_parts = []

        if 'summary' in resume_data:
            text_parts.append(resume_data['summary'])
        if 'experience' in resume_data:
            text_parts.append(' '.join(resume_data['experience']))
        if 'education' in resume_data:
            text_parts.append(' '.join(resume_data['education']))
        if 'skills' in resume_data:
            text_parts.append(' '.join(resume_data['skills']))

        return ' '.join(text_parts)

    def _extract_job_text(self, job_data: Dict) -> str:
        """Extract text content from job data."""
        text_parts = []

        if 'job_title' in job_data:
            text_parts.append(job_data['job_title'])
        if 'responsibilities' in job_data:
            text_parts.append(' '.join(job_data['responsibilities']))
        if 'required_skills' in job_data:
            text_parts.append(' '.join(job_data['required_skills']))
        if 'preferred_skills' in job_data:
            text_parts.append(' '.join(job_data['preferred_skills']))

        return ' '.join(text_parts)

    def _extract_resume_experience_level(self, resume_data: Dict) -> str:
        """Extract experience level from resume data."""
        # This is a simplified implementation
        # In a real system, you'd analyze work experience duration and roles

        if 'experience' in resume_data:
            experience_text = ' '.join(resume_data['experience']).lower()

            if any(word in experience_text for word in ['senior', 'lead', 'principal', 'architect']):
                return 'Senior'
            elif any(word in experience_text for word in ['mid', 'intermediate']):
                return 'Mid-level'
            elif any(word in experience_text for word in ['junior', 'entry']):
                return 'Junior'
            else:
                # Estimate based on number of experiences
                if len(resume_data['experience']) > 3:
                    return 'Senior'
                elif len(resume_data['experience']) > 1:
                    return 'Mid-level'
                else:
                    return 'Junior'

        return 'Mid-level'  # Default

    def _get_empty_similarity_result(self) -> Dict[str, Any]:
        """Return empty similarity result."""
        return {
            "overall_score": 0.0,
            "semantic_similarity": 0.0,
            "skills_match": 0.0,
            "experience_match": 0.0,
            "text_similarity": 0.0,
            "analysis": {
                "strengths": [],
                "weaknesses": [],
                "skill_gaps": [],
                "experience_alignment": "",
                "overall_assessment": "Unable to analyze - missing data"
            },
            "recommendations": []
        }
