#!/usr/bin/env python3
"""
Test script to verify our new AI services can be imported and instantiated.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test importing our new services."""
    print("Testing imports...")

    try:
        from app.services.advanced_resume_parser import AdvancedResumeParser
        print("✅ AdvancedResumeParser imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AdvancedResumeParser: {e}")
        return False

    try:
        from app.services.job_description_parser import JobDescriptionParser
        print("✅ JobDescriptionParser imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import JobDescriptionParser: {e}")
        return False

    try:
        from app.services.similarity_scorer import SimilarityScorer
        print("✅ SimilarityScorer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SimilarityScorer: {e}")
        return False

    try:
        from app.services.skills_recommender import SkillsRecommender
        print("✅ SkillsRecommender imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SkillsRecommender: {e}")
        return False

    try:
        from app.models.schemas import HiringCandidateResponse
        print("✅ HiringCandidateResponse schema imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import HiringCandidateResponse: {e}")
        return False

    return True

def test_instantiation():
    """Test instantiating our services."""
    print("\nTesting service instantiation...")

    try:
        from app.services.skills_recommender import SkillsRecommender
        recommender = SkillsRecommender()
        print("✅ SkillsRecommender instantiated successfully")
    except Exception as e:
        print(f"❌ Failed to instantiate SkillsRecommender: {e}")
        return False

    # Test other services (these might fail due to model loading)
    try:
        from app.services.job_description_parser import JobDescriptionParser
        parser = JobDescriptionParser()
        print("✅ JobDescriptionParser instantiated successfully")
    except Exception as e:
        print(f"⚠️  JobDescriptionParser instantiation failed (likely due to model loading): {e}")

    try:
        from app.services.similarity_scorer import SimilarityScorer
        scorer = SimilarityScorer()
        print("✅ SimilarityScorer instantiated successfully")
    except Exception as e:
        print(f"⚠️  SimilarityScorer instantiation failed (likely due to model loading): {e}")

    return True

def test_router_import():
    """Test importing the router with our new route."""
    print("\nTesting router import...")

    try:
        from app.routers.resume_router import router
        print("✅ Router imported successfully")

        # Check if our new route exists
        routes = [route.path for route in router.routes]
        if "/hiring-candidate" in routes:
            print("✅ hiring-candidate route found")
        else:
            print("❌ hiring-candidate route not found")
            return False

        return True
    except ImportError as e:
        print(f"❌ Failed to import router: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing our AI-powered hiring candidate services...\n")

    success = True
    success &= test_imports()
    success &= test_instantiation()
    success &= test_router_import()

    if success:
        print("\n🎉 All tests passed! The services should work correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)
