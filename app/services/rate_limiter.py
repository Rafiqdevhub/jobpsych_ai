from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException, Request, Depends
import threading

class RateLimiter:
    
    def __init__(self):
        self._ip_data: Dict[str, Dict] = {}
        self._user_data: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def check_ip_rate_limit(self, ip_address: str, max_requests: int = 2) -> None:
        """Check rate limit for anonymous users (IP-based)"""
        with self._lock:
            if ip_address not in self._ip_data:
                self._ip_data[ip_address] = {
                    "count": 0,
                    "first_upload_time": datetime.utcnow().isoformat()
                }
            
            ip_info = self._ip_data[ip_address]
            
            if ip_info["count"] >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Free limit exceeded",
                        "message": f"You have used all {max_requests} free resume analyses from this location. Sign up to continue with more analyses!",
                        "uploads_used": ip_info["count"],
                        "uploads_limit": max_requests,
                        "first_upload": ip_info["first_upload_time"],
                        "requires_auth": True,
                        "auth_message": "Create an account to unlock more resume analyses",
                        "signup_url": "/auth/signup"
                    }
                )
            
            ip_info["count"] += 1
    
    def check_user_rate_limit(self, user_id: str, is_premium: bool = False) -> None:
        """Check rate limit for authenticated users"""
        with self._lock:
            # Premium users have unlimited access
            if is_premium:
                return
            
            # Free authenticated users get additional uploads beyond IP limit
            max_requests = 2  # Additional uploads for authenticated free users
            
            if user_id not in self._user_data:
                self._user_data[user_id] = {
                    "count": 0,
                    "first_upload_time": datetime.utcnow().isoformat(),
                    "tier": "free"
                }
            
            user_info = self._user_data[user_id]
            
            if user_info["count"] >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Free tier limit exceeded", 
                        "message": f"You have used all {max_requests} free analyses in your account. Upgrade to premium for unlimited access!",
                        "uploads_used": user_info["count"],
                        "uploads_limit": max_requests,
                        "first_upload": user_info["first_upload_time"],
                        "requires_payment": True,
                        "tier": "free",
                        "upgrade_url": "/api/upgrade-plan"
                    }
                )
            
            user_info["count"] += 1
    
    def get_ip_remaining_requests(self, ip_address: str, max_requests: int = 2) -> Dict:
        """Get remaining requests for anonymous users (IP-based)"""
        with self._lock:
            if ip_address not in self._ip_data:
                return {
                    "remaining": max_requests,
                    "used": 0,
                    "tier": "anonymous",
                    "limit_type": "ip_based"
                }
            
            ip_info = self._ip_data[ip_address]
            remaining = max(0, max_requests - ip_info["count"])
            
            return {
                "remaining": remaining,
                "used": ip_info["count"],
                "tier": "anonymous",
                "limit_type": "ip_based",
                "first_upload": ip_info.get("first_upload_time", datetime.utcnow().isoformat())
            }
    
    def get_user_remaining_requests(self, user_id: str, is_premium: bool = False, max_requests: int = 2) -> Dict:
        """Get remaining requests for authenticated users"""
        with self._lock:
            if is_premium:
                return {
                    "remaining": "unlimited",
                    "used": self._user_data.get(user_id, {}).get("count", 0),
                    "tier": "premium",
                    "limit_type": "user_based"
                }
            
            if user_id not in self._user_data:
                return {
                    "remaining": max_requests,
                    "used": 0,
                    "tier": "free",
                    "limit_type": "user_based"
                }
            
            user_info = self._user_data[user_id]
            remaining = max(0, max_requests - user_info["count"])
            
            return {
                "remaining": remaining,
                "used": user_info["count"],
                "tier": "free",
                "limit_type": "user_based",
                "first_upload": user_info.get("first_upload_time", datetime.utcnow().isoformat())
            }

rate_limiter = RateLimiter()

def get_client_ip(request: Request) -> str:
    """Get client IP from request headers (kept for backward compatibility)"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    return request.client.host if request.client else "unknown"

def get_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user ID from authentication token in request.
    
    Returns None if no valid authentication is found.
    """
    # Try to get user ID from auth token/session
    auth_token = request.headers.get("Authorization")
    
    if auth_token and auth_token.startswith("Bearer "):
        try:
            # Placeholder: extract user ID from token - replace with actual auth logic
            token = auth_token.split("Bearer ")[1]
            # This is where you'd decode your token to get the user ID
            # For now, we're just using the token itself as the ID
            return token  # Return just the token as user ID
        except Exception:
            pass
    
    return None  # No valid authentication found

def is_premium_user(user_id: str) -> bool:
    """Check if user has premium subscription.
    
    This is a placeholder - replace with your actual premium check logic.
    """
    # TODO: Implement actual premium user check
    # This could check a database, external service, etc.
    # For now, return False (all users are free tier)
    return False

async def check_upload_rate_limit(request: Request) -> None:
    """Check if the user has exceeded their upload rate limit.
    
    Implements two-tier system:
    1. Anonymous users: IP-based limit (2 uploads per IP)
    2. Authenticated users: User-based limit (additional uploads after auth)
    """
    client_ip = get_client_ip(request)
    user_id = get_user_id_from_request(request)
    
    # Skip rate limiting for localhost/development environments
    if client_ip == "127.0.0.1" or client_ip == "localhost" or client_ip.startswith("192.168.") or client_ip.startswith("10."):
        return  # No rate limiting for local development
    
    if user_id:
        # Authenticated user - check user-based limits
        is_premium = is_premium_user(user_id)
        rate_limiter.check_user_rate_limit(user_id, is_premium=is_premium)
    else:
        # Anonymous user - check IP-based limits
        rate_limiter.check_ip_rate_limit(client_ip, max_requests=2)
