"""
User command handlers
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.queries import Database
from services.openai_service import OpenAIService
from config import Config

logger = logging.getLogger(__name__)
router = Router()

db = Database()
openai_service = OpenAIService()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command"""
    try:
        await db.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        
        welcome_text = (
            "🤖 <b>Добро пожаловать в AI Chatbot!</b>\n\n"
            "Я бот на основе ChatGPT, готовый ответить на ваши вопросы.\n\n"
            "<b>Возможности:</b>\n"
            "• Общение с AI (GPT-4 Turbo)\n"
            "• Сохранение истории диалога\n"
            "• Умные ответы на любые вопросы\n\n"
            "<b>Команды:</b>\n"
            "/help - показать все команды\n"
            "/reset - очистить историю диалога\n"
            "/setmodel - изменить модель AI (только для админов)\n\n"
            "Просто напишите мне сообщение, и я отвечу! 💬"
        )
        
        await message.answer(welcome_text, parse_mode="HTML")
        logger.info(f"User {message.from_user.id} started the bot")
        
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}")
        await message.answer("Произошла ошибка при запуске бота. Попробуйте позже.")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command"""
    help_text = (
        "📋 <b>Доступные команды:</b>\n\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n"
        "/reset - очистить историю диалога\n"
        "/setmodel [gpt-4/gpt-3.5] - изменить модель AI (только для админов)\n\n"
        "Просто отправьте сообщение, и я отвечу используя ChatGPT! 💬"
    )
    
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    """Handle /reset command - clear conversation history"""
    try:
        await db.clear_conversation_history(message.from_user.id)
        await message.answer(
            "✅ История диалога очищена! Можете начать новый разговор.",
            parse_mode="HTML"
        )
        logger.info(f"User {message.from_user.id} cleared conversation history")
        
    except Exception as e:
        logger.error(f"Error in cmd_reset: {e}")
        await message.answer("Произошла ошибка при очистке истории. Попробуйте позже.")


@router.message(Command("setmodel"))
async def cmd_setmodel(message: Message) -> None:
    """Handle /setmodel command - change AI model (admin only)"""
    if not Config.is_admin(message.from_user.id):
        await message.answer("❌ Эта команда доступна только администраторам.")
        return
    
    command_parts = message.text.split()
    if len(command_parts) < 2:
        available_models = ", ".join(Config.AVAILABLE_MODELS)
        await message.answer(
            f"Использование: /setmodel [модель]\n\n"
            f"Доступные модели: {available_models}"
        )
        return
    
    model = command_parts[1].lower()
    
    if openai_service.set_model(model):
        await message.answer(f"✅ Модель изменена на: <b>{model}</b>", parse_mode="HTML")
        logger.info(f"Admin {message.from_user.id} changed model to {model}")
    else:
        available_models = ", ".join(Config.AVAILABLE_MODELS)
        await message.answer(
            f"❌ Неверная модель. Доступные модели: {available_models}"
        )


@router.message(F.text)
async def handle_message(message: Message) -> None:
    """Handle regular text messages"""
    try:
        await db.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        history = await db.get_conversation_history(message.from_user.id)
        
        try:
            ai_response = await openai_service.get_response(
                user_message=message.text,
                history=history
            )
        except Exception as e:
            error_message = str(e)
            await message.answer(f"❌ {error_message}")
            logger.error(f"OpenAI API error for user {message.from_user.id}: {e}")
            return
        
        if not ai_response:
            await message.answer("Извините, не удалось получить ответ. Попробуйте позже.")
            return
        
        await db.add_message(
            user_id=message.from_user.id,
            role="user",
            content=message.text
        )
        
        await db.add_message(
            user_id=message.from_user.id,
            role="assistant",
            content=ai_response
        )
        
        await message.answer(ai_response)
        logger.info(f"Sent AI response to user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error handling message from user {message.from_user.id}: {e}")
        await message.answer(
            "Произошла непредвиденная ошибка. Попробуйте позже или используйте /reset для очистки истории."
        )
