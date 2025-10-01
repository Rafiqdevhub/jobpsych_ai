#!/usr/bin/env python3
"""
Test script to verify our core services can be imported and instantiated.
Uses pytest for proper testing framework.
"""

import pytest
import os
import sys
from unittest.mock import patch

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


class TestImports:
    """Test importing our core services."""

    def test_resume_parser_import(self):
        """Test importing ResumeParser."""
        from app.services.resume_parser import ResumeParser
        assert ResumeParser is not None

    def test_role_recommender_import(self):
        """Test importing RoleRecommender."""
        from app.services.role_recommender import RoleRecommender
        assert RoleRecommender is not None

    def test_question_generator_import(self):
        """Test importing QuestionGenerator."""
        from app.services.question_generator import QuestionGenerator
        assert QuestionGenerator is not None

    def test_advanced_analyzer_import(self):
        """Test importing AdvancedAnalyzer."""
        from app.services.advanced_analyzer import AdvancedAnalyzer
        assert AdvancedAnalyzer is not None


class TestInstantiation:
    """Test instantiating our services."""

    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_resume_parser_instantiation(self):
        """Test instantiating ResumeParser with mocked API key."""
        from app.services.resume_parser import ResumeParser
        parser = ResumeParser()
        assert parser is not None

    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_role_recommender_instantiation(self):
        """Test instantiating RoleRecommender."""
        from app.services.role_recommender import RoleRecommender
        recommender = RoleRecommender()
        assert recommender is not None

    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_question_generator_instantiation(self):
        """Test instantiating QuestionGenerator."""
        from app.services.question_generator import QuestionGenerator
        generator = QuestionGenerator()
        assert generator is not None

    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_advanced_analyzer_instantiation(self):
        """Test instantiating AdvancedAnalyzer."""
        from app.services.advanced_analyzer import AdvancedAnalyzer
        analyzer = AdvancedAnalyzer()
        assert analyzer is not None


class TestRouter:
    """Test router functionality."""

    def test_router_import(self):
        """Test importing the router."""
        from app.routers.resume_router import router
        assert router is not None

    def test_router_routes(self):
        """Test that expected routes exist."""
        from app.routers.resume_router import router

        routes = [route.path for route in router.routes]
        expected_routes = ["/analyze-resume", "/hiredesk-analyze", "/batch-analyze", "/compare-resumes"]

        for route in expected_routes:
            assert route in routes, f"Route {route} not found in router routes: {routes}"


class TestSchemas:
    """Test that schemas can be imported and used."""

    def test_resume_data_schema(self):
        """Test ResumeData schema."""
        from app.models.schemas import ResumeData, PersonalInfo

        personal_info = PersonalInfo(name="John Doe")
        resume_data = ResumeData(
            personalInfo=personal_info,
            workExperience=[],
            education=[],
            skills=[],
            highlights=[]
        )
        assert resume_data.personalInfo.name == "John Doe"

    def test_question_schema(self):
        """Test Question schema."""
        from app.models.schemas import Question

        question = Question(
            type="technical",
            question="What is Python?",
            context="Programming language"
        )
        assert question.type == "technical"
        assert question.question == "What is Python?"


class TestFastAPIApp:
    """Test FastAPI application endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct response."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "JobPsych" in data["message"]
        assert "endpoints" in data

    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_health_endpoint(self, client):
        """Test the health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["api_configured"] is True
