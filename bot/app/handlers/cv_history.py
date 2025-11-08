from app.bot_instance import bot
from app.db.database import db


def _send_no_cv(chat_id):
    bot.send_message(chat_id, "You don't have CV yet 💾")


def send_cv_history(tg_id: int, chat_id: int):
    query = {"tg_id": str(tg_id)}
    profile_doc = db.profiles.find_one(query)


    if profile_doc is None:
        _send_no_cv(chat_id)
        return

    history = profile_doc.get("cv_history") or []

    if not history:
        cv_doc = profile_doc.get("cv")
        if not cv_doc:
            _send_no_cv(chat_id)
            return
        history = [cv_doc]

    lines = ["📚 CV history:\n"]
    for cv in history:
        version = cv.get("version", "?")
        firstname = cv.get("firstname", "")
        lastname = cv.get("lastname", "")
        email = cv.get("email", "")
        lines.append(f"• Version {version}: {firstname} {lastname} ({email})")

    text = "\n".join(lines)
    bot.send_message(chat_id, text)


@bot.message_handler(commands=["cv_history"])
def cv_history_command(message):
    send_cv_history(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "cv_history")
def cv_history_callback(call):
    send_cv_history(call.from_user.id, call.message.chat.id)
    bot.answer_callback_query(call.id)
