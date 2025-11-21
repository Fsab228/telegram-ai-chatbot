"""
Main bot file for Telegram AI Chatbot
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import Config
from database.queries import Database
from handlers import user, admin

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main function to start the bot"""
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
        
        db = Database()
        await db.init_db()
        logger.info("Database initialized")
        
        bot = Bot(
            token=Config.TELEGRAM_TOKEN(),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        
        dp.include_router(user.router)
        dp.include_router(admin.router)
        logger.info("Routers registered")
        
        bot_info = await bot.get_me()
        logger.info(f"Bot started: @{bot_info.username} ({bot_info.first_name})")
        
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if 'bot' in locals():
            await bot.session.close()
        logger.info("Bot session closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
