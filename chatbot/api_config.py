"""
API Configuration for Driving License Management System
This file contains all API-related configuration and utility functions.
"""

import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class APIConfig:
    """Configuration class for API settings."""
    
    # Base API URL
    BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7500")
    
    # API Endpoints
    ENDPOINTS = {
        "create_license": "/drivingLicense/create",
        "get_license_details": "/drivingLicense/getLicenseDetails",
        "update_license_status": "/drivingLicense/updateStatus",
        "change_address": "/drivingLicense/changeAddress",
        "renew_license": "/drivingLicense/renewLicense",
    }
    

    # Authentication
    AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "<token>")
    
    # Request timeout (in seconds)
    TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    
    # Retry configuration
    MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("API_RETRY_DELAY", "1"))
    
    @classmethod
    def get_endpoint_url(cls, endpoint_name: str) -> str:
        """Get full URL for a specific endpoint."""
        if endpoint_name not in cls.ENDPOINTS:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")
        
        return f"{cls.BASE_URL}{cls.ENDPOINTS[endpoint_name]}"
    
    @classmethod
    def get_auth_headers(cls) -> Dict[str, str]:
        """Get authentication headers."""
        return {
            "Authorization": f"Bearer {cls.AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate API configuration."""
        try:
            # Check if base URL is accessible
            import requests
            response = requests.get(cls.BASE_URL, timeout=5)
            logger.info(f"API base URL is accessible: {cls.BASE_URL}")
            return True
        except Exception as e:
            logger.error(f"API configuration validation failed: {e}")
            return False

# API Response Models
class APIResponse:
    """Standard API response structure."""
    
    def __init__(self, success: bool, message: str, data: Optional[Dict] = None):
        self.success = success
        self.message = message
        self.data = data or {}
    
    @classmethod
    def from_dict(cls, response_dict: Dict) -> 'APIResponse':
        """Create APIResponse from dictionary."""
        return cls(
            success=response_dict.get("success", False),
            message=response_dict.get("message", ""),
            data=response_dict.get("data", {})
        )
    
    def is_success(self) -> bool:
        """Check if response indicates success."""
        return self.success
    
    def get_data(self, key: str, default=None):
        """Get data value with default fallback."""
        return self.data.get(key, default)

# Error handling
class APIError(Exception):
    """Custom exception for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

# Utility functions
def format_license_number(license_number: str) -> str:
    """Format license number for display."""
    if not license_number:
        return ""
    
    # Remove common separators and format
    clean_number = license_number.replace("-", "").replace("_", "").replace(" ", "")
    
    # Add separators for better readability (DL-123-456 format)
    if len(clean_number) >= 6:
        return f"{clean_number[:2]}-{clean_number[2:5]}-{clean_number[5:]}"
    
    return clean_number

def parse_api_date(date_string: str) -> Optional[str]:
    """Parse API date string and return formatted date."""
    try:
        from datetime import datetime
        
        # Handle ISO format dates from API
        if 'T' in date_string:
            # Remove timezone info if present
            date_part = date_string.split('T')[0]
            return date_part
        else:
            return date_string[:10]  # Return first 10 characters (YYYY-MM-DD)
            
    except Exception as e:
        logger.error(f"Date parsing failed: {e}")
        return None

def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
    """Mask sensitive data for display."""
    if not data or len(data) <= 4:
        return mask_char * len(data) if data else ""
    
    return data[:2] + mask_char * (len(data) - 4) + data[-2:]
