from app.bot_instance import bot
from app.db.models.user import User
from app.db.models.profile import Profile
from app.handlers.dashboard import dashboard
from app.db.database import db


def cv_history(message):
    tg_id = message.from_user.id

    profile_doc = db.profiles.find_one({"tg_id": tg_id})

    if not profile_doc or "cv_history" not in profile_doc or not profile_doc["cv_history"]:
        bot.reply_to(message, "You don't have CV 💾")
        return

    history = profile_doc["cv_history"]

    lines = ["📚 CV history:\n"]
    for cv in history:
        version = cv.get("version", "?")
        firstname = cv.get("firstname", "")
        lastname = cv.get("lastname", "")
        email = cv.get("email", "")
        lines.append(f"• Version {version}: {firstname} {lastname} ({email})")

    text = "\n".join(lines)
    bot.reply_to(message, text)

@bot.callback_query_handler(func=lambda call: call.data == "cv_history")
def cv_history_callback(call):
    cv_history(call.message)
    bot.answer_callback_query(call.id)

