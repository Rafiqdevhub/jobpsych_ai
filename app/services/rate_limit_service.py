import os
import asyncio
from typing import Dict, Optional
import aiohttp
import logging

logger = logging.getLogger(__name__)

class RateLimitService:
    def __init__(self):
        self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "https://jobpsych-payment.vercel.app/api")
        # self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:5000/api")
        self.upload_limit = 10
        self.batch_size_limit = 5  # Files per batch
        self.free_tier_limit = 10  # Total files for free users

    async def check_user_upload_limit(self, email: str) -> Dict:
        """
        Check user upload count from Express.js auth service
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.auth_service_url}/user-uploads/{email}",
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
                        return {
                            "allowed": True,
                            "current_count": 0,
                            "limit": self.upload_limit,
                            "remaining": self.upload_limit
                        }
                    else:
                        # If service is unavailable, allow the request
                        return {
                            "allowed": True,
                            "current_count": 0,
                            "limit": self.upload_limit,
                            "remaining": self.upload_limit
                        }
        except asyncio.TimeoutError:
            # Fail open - allow request if rate limit service is down
            return {
                "allowed": True,
                "current_count": 0,
                "limit": self.upload_limit,
                "remaining": self.upload_limit
            }
        except Exception as e:
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
                    f"{self.auth_service_url}/increment-upload",
                    json={"email": email},
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        return False
        except Exception as e:
            return False

    async def get_feature_usage(self, email: str) -> Optional[Dict]:
        """
        Get all feature usage stats from Express.js auth service
        Returns: { filesUploaded, batch_analysis, compare_resumes }
        """
        try:
            # Normalize email to lowercase
            normalized_email = email.lower().strip()
            # Call Express.js service
            url = f"{self.auth_service_url}/user-uploads/{normalized_email}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "files_uploaded": data.get("filesUploaded", 0),
                            "batch_analysis": data.get("batch_analysis", 0),
                            "compare_resumes": data.get("compare_resumes", 0)
                        }
                    elif response.status == 404:
                        # Return defaults if user not found
                        return {
                            "files_uploaded": 0,
                            "batch_analysis": 0,
                            "compare_resumes": 0
                        }
                    else:
                        return None
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None

    async def ensure_user_exists(self, email: str) -> bool:
        """
        Check if user exists in Express.js auth service
        
        Returns: True if user exists, False if not found
        """
        try:
            # Normalize email
            normalized_email = email.lower().strip()
            
            # Check if user exists
            usage = await self.get_feature_usage(normalized_email)
            if usage is not None:
                return True
            
            # If usage is None, service error occurred
            return False
            
        except Exception as e:
            return False

    async def check_batch_analysis_limit(self, email: str, batch_size: int) -> Dict:
        """
        Check if user can process a batch for analysis
        
        Args:
            email: User email
            batch_size: Number of files in the batch
        
        Returns:
        {
            "allowed": bool,
            "reason": str,  # "ok" | "batch_size_exceeded" | "file_limit_exceeded" | "upgrade_required"
            "current_files_uploaded": int,
            "current_batches": int,
            "batch_size": int,
            "files_limit": int,
            "files_remaining": int,
            "would_exceed_by": int,  # How many over limit
            "warning_threshold": int  # e.g., 8 (warn at 8 files)
        }
        """
        try:
            # Validate batch size
            if batch_size > self.batch_size_limit:
                return {
                    "allowed": False,
                    "reason": "batch_size_exceeded",
                    "message": f"Maximum {self.batch_size_limit} files per batch. You submitted {batch_size}.",
                    "batch_size_limit": self.batch_size_limit,
                    "submitted": batch_size
                }

            # Get current usage stats
            usage = await self.get_feature_usage(email)
            if usage is None:
                return {
                    "allowed": True,
                    "reason": "service_unavailable",
                    "message": "Could not verify limit, allowing request"
                }

            current_files = usage["files_uploaded"]
            current_batches = usage["batch_analysis"]
            would_be_total = current_files + batch_size
            warning_threshold = 8  # Warn users at 8 files

            # Check if would exceed limit
            if would_be_total > self.free_tier_limit:
                files_over = would_be_total - self.free_tier_limit
                return {
                    "allowed": False,
                    "reason": "file_limit_exceeded",
                    "message": f"Upload limit exceeded. Current: {current_files}, Batch size: {batch_size}, Limit: {self.free_tier_limit}. Would exceed by {files_over} files.",
                    "current_files_uploaded": current_files,
                    "current_batches": current_batches,
                    "batch_size": batch_size,
                    "files_limit": self.free_tier_limit,
                    "would_be_total": would_be_total,
                    "files_remaining": 0,
                    "would_exceed_by": files_over,
                    "upgrade_required": True
                }

            # Check if approaching limit (warn)
            warning = False
            if would_be_total >= warning_threshold:
                warning = True

            files_remaining = self.free_tier_limit - would_be_total

            return {
                "allowed": True,
                "reason": "ok",
                "current_files_uploaded": current_files,
                "current_batches": current_batches,
                "batch_size": batch_size,
                "files_limit": self.free_tier_limit,
                "files_remaining": files_remaining,
                "would_be_total": would_be_total,
                "warning": warning,
                "warning_threshold": warning_threshold,
                "upgrade_required": False
            }

        except Exception as e:
            # Fail open - allow request but log the error
            return {
                "allowed": True,
                "reason": "check_failed",
                "message": "Could not verify limit, allowing request"
            }

    async def increment_batch_counter(self, email: str) -> bool:
        """
        Increment batch_analysis counter (one batch processed)
        
        Calls: POST /increment-batch-analysis
        """
        try:
            # Normalize email
            normalized_email = email.lower().strip()
            url = f"{self.auth_service_url}/increment-batch-analysis"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"email": normalized_email},
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        # Don't block - endpoint missing or temporarily unavailable
                        return True
        except asyncio.TimeoutError:
            # Timeout - don't block
            return True
        except Exception as e:
            # Error - don't block
            return True

    async def increment_compare_resumes_counter(self, email: str) -> bool:
        """
        Increment compare_resumes counter (one comparison completed)
        
        Calls: POST /increment-compare-resumes
        """
        try:
            # Normalize email
            normalized_email = email.lower().strip()
            url = f"{self.auth_service_url}/increment-compare-resumes"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"email": normalized_email},
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        # Don't block - endpoint missing or temporarily unavailable
                        return True
        except asyncio.TimeoutError:
            # Timeout - don't block
            return True
        except Exception as e:
            # Error - don't block
            return True

    async def increment_upload_count(self, email: str, count: int = 1) -> bool:
        """
        Increment upload count by N files
        
        Uses dedicated endpoint: POST /increment-upload
        """
        # Normalize email
        normalized_email = email.lower().strip()
        
        if count <= 0:
            return False

        try:
            # Call increment endpoint 'count' times for each successful file
            success_count = 0
            for i in range(count):
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.auth_service_url}/increment-upload",
                        json={"email": normalized_email},
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            success_count += 1

            return success_count > 0  # Return True if at least one succeeded

        except Exception as e:
            return False

# Global instance
rate_limit_service = RateLimitService()