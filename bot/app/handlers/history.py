from app.bot_instance import bot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.services.interview_history import get_interview_history

@bot.message_handler(commands=["history"])
def history(msg):
    user_id = msg.from_user.id
    records = get_interview_history(user_id)

    if not records:
        bot.send_message(user_id, "Ви ще не проходили інтервʼю.")
        return

    text = "<b>Останні інтервʼю:</b>\n\n"

    for r in records:
        text += f"{r['score']}/{r['total']} — {r['timestamp'].strftime('%d.%m %H:%M')}\n"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Нове інтервʼю", callback_data="start_interview_again"))

    bot.send_message(msg.chat.id, text, parse_mode="HTML", reply_markup=kb)