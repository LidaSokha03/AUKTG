from app.bot_instance import bot

import app.handlers.history
import app.handlers.start
import app.handlers.auth
import app.handlers.interview
import app.handlers.from_pdf
import app.handlers.dashboard
import app.handlers.profile
import app.handlers.clear_history
import app.handlers.cv_history



if __name__ == "__main__":
    print("...")
    bot.infinity_polling()
