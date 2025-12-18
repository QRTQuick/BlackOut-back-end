import os
import secrets
import hashlib
from typing import List, Optional

class APIKeyManager:
    def __init__(self):
        # For production, use a database or secure storage
        self.valid_keys = {
            "demo-key": {"name": "Demo Access", "rate_limit": 10, "active": True},
            "dev-key": {"name": "Developer Access", "rate_limit": 100, "active": True},
            "premium-key": {"name": "Premium Access", "rate_limit": 1000, "active": True}
        }
    
    def generate_api_key(self, prefix: str = "nbl") -> str:
        """Generate a new API key"""
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"
    
    def validate_key(self, api_key: str) -> bool:
        """Validate if API key is active and valid"""
        return api_key in self.valid_keys and self.valid_keys[api_key]["active"]
    
    def get_key_info(self, api_key: str) -> Optional[dict]:
        """Get information about an API key"""
        return self.valid_keys.get(api_key)

# Global instance
api_key_manager = APIKeyManager()

# For development - allow the original key
DEVELOPMENT_KEY = os.getenv("API_KEY", "blackout-secret-key")
api_key_manager.valid_keys[DEVELOPMENT_KEY] = {
    "name": "Development Key", 
    "rate_limit": 50, 
    "active": True
}