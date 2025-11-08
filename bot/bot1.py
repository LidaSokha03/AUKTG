from app.bot_instance import bot

import app.handlers.history
import app.handlers.start
import app.handlers.auth
import app.handlers.interview
import app.handlers.from_pdf
import app.handlers.dashboard
import app.handlers.profile
import app.handlers.cv_template
import app.handlers.language
import app.handlers.clear_history



if __name__ == "__main__":
    print("🚀 Bot is running...")
    bot.infinity_polling()
