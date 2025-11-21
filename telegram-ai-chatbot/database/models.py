"""
Database models for Telegram AI Chatbot
"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    """User model"""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    created_at: datetime
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Conversation:
    """Conversation message model"""
    user_id: int
    role: str
    content: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert conversation to dictionary"""
        return {
            "user_id": self.user_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
