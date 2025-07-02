from datetime import datetime, timedelta
from typing import Dict
from fastapi import HTTPException, Request
import threading

class RateLimiter:
    
    def __init__(self):
        self._ip_data: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def check_rate_limit(self, ip_address: str, max_requests: int = 2) -> None:
        with self._lock:
            now = datetime.utcnow()
            
            if ip_address not in self._ip_data:
                self._ip_data[ip_address] = {
                    "count": 0,
                    "first_request": now,
                    "last_reset": now
                }
            
            ip_info = self._ip_data[ip_address]
            
            time_since_first = now - ip_info["first_request"]
            if time_since_first >= timedelta(hours=24):
                ip_info["count"] = 0
                ip_info["first_request"] = now
                ip_info["last_reset"] = now
            
            if ip_info["count"] >= max_requests:
                reset_time = ip_info["first_request"] + timedelta(hours=24)
                remaining_time = reset_time - now
                hours_remaining = int(remaining_time.total_seconds() // 3600)
                minutes_remaining = int((remaining_time.total_seconds() % 3600) // 60)
                
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": f"You have exceeded the daily limit of {max_requests} resume uploads per day.",
                        "reset_in": f"{hours_remaining}h {minutes_remaining}m",
                        "retry_after": int(remaining_time.total_seconds())
                    }
                )
            
            ip_info["count"] += 1
    
    def get_remaining_requests(self, ip_address: str, max_requests: int = 2) -> Dict:
        with self._lock:
            if ip_address not in self._ip_data:
                return {
                    "remaining": max_requests,
                    "reset_time": None,
                    "used": 0
                }
            
            ip_info = self._ip_data[ip_address]
            now = datetime.utcnow()
            
            time_since_first = now - ip_info["first_request"]
            if time_since_first >= timedelta(hours=24):
                return {
                    "remaining": max_requests,
                    "reset_time": None,
                    "used": 0
                }
            
            reset_time = ip_info["first_request"] + timedelta(hours=24)
            remaining = max(0, max_requests - ip_info["count"])
            
            return {
                "remaining": remaining,
                "reset_time": reset_time.isoformat(),
                "used": ip_info["count"]
            }

rate_limiter = RateLimiter()

def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    return request.client.host if request.client else "unknown"

async def check_upload_rate_limit(request: Request) -> None:
    client_ip = get_client_ip(request)
    rate_limiter.check_rate_limit(client_ip, max_requests=2)
