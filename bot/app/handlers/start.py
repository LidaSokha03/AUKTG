from app.bot_instance import bot
from telebot import types
from app.db.models.user import User
from app.handlers.auth import registration_state

@bot.message_handler(commands=['start'])
def send_welcome(message):
    tg_id = message.from_user.id
    user = User(tg_id)

    if not user.exists():
        user.save()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    register_button = types.KeyboardButton('📝 Register')
    login_button = types.KeyboardButton('🔐 Login')

    markup.add(register_button, login_button)

    bot.send_message(
    message.chat.id,
    "Hello! 👋\n"
    "Choose one from the options:\n\n"
    "/register — Register in the system\n"
    "/login — Log in to your account",
    reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/'))
def echo_all(message):
    tg_id = message.from_user.id
    if tg_id in registration_state:
        return
    bot.reply_to(message, "Command not recognized.")

