from app.bot_instance import bot
import app.handlers.start
import app.handlers.dashboard
import app.handlers.profile
import app.handlers.cv_template
import app.handlers.language

if __name__ == "__main__":
    print("🚀 Bot is running...")
    bot.infinity_polling()
