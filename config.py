"""Configuration Dust MCP Server"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Dust API
    DUST_API_KEY = os.getenv("DUST_API_KEY", "")
    WORKSPACE_ID = os.getenv("DUST_WORKSPACE_ID", "")
    
    # Base URL — ne pas modifier
    API_BASE_URL = "https://dust.tt/api/v1"
    
    @classmethod
    def workspace_url(cls) -> str:
        return f"{cls.API_BASE_URL}/w/{cls.WORKSPACE_ID}"
    
    @classmethod
    def validate(cls) -> bool:
        if not cls.DUST_API_KEY:
            raise ValueError("DUST_API_KEY is required")
        if not cls.WORKSPACE_ID:
            raise ValueError("DUST_WORKSPACE_ID is required")
        return True