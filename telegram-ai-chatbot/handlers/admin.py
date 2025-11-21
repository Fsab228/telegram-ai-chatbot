"""
Admin command handlers
"""
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database.queries import Database
from config import Config

logger = logging.getLogger(__name__)
router = Router()

db = Database()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return Config.is_admin(user_id)


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    """Handle /stats command - show bot statistics (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Эта команда доступна только администраторам.")
        return
    
    try:
        user_count = await db.get_user_count()
        message_count = await db.get_message_count()
        
        stats_text = (
            "📊 <b>Статистика бота:</b>\n\n"
            f"👥 Всего пользователей: <b>{user_count}</b>\n"
            f"💬 Всего сообщений: <b>{message_count}</b>\n"
        )
        
        try:
            from services.openai_service import OpenAIService
            openai_service = OpenAIService()
            stats_text += f"🤖 Текущая модель: <b>{openai_service.get_model()}</b>\n"
        except:
            pass
        
        await message.answer(stats_text, parse_mode="HTML")
        logger.info(f"Admin {message.from_user.id} requested stats")
        
    except Exception as e:
        logger.error(f"Error in cmd_stats: {e}")
        await message.answer("Произошла ошибка при получении статистики.")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message) -> None:
    """Handle /broadcast command - send message to all users (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Эта команда доступна только администраторам.")
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        await message.answer(
            "Использование: /broadcast [сообщение]\n\n"
            "Отправит сообщение всем пользователям бота."
        )
        return
    
    broadcast_text = command_parts[1]
    
    try:
        user_ids = await db.get_all_user_ids()
        
        if not user_ids:
            await message.answer("Нет пользователей для рассылки.")
            return
        
        success_count = 0
        fail_count = 0
        
        for user_id in user_ids:
            try:
                await message.bot.send_message(user_id, broadcast_text)
                success_count += 1
            except Exception as e:
                fail_count += 1
                logger.warning(f"Failed to send broadcast to user {user_id}: {e}")
        
        result_text = (
            f"📢 <b>Рассылка завершена:</b>\n\n"
            f"✅ Успешно отправлено: <b>{success_count}</b>\n"
            f"❌ Ошибок: <b>{fail_count}</b>"
        )
        
        await message.answer(result_text, parse_mode="HTML")
        logger.info(f"Admin {message.from_user.id} sent broadcast to {success_count} users")
        
    except Exception as e:
        logger.error(f"Error in cmd_broadcast: {e}")
        await message.answer("Произошла ошибка при рассылке сообщений.")
