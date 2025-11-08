from telebot import types
from app.bot_instance import bot

@bot.message_handler(commands=["dashboard"])
def dashboard(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✏️ Заповнити CV", callback_data="profile"))
    markup.add(types.InlineKeyboardButton("📄 Обрати шаблон", callback_data="template"))
    markup.add(types.InlineKeyboardButton("🌐 Мова", callback_data="language"))

    bot.send_message(
        message.chat.id,
        "<b>📄 Dashboard</b>\nОберіть дію:",
        reply_markup=markup,
        parse_mode="HTML"
    )
