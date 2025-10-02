import os
import asyncio
from typing import Dict, Optional
import aiohttp
import json
import logging

logger = logging.getLogger(__name__)

class RateLimitService:
    def __init__(self):
        self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "https://jobpsych-payment.vercel.app/api")
        self.upload_limit = 10

    async def check_user_upload_limit(self, email: str) -> Dict:
        """
        Check user upload count from Express.js auth service
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Call your Express.js service to get user upload count
                async with session.get(
                    f"{self.auth_service_url}/auth/user-uploads/{email}",
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        files_uploaded = data.get("filesUploaded", 0)
                        return {
                            "allowed": files_uploaded < self.upload_limit,
                            "current_count": files_uploaded,
                            "limit": self.upload_limit,
                            "remaining": max(0, self.upload_limit - files_uploaded)
                        }
                    elif response.status == 404:
                        # User not found, treat as new user with 0 uploads
                        logger.warning(f"User not found in auth service: {email}")
                        return {
                            "allowed": True,
                            "current_count": 0,
                            "limit": self.upload_limit,
                            "remaining": self.upload_limit
                        }
                    else:
                        # If service is unavailable, allow the request but log
                        logger.warning(f"Auth service unavailable: {response.status}")
                        return {
                            "allowed": True,
                            "current_count": 0,
                            "limit": self.upload_limit,
                            "remaining": self.upload_limit
                        }
        except asyncio.TimeoutError:
            logger.error(f"Timeout checking rate limit for {email}")
            # Fail open - allow request if rate limit service is down
            return {
                "allowed": True,
                "current_count": 0,
                "limit": self.upload_limit,
                "remaining": self.upload_limit
            }
        except Exception as e:
            logger.error(f"Rate limit check failed for {email}: {e}")
            # Fail open - allow request if rate limit service is down
            return {
                "allowed": True,
                "current_count": 0,
                "limit": self.upload_limit,
                "remaining": self.upload_limit
            }

    async def increment_user_upload(self, email: str) -> bool:
        """
        Increment user upload count in Express.js auth service
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.auth_service_url}/auth/increment-upload",
                    json={"email": email},
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Successfully incremented upload count for {email}")
                        return True
                    else:
                        logger.warning(f"Failed to increment upload count for {email}: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to increment upload count for {email}: {e}")
            return False

# Global instance
rate_limit_service = RateLimitService()