"""
Configuration module for Telegram AI Chatbot
"""
import os
from pathlib import Path
from typing import Optional

try:
    base_dir = Path(__file__).parent.absolute()
except:
    base_dir = Path(os.getcwd())

env_file = base_dir / ".env"

if not env_file.exists():
    cwd_env = Path(os.getcwd()) / ".env"
    if cwd_env.exists():
        env_file = cwd_env
        base_dir = Path(os.getcwd())

def _load_env_file():
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        os.environ[key] = value

try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=str(env_file), override=True)
    else:
        load_dotenv()
except ImportError:
    pass

_load_env_file()


class Config:
    """Bot configuration settings"""
    
    DEFAULT_MODEL: str = "gpt-4o"
    AVAILABLE_MODELS: list[str] = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    CONVERSATION_HISTORY_LIMIT: int = 10
    DATABASE_PATH: str = "bot_database.db"
    
    @classmethod
    def TELEGRAM_TOKEN(cls) -> str:
        return os.getenv("TELEGRAM_TOKEN", "")
    
    @classmethod
    def OPENAI_API_KEY(cls) -> str:
        return os.getenv("OPENAI_API_KEY", "")
    
    @classmethod
    def ADMIN_IDS(cls) -> list[int]:
        admin_ids_str = os.getenv("ADMIN_ID", "")
        return [
            int(admin_id.strip()) 
            for admin_id in admin_ids_str.split(",") 
            if admin_id.strip().isdigit()
        ]
    
    @classmethod
    def LOG_LEVEL(cls) -> str:
        return os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        token = cls.TELEGRAM_TOKEN()
        api_key = cls.OPENAI_API_KEY()
        
        if not token:
            env_path = base_dir / ".env"
            error_msg = (
                f"TELEGRAM_TOKEN is not set in environment variables.\n"
                f"Please check that .env file exists at: {env_path}\n"
                f"File exists: {env_path.exists()}"
            )
            raise ValueError(error_msg)
        if not api_key:
            env_path = base_dir / ".env"
            error_msg = (
                f"OPENAI_API_KEY is not set in environment variables.\n"
                f"Please check that .env file exists at: {env_path}\n"
                f"File exists: {env_path.exists()}"
            )
            raise ValueError(error_msg)
        return True
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in cls.ADMIN_IDS()
