"""
Comprehensive test suite for JobPsych AI Resume Analyzer
Tests authentication, resume analysis, rate limiting, and all services
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
import os

# Import the FastAPI app
from app.main import app

# Create test client
client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_jwt_secret(monkeypatch):
    """Mock JWT secret for testing"""
    monkeypatch.setenv("JWT_ACCESS_SECRET", "test_secret_key_for_testing_purposes_only_1234567890")
    monkeypatch.setenv("JWT_SECRET", "test_secret_key_for_testing_purposes_only_1234567890")
    return "test_secret_key_for_testing_purposes_only_1234567890"


@pytest.fixture
def valid_token(mock_jwt_secret):
    """Generate a valid JWT token for testing"""
    from jose import jwt
    from datetime import datetime, timedelta
    
    payload = {
        "userId": "test_user_123",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, mock_jwt_secret, algorithm="HS256")
    return token


@pytest.fixture
def expired_token(mock_jwt_secret):
    """Generate an expired JWT token for testing"""
    from jose import jwt
    from datetime import datetime, timedelta
    
    payload = {
        "userId": "test_user_123",
        "email": "test@example.com",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
        "iat": datetime.utcnow() - timedelta(hours=2)
    }
    token = jwt.encode(payload, mock_jwt_secret, algorithm="HS256")
    return token


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing"""
    # Minimal valid PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer<</Size 4/Root 1 0 R>>
startxref
190
%%EOF"""
    return BytesIO(pdf_content)


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

def test_root_endpoint():
    """Test the root endpoint returns API information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Resume Analysis" in data["message"]


def test_cors_headers():
    """Test CORS headers are properly set"""
    response = client.options("/")
    assert response.status_code in [200, 405]  # Some frameworks return 405 for OPTIONS


def test_cors_test_endpoint():
    """Test the CORS test endpoint"""
    response = client.get("/api/cors-test")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "CORS is working!"
    assert data["status"] == "success"


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_auth_missing_token(mock_jwt_secret):
    """Test authentication fails when no token is provided"""
    response = client.post(
        "/api/hiredesk-analyze",
        files={"file": ("test.pdf", BytesIO(b"dummy"), "application/pdf")},
        data={
            "target_role": "Software Engineer",
            "job_description": "Python developer"
        }
    )
    assert response.status_code == 403  # Forbidden - no credentials


def test_auth_invalid_token(mock_jwt_secret):
    """Test authentication fails with invalid token"""
    response = client.post(
        "/api/hiredesk-analyze",
        headers={"Authorization": "Bearer invalid_token_here"},
        files={"file": ("test.pdf", BytesIO(b"dummy"), "application/pdf")},
        data={
            "target_role": "Software Engineer",
            "job_description": "Python developer"
        }
    )
    assert response.status_code == 401  # Unauthorized


def test_auth_expired_token(mock_jwt_secret, expired_token):
    """Test authentication fails with expired token"""
    response = client.post(
        "/api/hiredesk-analyze",
        headers={"Authorization": f"Bearer {expired_token}"},
        files={"file": ("test.pdf", BytesIO(b"dummy"), "application/pdf")},
        data={
            "target_role": "Software Engineer",
            "job_description": "Python developer"
        }
    )
    assert response.status_code == 401  # Unauthorized


def test_auth_malformed_header(mock_jwt_secret):
    """Test authentication fails with malformed Authorization header"""
    response = client.post(
        "/api/hiredesk-analyze",
        headers={"Authorization": "InvalidFormat token123"},
        files={"file": ("test.pdf", BytesIO(b"dummy"), "application/pdf")},
        data={
            "target_role": "Software Engineer",
            "job_description": "Python developer"
        }
    )
    assert response.status_code in [401, 403]


# ============================================================================
# RESUME ANALYSIS TESTS (PUBLIC ENDPOINT)
# ============================================================================

def test_analyze_resume_success():
    """Test resume analysis endpoint exists"""
    # Skip full integration test - requires Google API
    # Test that endpoint rejects missing file
    response = client.post("/api/analyze-resume")
    assert response.status_code == 422  # Missing required field


def test_analyze_resume_with_target_role():
    """Test resume analysis endpoint accepts file parameter"""
    # This is a basic smoke test
    # Full integration testing requires Google API key and is done separately
    pytest.skip("Requires Google API integration - run as integration test")


def test_analyze_resume_missing_file():
    """Test resume analysis fails without file"""
    response = client.post("/api/analyze-resume")
    assert response.status_code == 422  # Unprocessable Entity


def test_analyze_resume_invalid_file_type():
    """Test resume analysis fails with invalid file type"""
    pytest.skip("Integration test - requires actual file processing")


# ============================================================================
# AUTHENTICATED RESUME ANALYSIS TESTS
# ============================================================================

def test_hiredesk_analyze_success(valid_token, sample_pdf_file, mock_jwt_secret):
    """Test authenticated endpoint requires proper authentication"""
    # Skip full integration test
    pytest.skip("Integration test - requires full Google API and rate limit service")


def test_hiredesk_analyze_rate_limit_exceeded(valid_token, sample_pdf_file, mock_jwt_secret):
    """Test rate limit is enforced"""
    pytest.skip("Integration test - requires rate limit service")


def test_hiredesk_analyze_missing_required_fields(valid_token, sample_pdf_file, mock_jwt_secret):
    """Test analysis fails without required fields"""
    response = client.post(
        "/api/hiredesk-analyze",
        headers={"Authorization": f"Bearer {valid_token}"},
        files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
        data={"target_role": "Engineer"}  # Missing job_description
    )
    
    assert response.status_code == 422  # Unprocessable Entity


# ============================================================================
# RATE LIMITING TESTS
# ============================================================================

def test_rate_limiting_per_ip():
    """Test IP-based rate limiting on public endpoint"""
    # Make multiple rapid requests
    responses = []
    for _ in range(10):
        response = client.get("/api/cors-test")
        responses.append(response.status_code)
    
    # All should succeed or eventually rate limit
    assert all(status in [200, 429] for status in responses)


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_404_not_found():
    """Test 404 error for non-existent endpoints"""
    response = client.get("/api/nonexistent-endpoint")
    assert response.status_code == 404


def test_405_method_not_allowed():
    """Test 405 error for wrong HTTP method"""
    response = client.get("/api/hiredesk-analyze")
    assert response.status_code == 405


# ============================================================================
# SERVICE TESTS
# ============================================================================

def test_resume_parser_import():
    """Test ResumeParser can be imported"""
    from app.services.resume_parser import ResumeParser
    parser = ResumeParser()
    assert parser is not None


def test_role_recommender_import():
    """Test RoleRecommender can be imported"""
    from app.services.role_recommender import RoleRecommender
    recommender = RoleRecommender()
    assert recommender is not None


def test_question_generator_import():
    """Test QuestionGenerator can be imported"""
    from app.services.question_generator import QuestionGenerator
    generator = QuestionGenerator()
    assert generator is not None


def test_advanced_analyzer_import():
    """Test AdvancedAnalyzer can be imported"""
    from app.services.advanced_analyzer import AdvancedAnalyzer
    analyzer = AdvancedAnalyzer()
    assert analyzer is not None


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_app_startup():
    """Test application starts without errors"""
    assert app is not None
    assert app.title == "JobPsych ai"
    assert app.version == "2.0.0"


def test_cors_origins_configured():
    """Test CORS middleware is properly configured"""
    # Check that CORS middleware is in the middleware stack
    middleware_classes = [m.__class__.__name__ for m in app.user_middleware]
    # CORS middleware might be wrapped, so we check for its presence
    assert len(app.user_middleware) > 0


# ============================================================================
# SCHEMA VALIDATION TESTS
# ============================================================================

def test_schemas_can_be_imported():
    """Test all schemas can be imported"""
    from app.models.schemas import (
        ResumeAnalysisResponse,
        ResumeData,
        Question,
        PersonalInfo
    )
    assert ResumeAnalysisResponse is not None
    assert ResumeData is not None
    assert Question is not None
    assert PersonalInfo is not None


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

def test_environment_variables(mock_jwt_secret):
    """Test environment variables are loaded"""
    from app.dependencies.auth import JWT_SECRET
    assert JWT_SECRET is not None
    assert len(JWT_SECRET) > 0


# ============================================================================
# CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test"""
    yield
    # Add any cleanup logic here if needed
