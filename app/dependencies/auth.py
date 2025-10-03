from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os
from typing import Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_ACCESS_SECRET") or os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

# Log JWT_SECRET status at module load time
if JWT_SECRET:
    logger.info(f"✅ JWT_SECRET loaded successfully (length: {len(JWT_SECRET)})")
    # Show which variable was used
    if os.getenv("JWT_ACCESS_SECRET"):
        logger.info(f"📌 Using JWT_ACCESS_SECRET (matches Express.js primary)")
    else:
        logger.info(f"📌 Using JWT_SECRET (fallback)")
else:
    logger.error("❌ Neither JWT_ACCESS_SECRET nor JWT_SECRET found in environment!")

print(f"🔍 AUTH MODULE LOADED - JWT_SECRET: {'✅ SET' if JWT_SECRET else '❌ NOT SET'}")

class TokenData:
    def __init__(self, email: str, user_id: str = None, name: str = None):
        self.email = email
        self.user_id = user_id
        self.name = name

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Verify JWT token and extract user information
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "success": False,
            "message": "Could not validate credentials",
            "error": "AUTHENTICATION_ERROR"
        },
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "JWT configuration error",
                "error": "SERVER_ERROR"
            }
        )

    try:
        token = credentials.credentials
        
        # Debug logging
        logger.info("=" * 60)
        logger.info("🔍 JWT TOKEN VALIDATION ATTEMPT")
        logger.info(f"Token length: {len(token)}")
        logger.info(f"Token preview (first 50 chars): {token[:50] if len(token) > 50 else token}...")
        logger.info(f"Token preview (last 20 chars): ...{token[-20:]}")
        logger.info(f"JWT_SECRET (first 10 chars): {JWT_SECRET[:10] if JWT_SECRET else 'NOT SET'}...")
        logger.info(f"Algorithm: {ALGORITHM}")
        
        # Check if token looks like a JWT (should have 3 parts separated by dots)
        token_parts = token.split('.')
        logger.info(f"Token parts count: {len(token_parts)} (should be 3 for valid JWT)")
        
        if len(token_parts) != 3:
            logger.error(f"❌ INVALID TOKEN FORMAT! Token has {len(token_parts)} parts, expected 3")
            logger.error(f"Full token: {token}")
            raise credentials_exception
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        
        logger.info("✅ Token decoded successfully!")
        logger.info(f"Payload keys: {list(payload.keys())}")
        logger.info(f"Payload: {payload}")

        email: str = payload.get("email")
        user_id: str = payload.get("id") or payload.get("userId")
        name: str = payload.get("name")

        logger.info(f"Extracted - Email: {email}, User ID: {user_id}, Name: {name}")

        if email is None:
            logger.error("❌ Email not found in token payload!")
            raise credentials_exception

        logger.info(f"✅ Authentication successful for user: {email}")
        logger.info("=" * 60)
        return TokenData(email=email, user_id=user_id, name=name)

    except JWTError as e:
        logger.error(f"❌ JWT decode error: {type(e).__name__}: {e}")
        logger.error("=" * 60)
        raise credentials_exception
    except Exception as e:
        logger.error(f"❌ Token validation error: {type(e).__name__}: {e}")
        logger.error("=" * 60)
        raise credentials_exception