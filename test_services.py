#!/usr/bin/env python3
"""
Test script to verify our core services can be imported and instantiated.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test importing our core services."""
    print("Testing imports...")

    try:
        from app.services.resume_parser import ResumeParser
        print("✅ ResumeParser imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ResumeParser: {e}")
        return False

    try:
        from app.services.role_recommender import RoleRecommender
        print("✅ RoleRecommender imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import RoleRecommender: {e}")
        return False

    try:
        from app.services.question_generator import QuestionGenerator
        print("✅ QuestionGenerator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import QuestionGenerator: {e}")
        return False

    return True

def test_instantiation():
    """Test instantiating our services."""
    print("\nTesting service instantiation...")

    try:
        from app.services.resume_parser import ResumeParser
        parser = ResumeParser()
        print("✅ ResumeParser instantiated successfully")
    except Exception as e:
        print(f"❌ Failed to instantiate ResumeParser: {e}")
        return False

    try:
        from app.services.role_recommender import RoleRecommender
        recommender = RoleRecommender()
        print("✅ RoleRecommender instantiated successfully")
    except Exception as e:
        print(f"❌ Failed to instantiate RoleRecommender: {e}")
        return False

    try:
        from app.services.question_generator import QuestionGenerator
        generator = QuestionGenerator()
        print("✅ QuestionGenerator instantiated successfully")
    except Exception as e:
        print(f"❌ Failed to instantiate QuestionGenerator: {e}")
        return False

    return True

def test_router_import():
    """Test importing the router."""
    print("\nTesting router import...")

    try:
        from app.routers.resume_router import router
        print("✅ Router imported successfully")

        # Check if our core routes exist
        routes = [route.path for route in router.routes]
        expected_routes = ["/generate-questions", "/analyze-resume", "/hiredesk-analyze"]

        for route in expected_routes:
            if route in routes:
                print(f"✅ {route} route found")
            else:
                print(f"❌ {route} route not found")
                return False

        return True
    except ImportError as e:
        print(f"❌ Failed to import router: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing our core services...\n")

    success = True
    success &= test_imports()
    success &= test_instantiation()
    success &= test_router_import()

    if success:
        print("\n🎉 All tests passed! The services should work correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)
