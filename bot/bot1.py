from app.bot_instance import bot

import app.handlers.history
import app.handlers.start
import app.handlers.auth
import app.handlers.interview 
import app.handlers.from_pdf


if __name__ == "__main__":
    print("🚀 Bot is running...")
    bot.infinity_polling()
