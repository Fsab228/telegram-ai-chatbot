"""
OpenAI service for ChatGPT integration
"""
import logging
from typing import List, Dict, Optional
from openai import AsyncOpenAI, RateLimitError, APIError, APIConnectionError
from config import Config
from database.models import Conversation

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = Config.OPENAI_API_KEY()
        self.client = AsyncOpenAI(api_key=api_key)
        self.current_model = Config.DEFAULT_MODEL
    
    def set_model(self, model: str) -> bool:
        """Set AI model"""
        if model in Config.AVAILABLE_MODELS:
            self.current_model = model
            logger.info(f"Model changed to {model}")
            return True
        return False
    
    def get_model(self) -> str:
        """Get current AI model"""
        return self.current_model
    
    def _format_messages(self, history: List[Conversation], user_message: str) -> List[Dict[str, str]]:
        """Format conversation history for OpenAI API"""
        messages = []
        
        for conv in history:
            messages.append({
                "role": conv.role,
                "content": conv.content
            })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    async def get_response(self, user_message: str, history: List[Conversation]) -> Optional[str]:
        """
        Get AI response from OpenAI
        
        Args:
            user_message: User's message
            history: Conversation history
            
        Returns:
            AI response or None if error occurred
        """
        try:
            messages = self._format_messages(history, user_message)
            
            response = await self.client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                logger.warning("Empty response from OpenAI API")
                return None
                
        except RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded: {e}")
            raise Exception("Превышен лимит запросов к API. Пожалуйста, попробуйте позже.")
        
        except APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {e}")
            raise Exception("Ошибка подключения к API. Проверьте интернет-соединение.")
        
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            if "Invalid API key" in str(e) or "authentication" in str(e).lower():
                raise Exception("Неверный API ключ OpenAI. Обратитесь к администратору.")
            raise Exception(f"Ошибка API: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI service: {e}")
            raise Exception("Произошла непредвиденная ошибка. Попробуйте позже.")
