from datetime import datetime, timedelta
from typing import Dict
from fastapi import HTTPException, Request
import threading

class RateLimiter:
    
    def __init__(self):
        self._ip_data: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def _get_next_midnight_utc(self) -> datetime:
        now = datetime.utcnow()
        today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now > today_midnight:
            return today_midnight + timedelta(days=1)
        return today_midnight
    
    def _should_reset_counter(self, last_reset: datetime) -> bool:
        now = datetime.utcnow()
        today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return last_reset < today_midnight
        return last_reset < today_midnight
    
    def check_rate_limit(self, ip_address: str, max_requests: int = 2) -> None:
        with self._lock:
            now = datetime.utcnow()
            
            if ip_address not in self._ip_data:
                self._ip_data[ip_address] = {
                    "count": 0,
                    "last_reset": now
                }
            
            ip_info = self._ip_data[ip_address]
            
            if self._should_reset_counter(ip_info["last_reset"]):
                ip_info["count"] = 0
                ip_info["last_reset"] = now
            
            if ip_info["count"] >= max_requests:
                next_midnight = self._get_next_midnight_utc()
                remaining_time = next_midnight - now
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
                    "reset_time": self._get_next_midnight_utc().isoformat(),
                    "used": 0
                }
            
            ip_info = self._ip_data[ip_address]
            now = datetime.utcnow()
            
            if self._should_reset_counter(ip_info["last_reset"]):
                ip_info["count"] = 0
                ip_info["last_reset"] = now
            
            next_midnight = self._get_next_midnight_utc()
            remaining = max(0, max_requests - ip_info["count"])
            
            return {
                "remaining": remaining,
                "reset_time": next_midnight.isoformat(),
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
