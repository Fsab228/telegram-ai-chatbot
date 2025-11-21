# 🤖 Telegram AI Chatbot

<div align="center">

**Smart Telegram bot based on ChatGPT with conversation history support and admin panel**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.22+-green.svg)](https://github.com/aiogram/aiogram)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#-configuration)

</div>

---

## 📖 Description

Telegram AI Chatbot is a full-featured Telegram bot that uses the power of OpenAI API to communicate with users. The bot supports conversation history, admin panel, statistics, and much more.

We built this bot to simplify creating smart Telegram bots with AI support. The library has the following capabilities:

- **Asynchronous OpenAI API calls**, allowing multiple requests to be processed simultaneously
- **Simple creation and modification** of commands and handlers
- **Conversation history storage** for more meaningful responses
- **Admin panel** for bot management

The library is built as intuitively as possible. No complex concepts to learn.

## ✨ Features

### For Users
- 💬 **Smart communication** - answers questions using GPT-4o, GPT-4 Turbo, or GPT-3.5 Turbo
- 🧠 **Conversation context** - remembers last 10 messages for more meaningful responses
- 🔄 **History clearing** - ability to start a new conversation with one command
- 📝 **Clear errors** - informative messages when problems occur

### For Administrators
- 🔐 **Model management** - switch between GPT-4o, GPT-4 Turbo, and GPT-3.5 Turbo
- 📊 **Statistics** - track number of users and messages
- 📢 **Broadcasts** - send messages to all bot users
- 📋 **Logging** - detailed logs of all operations

## 🚀 Installation

Telegram AI Chatbot supports Python 3.8 and above.

To install dependencies:

```bash
pip install -r requirements.txt
```

This project depends on the following packages:

- `aiogram` - asynchronous framework for Telegram bots
- `openai` - client for OpenAI API
- `python-dotenv` - environment variable management
- `aiosqlite` - asynchronous SQLite operations

## 📝 Usage

After installing packages, create a `.env` file in the project root and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
TELEGRAM_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_user_id
LOG_LEVEL=INFO
```

### Quick Start

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/telegram-ai-chatbot.git
cd telegram-ai-chatbot
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**

Copy `env.example` to `.env` and fill in your data:

```bash
cp env.example .env
```

4. **Run the bot:**

```bash
python bot.py
```

Done! Bot is running and ready to work 🎉

## 💻 Usage Examples

### Main File (bot.py)

The main function is an async function that contains all business logic:

```python
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
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Handling User Messages

```python
@router.message(F.text)
async def handle_message(message: Message) -> None:
    """Handle regular text messages"""
    history = await db.get_conversation_history(message.from_user.id)
    
    ai_response = await openai_service.get_response(
        user_message=message.text,
        history=history
    )
    
    await message.answer(ai_response)
```

### Using Commands

**For users:**
```
/start - Start working with the bot
/help - Show list of commands
/reset - Clear conversation history
```

**For administrators:**
```
/setmodel gpt-4o - Change AI model
/stats - Show bot statistics
/broadcast Hello everyone! - Send message to all users
```

## 📋 API Reference

### Config

Class for working with bot configuration.

**Methods:**

- `Config.TELEGRAM_TOKEN()` - get Telegram bot token
- `Config.OPENAI_API_KEY()` - get OpenAI API key
- `Config.ADMIN_IDS()` - get list of administrator IDs
- `Config.validate()` - check presence of all required variables
- `Config.is_admin(user_id)` - check if user is administrator

### OpenAIService

Service for working with OpenAI API.

**Methods:**

- `get_response(user_message, history)` - get AI response (await)
- `set_model(model)` - set AI model
- `get_model()` - get current model

**Example:**

```python
from services.openai_service import OpenAIService

openai_service = OpenAIService()
response = await openai_service.get_response(
    user_message="Hello!",
    history=[]
)
```

### Database

Class for working with database.

**Methods:**

- `init_db()` - initialize database (await)
- `add_user(user_id, username, first_name)` - add user (await)
- `add_message(user_id, role, content)` - add message (await)
- `get_conversation_history(user_id, limit)` - get conversation history (await)
- `clear_conversation_history(user_id)` - clear history (await)
- `get_user_count()` - get user count (await)
- `get_message_count()` - get message count (await)

**Example:**

```python
from database.queries import Database

db = Database()
await db.init_db()

history = await db.get_conversation_history(user_id=123456789, limit=10)
```

## ⚙️ Configuration

### Changing Default Model

In `config.py` file:

```python
DEFAULT_MODEL: str = "gpt-4o"  # Available: gpt-4o, gpt-4-turbo, gpt-3.5-turbo
```

### Changing History Limit

In `config.py` file:

```python
CONVERSATION_HISTORY_LIMIT: int = 10  # Number of messages to store
```

### Adding Multiple Administrators

In `.env` file:

```env
ADMIN_ID=123456789,987654321,111222333
```

## 📁 Project Structure

```
telegram-ai-chatbot/
├── bot.py                 # Main bot file
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── .env.example          # Example environment variables file
├── .gitignore            # Git ignored files
├── database/
│   ├── __init__.py
│   ├── models.py         # Data models
│   └── queries.py        # Database queries
├── handlers/
│   ├── __init__.py
│   ├── user.py           # User command handlers
│   └── admin.py          # Administrator command handlers
└── services/
    ├── __init__.py
    └── openai_service.py # OpenAI API integration
```

## 🛠️ Technologies

- **Python 3.8+** - programming language
- **aiogram 3.22+** - modern asynchronous framework for Telegram bots
- **OpenAI API** - integration with ChatGPT (GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo)
- **SQLite** - database for storing users and history
- **python-dotenv** - environment variable management

## 🔒 Security

- ✅ All tokens are stored in `.env` file, which is not committed to Git
- ✅ `.env` file is added to `.gitignore`
- ✅ No personal data is stored in code
- ✅ It's recommended to regularly check API key usage in OpenAI Dashboard

## 🐛 Troubleshooting

### Bot Won't Start
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that `.env` file is created and contains all required variables
- Check logs in `bot.log` file

### Bot Not Responding to Messages
- Check Telegram Bot Token correctness
- Make sure bot is running and working
- Check logs for errors

### OpenAI API Errors
- Check API key correctness
- Make sure your OpenAI account has funds
- Check request limits in OpenAI Dashboard

## 🤝 Contributing

Telegram AI Chatbot is an open source project!

This project is constantly evolving, and we welcome any contribution or feedback.

**Open Tasks:**
- Adding support for other AI models
- Improving error handling
- Adding tests
- Performance optimization

If you want to contribute:

1. Fork the repository
2. Create a branch for new feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is created for educational purposes. Use at your own risk.

## ⭐ Acknowledgments

- [aiogram](https://github.com/aiogram/aiogram) - excellent framework for Telegram bots
- [OpenAI](https://openai.com/) - for powerful API and GPT models

---

<div align="center">

**Made with ❤️ using Python and OpenAI**

⭐ If you liked the project, give it a star!

</div>
