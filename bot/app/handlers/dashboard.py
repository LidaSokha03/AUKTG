from telebot import types
from app.bot_instance import bot

@bot.message_handler(commands=["dashboard"])
def dashboard(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✏️ Make up CV", callback_data="profile"))
    markup.add(types.InlineKeyboardButton("📁 CV history", callback_data="cv_history"))
    markup.add(types.InlineKeyboardButton("📝 Start interview", callback_data="interview"))
    markup.add(types.InlineKeyboardButton("🌐 Language", callback_data="language"))

    bot.send_message(
        message.chat.id,
        "<b>📄 Dashboard</b>\nChoose action:",
        reply_markup=markup,
        parse_mode="HTML"
    )
