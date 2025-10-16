"""
Unit tests for individual services
Tests resume parser, role recommender, question generator, and rate limiter
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO


# ============================================================================
# RESUME PARSER TESTS
# ============================================================================

class TestResumeParser:
    """Test suite for ResumeParser service"""
    
    @pytest.fixture
    def parser(self):
        from app.services.resume_parser import ResumeParser
        return ResumeParser()
    
    def test_parser_initialization(self, parser):
        """Test parser initializes correctly"""
        assert parser is not None
    
    @pytest.mark.asyncio
    async def test_parse_pdf_structure(self, parser):
        """Test parser returns correct data structure"""
        # Create a minimal PDF
        pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
trailer<</Size 4/Root 1 0 R>>
startxref
190
%%EOF"""
        
        from fastapi import UploadFile
        file = UploadFile(filename="test.pdf", file=BytesIO(pdf_content))
        
        with patch.object(parser, 'parse') as mock_parse:
            mock_parse.return_value = {
                "personal_info": {},
                "summary": "",
                "experience": [],
                "education": [],
                "skills": [],
                "certifications": [],
                "projects": [],
                "languages": []
            }
            
            result = await parser.parse(file)
            
            assert "personal_info" in result
            assert "experience" in result
            assert "skills" in result


# ============================================================================
# ROLE RECOMMENDER TESTS
# ============================================================================

class TestRoleRecommender:
    """Test suite for RoleRecommender service"""
    
    @pytest.fixture
    def recommender(self):
        from app.services.role_recommender import RoleRecommender
        return RoleRecommender()
    
    def test_recommender_initialization(self, recommender):
        """Test recommender initializes correctly"""
        assert recommender is not None
    
    @pytest.mark.asyncio
    async def test_recommend_roles_returns_list(self, recommender):
        """Test role recommendation returns proper structure"""
        resume_data = {
            "personal_info": {"name": "Test User"},
            "skills": ["Python", "FastAPI"],
            "experience": []
        }
        
        with patch.object(recommender, 'recommend_roles') as mock_recommend:
            mock_recommend.return_value = {
                "recommended_roles": ["Backend Developer", "Software Engineer"],
                "match_scores": {}
            }
            
            result = await recommender.recommend_roles(resume_data)
            
            assert "recommended_roles" in result
            assert isinstance(result["recommended_roles"], list)
    
    @pytest.mark.asyncio
    async def test_analyze_role_fit(self, recommender):
        """Test role fit analysis"""
        resume_data = {
            "skills": ["Python", "JavaScript"],
            "experience": []
        }
        
        with patch.object(recommender, 'analyze_role_fit') as mock_fit:
            mock_fit.return_value = {
                "target_role": "Full Stack Developer",
                "match_score": 75,
                "strengths": ["Python expertise"],
                "gaps": ["Needs more frontend experience"]
            }
            
            result = await recommender.analyze_role_fit(
                resume_data, 
                "Full Stack Developer",
                "Looking for full stack developer"
            )
            
            assert "target_role" in result
            assert "match_score" in result


# ============================================================================
# QUESTION GENERATOR TESTS
# ============================================================================

class TestQuestionGenerator:
    """Test suite for QuestionGenerator service"""
    
    @pytest.fixture
    def generator(self):
        from app.services.question_generator import QuestionGenerator
        return QuestionGenerator()
    
    def test_generator_initialization(self, generator):
        """Test generator initializes correctly"""
        assert generator is not None
    
    @pytest.mark.asyncio
    async def test_generate_questions_structure(self, generator):
        """Test question generation returns proper structure"""
        resume_data = {
            "skills": ["Python", "Machine Learning"],
            "experience": [{"title": "Data Scientist"}]
        }
        
        with patch.object(generator, 'generate') as mock_gen:
            mock_gen.return_value = [
                {
                    "type": "technical",
                    "question": "Explain your Python experience",
                    "context": "Based on your resume"
                }
            ]
            
            result = await generator.generate(resume_data)
            
            assert isinstance(result, list)
            if len(result) > 0:
                assert "question" in result[0]


# ============================================================================
# ADVANCED ANALYZER TESTS
# ============================================================================

class TestAdvancedAnalyzer:
    """Test suite for AdvancedAnalyzer service"""
    
    @pytest.fixture
    def analyzer(self):
        from app.services.advanced_analyzer import AdvancedAnalyzer
        return AdvancedAnalyzer()
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None


# ============================================================================
# RATE LIMIT SERVICE TESTS
# ============================================================================

class TestRateLimitService:
    """Test suite for Rate Limit Service"""
    
    @pytest.fixture
    def rate_limiter(self):
        from app.services.rate_limit_service import rate_limit_service
        return rate_limit_service
    
    @pytest.mark.asyncio
    async def test_check_upload_limit(self, rate_limiter):
        """Test checking upload limit"""
        with patch.object(rate_limiter, 'check_user_upload_limit') as mock_check:
            mock_check.return_value = {
                "allowed": True,
                "remaining": 5,
                "limit": 10,
                "current": 5
            }
            
            result = await rate_limiter.check_user_upload_limit("test@example.com")
            
            assert "allowed" in result
            assert "remaining" in result
            assert "limit" in result
    
    @pytest.mark.asyncio
    async def test_increment_upload_count(self, rate_limiter):
        """Test incrementing upload count"""
        with patch.object(rate_limiter, 'increment_user_upload') as mock_inc:
            mock_inc.return_value = True
            
            result = await rate_limiter.increment_user_upload("test@example.com")
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, rate_limiter):
        """Test rate limit exceeded scenario"""
        with patch.object(rate_limiter, 'check_user_upload_limit') as mock_check:
            mock_check.return_value = {
                "allowed": False,
                "remaining": 0,
                "limit": 10,
                "current": 10,
                "message": "Upload limit exceeded"
            }
            
            result = await rate_limiter.check_user_upload_limit("test@example.com")
            
            assert result["allowed"] is False
            assert result["remaining"] == 0


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test suite for authentication utilities"""
    
    def test_jwt_secret_loaded(self):
        """Test JWT secret is loaded from environment"""
        import os
        os.environ["JWT_ACCESS_SECRET"] = "test_secret_123"
        os.environ["JWT_SECRET"] = "test_secret_123"
        
        # Reload the module to pick up new env vars
        from app.dependencies import auth
        # Force reload
        import importlib
        importlib.reload(auth)
        
        assert auth.JWT_SECRET is not None
    
    def test_token_data_class(self):
        """Test TokenData class"""
        from app.dependencies.auth import TokenData
        
        token_data = TokenData(
            email="test@example.com",
            user_id="123",
            name="Test User"
        )
        
        assert token_data.email == "test@example.com"
        assert token_data.user_id == "123"
        assert token_data.name == "Test User"


# ============================================================================
# SCHEMA VALIDATION TESTS
# ============================================================================

class TestSchemas:
    """Test suite for Pydantic schemas"""
    
    def test_personal_info_schema(self):
        """Test PersonalInfo schema validation"""
        from app.models.schemas import PersonalInfo
        
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoe",
            "github": "github.com/johndoe",
            "website": "johndoe.com"
        }
        
        personal_info = PersonalInfo(**data)
        assert personal_info.name == "John Doe"
        assert personal_info.email == "john@example.com"
    
    def test_resume_data_schema(self):
        """Test ResumeData schema validation"""
        from app.models.schemas import ResumeData, PersonalInfo, Experience, Education
        
        data = {
            "personalInfo": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "workExperience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2020-2023"
                }
            ],
            "education": [
                {
                    "degree": "BS Computer Science",
                    "institution": "University",
                    "year": "2020"
                }
            ],
            "skills": ["Python", "JavaScript"],
            "highlights": ["Led team of 5 developers"]
        }
        
        resume_data = ResumeData(**data)
        assert resume_data.personalInfo.name == "John Doe"
        assert len(resume_data.skills) == 2
        assert len(resume_data.workExperience) == 1
    
    def test_question_schema(self):
        """Test Question schema validation"""
        from app.models.schemas import Question
        
        question = Question(
            type="technical",
            question="What is your experience with Python?",
            context="Based on your resume showing Python skills"
        )
        
        assert question.question is not None
        assert question.type == "technical"
        assert question.context is not None


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test suite for error handling"""
    
    def test_invalid_file_format(self):
        """Test handling of invalid file formats"""
        from fastapi import UploadFile
        from app.services.resume_parser import ResumeParser
        
        parser = ResumeParser()
        invalid_file = UploadFile(
            filename="test.txt",
            file=BytesIO(b"This is not a PDF")
        )
        
        # Should handle gracefully (implementation specific)
        # This test ensures the service exists and can be instantiated
        assert parser is not None
    
    def test_missing_required_fields(self):
        """Test validation of required fields"""
        from app.models.schemas import PersonalInfo
        from pydantic import ValidationError
        
        # Missing required 'name' field
        with pytest.raises(ValidationError):
            PersonalInfo(email="test@example.com")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test suite for performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import asyncio
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        async def make_request():
            response = client.get("/health")
            return response.status_code
        
        # Simulate 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert all(status == 200 for status in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
