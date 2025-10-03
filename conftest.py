"""
Configuration file for pytest
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ["JWT_ACCESS_SECRET"] = "test_secret_key_for_testing_purposes_only_1234567890"
os.environ["JWT_SECRET"] = "test_secret_key_for_testing_purposes_only_1234567890"
os.environ["GOOGLE_API_KEY"] = "test_google_api_key"

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests"""
    print("\n🧪 Setting up test environment...")
    yield
    print("\n✅ Test environment teardown complete")


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment between tests"""
    yield
    # Cleanup code here if needed
