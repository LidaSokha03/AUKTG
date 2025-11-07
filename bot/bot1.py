from app.bot_instance import bot

import app.handlers.start
import app.handlers.auth

if __name__ == "__main__":
    print("🚀 Bot is running...")
    bot.infinity_polling()
