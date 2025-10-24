import os
import asyncio
from typing import Dict, Optional
import aiohttp
import logging

logger = logging.getLogger(__name__)

class RateLimitService:
    def __init__(self):
        # self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "https://jobpsych-auth.vercel.app/api")
        self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:5000/api")
        self.upload_limit = 10
        self.batch_size_limit = 5
        self.free_tier_limit = 10

    async def check_files_uploaded_limit(self, email: str) -> Dict:
        """
        Check filesUploaded count (used by hiredesk_analyze)
        For single file uploads
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

    async def check_user_upload_limit(self, email: str) -> Dict:
        return await self.check_files_uploaded_limit(email)

    async def increment_files_uploaded(self, email: str, count: int = 1) -> bool:
        """
        Increment filesUploaded counter for hiredesk_analyze
        Used for single file uploads via hiredesk_analyze endpoint
        Args:
            email: User email
            count: Number of files to increment (default 1)
        Returns: True if successful, False otherwise
        """
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

    async def increment_user_upload(self, email: str) -> bool:
        return await self.increment_files_uploaded(email, 1)

    async def get_feature_usage(self, email: str) -> Optional[Dict]:
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
        try:
            # Validate batch size (max 5 files per batch)
            if batch_size > self.batch_size_limit:
                return {
                    "allowed": False,
                    "reason": "batch_size_exceeded",
                    "message": f"Maximum {self.batch_size_limit} files per batch. You submitted {batch_size}.",
                    "batch_limit": self.batch_size_limit,
                    "submitted": batch_size
                }

            # Get current batch_analysis counter
            usage = await self.get_feature_usage(email)
            if usage is None:
                # Service unavailable - fail open
                return {
                    "allowed": True,
                    "reason": "service_unavailable",
                    "message": "Could not verify limit, allowing request",
                    "current_batch_count": 0,
                    "batch_size": batch_size,
                    "files_limit": self.free_tier_limit,
                    "files_allowed": batch_size,
                    "would_exceed_by": 0
                }

            current_batch_count = usage.get("batch_analysis", 0)
            
            # Check if adding this batch would exceed the free tier limit (10 files)
            total_after_upload = current_batch_count + batch_size
            
            if total_after_upload > self.free_tier_limit:
                # User would exceed the limit
                files_allowed = self.free_tier_limit - current_batch_count
                would_exceed_by = total_after_upload - self.free_tier_limit
                
                if files_allowed <= 0:
                    # User has already hit the limit
                    return {
                        "allowed": False,
                        "reason": "file_limit_exceeded",
                        "message": f"You've reached your free limit of {self.free_tier_limit} files. Cannot analyze more files.",
                        "current_files_uploaded": current_batch_count,
                        "batch_size": batch_size,
                        "files_limit": self.free_tier_limit,
                        "files_allowed": 0,
                        "would_exceed_by": batch_size
                    }
                else:
                    # User can upload some files, but not all
                    return {
                        "allowed": False,
                        "reason": "file_limit_exceeded",
                        "message": f"Uploading all {batch_size} files would exceed your free limit of {self.free_tier_limit}. You can upload {files_allowed} more file(s).",
                        "current_files_uploaded": current_batch_count,
                        "batch_size": batch_size,
                        "files_limit": self.free_tier_limit,
                        "files_allowed": files_allowed,
                        "would_exceed_by": would_exceed_by
                    }
            
            # All files are allowed
            return {
                "allowed": True,
                "reason": "ok",
                "message": f"Batch analysis allowed. Current files: {current_batch_count}, Uploading: {batch_size}",
                "current_batch_count": current_batch_count,
                "batch_size": batch_size,
                "files_limit": self.free_tier_limit,
                "files_allowed": batch_size,
                "would_exceed_by": 0
            }

        except Exception as e:
            # Fail open - allow request
            return {
                "allowed": True,
                "reason": "check_failed",
                "message": "Could not verify limit, allowing request",
                "current_batch_count": 0,
                "batch_size": batch_size,
                "files_limit": self.free_tier_limit,
                "files_allowed": batch_size,
                "would_exceed_by": 0
            }

    async def check_compare_resumes_limit(self, email: str, resume_count: int) -> Dict:
        try:
            # Validate resume count (max 5 resumes per comparison)
            if resume_count > self.batch_size_limit:
                return {
                    "allowed": False,
                    "reason": "resume_count_exceeded",
                    "message": f"Maximum {self.batch_size_limit} resumes allowed. You submitted {resume_count}.",
                    "resume_limit": self.batch_size_limit,
                    "submitted": resume_count
                }

            # Get current compare_resumes counter (independent check)
            usage = await self.get_feature_usage(email)
            if usage is None:
                # Service unavailable - fail open
                return {
                    "allowed": True,
                    "reason": "service_unavailable",
                    "message": "Could not verify limit, allowing request",
                    "current_compare_count": 0,
                    "resume_count": resume_count
                }

            current_compare_count = usage.get("compare_resumes", 0)

            return {
                "allowed": True,
                "reason": "ok",
                "message": f"Resume comparison allowed. Current comparisons: {current_compare_count}",
                "current_compare_count": current_compare_count,
                "resume_count": resume_count
            }

        except Exception as e:
            # Fail open - allow request
            return {
                "allowed": True,
                "reason": "check_failed",
                "message": "Could not verify limit, allowing request",
                "current_compare_count": 0,
                "resume_count": resume_count
            }

    async def check_selected_candidate_limit(self, email: str, file_count: int) -> Dict:
        """
        Check selected_candidate limit - INDEPENDENT from batch_analysis.
        Uses its own counter to track candidate selections.
        Args:
            email: User email
            file_count: Number of files being submitted (max 5 per batch)
        Returns:
            Dict indicating if the request is allowed
        """
        try:
            # Validate batch size (max 5 files per batch)
            if file_count > self.batch_size_limit:
                return {
                    "allowed": False,
                    "reason": "batch_size_exceeded",
                    "message": f"Maximum {self.batch_size_limit} files per batch. You submitted {file_count}.",
                    "batch_limit": self.batch_size_limit,
                    "submitted": file_count
                }

            # Get current selected_candidate counter (independent check)
            usage = await self.get_feature_usage(email)
            if usage is None:
                # Service unavailable - fail open
                return {
                    "allowed": True,
                    "reason": "service_unavailable",
                    "message": "Could not verify limit, allowing request",
                    "current_count": 0,
                    "file_count": file_count,
                    "files_limit": self.free_tier_limit,
                    "files_allowed": file_count,
                    "would_exceed_by": 0
                }

            # Get selected_candidate counter (separate from batch_analysis)
            current_selected_count = usage.get("selected_candidate", 0)
            
            # Check if adding these files would exceed the free tier limit (10 files)
            total_after_upload = current_selected_count + file_count
            
            if total_after_upload > self.free_tier_limit:
                # User would exceed the limit
                files_allowed = self.free_tier_limit - current_selected_count
                would_exceed_by = total_after_upload - self.free_tier_limit
                
                if files_allowed <= 0:
                    # User has already hit the limit
                    return {
                        "allowed": False,
                        "reason": "file_limit_exceeded",
                        "message": f"You've reached your free limit of {self.free_tier_limit} candidate selections. Upgrade to select more candidates.",
                        "current_count": current_selected_count,
                        "batch_size": file_count,
                        "files_limit": self.free_tier_limit,
                        "files_allowed": 0,
                        "would_exceed_by": file_count
                    }
                else:
                    # User can upload some files, but not all
                    return {
                        "allowed": False,
                        "reason": "file_limit_exceeded",
                        "message": f"Uploading all {file_count} files would exceed your free limit of {self.free_tier_limit}. You can select {files_allowed} more candidate(s).",
                        "current_count": current_selected_count,
                        "batch_size": file_count,
                        "files_limit": self.free_tier_limit,
                        "files_allowed": files_allowed,
                        "would_exceed_by": would_exceed_by
                    }
            
            # All files are allowed
            return {
                "allowed": True,
                "reason": "ok",
                "message": f"Candidate selection allowed. Current selections: {current_selected_count}, Submitting: {file_count}",
                "current_count": current_selected_count,
                "batch_size": file_count,
                "files_limit": self.free_tier_limit,
                "files_allowed": file_count,
                "would_exceed_by": 0
            }

        except Exception as e:
            # Fail open - allow request
            return {
                "allowed": True,
                "reason": "check_failed",
                "message": "Could not verify limit, allowing request",
                "current_count": 0,
                "batch_size": file_count,
                "files_limit": self.free_tier_limit,
                "files_allowed": file_count,
                "would_exceed_by": 0
            }

    async def increment_batch_counter(self, email: str, count: int = 1) -> bool:
        try:
            # Normalize email
            normalized_email = email.lower().strip()
            url = f"{self.auth_service_url}/increment-batch-analysis"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"email": normalized_email, "count": count},
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

    async def increment_compare_resumes_counter(self, email: str, count: int = 1) -> bool:
        """
        Increment compare_resumes counter.
        Args:
            email: User email
            count: Number of comparisons/files to increment (default 1)
        Returns: True if successful, False otherwise
        """
        try:
            # Normalize email
            normalized_email = email.lower().strip()
            url = f"{self.auth_service_url}/increment-compare-resumes"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"email": normalized_email, "count": count},
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
        return await self.increment_files_uploaded(email, count)

    async def increment_selected_candidate_counter(self, email: str, count: int = 1) -> bool:
        """
        Increment selected_candidate counter for selection-candidate endpoint.
        Args:
            email: User email
            count: Number of selections/files to increment (default 1)
        Returns: True if successful, False otherwise
        """
        try:
            # Normalize email
            normalized_email = email.lower().strip()
            url = f"{self.auth_service_url}/increment-selected-candidate"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"email": normalized_email, "count": count},
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

# Global instance
rate_limit_service = RateLimitService()