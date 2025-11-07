from app.bot_instance import bot
from telebot import types

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    register_button = types.KeyboardButton('/register')
    login_button = types.KeyboardButton('/login')
    markup.add(register_button, login_button)

    bot.send_message(
    message.chat.id,
    "Вітання! 👋\n"
    "Виберіть одну опцію з двох нижче:\n\n"
    "/register — Зареєструватися в системі\n"
    "/login — Увійти в систему",
    reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Виберіть існуючу команду")
