from app.bot_instance import bot
from telebot import types
from app.db.models.user import User

@bot.message_handler(commands=['start'])
def send_welcome(message):
    tg_id = message.from_user.id
    user = User(tg_id)

    if not user.exists():
        user.save()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    register_button = types.KeyboardButton('/register')
    login_button = types.KeyboardButton('/login')
    interview_button = types.KeyboardButton('/interview')  # кнопка інтервʼю ✅

    markup.add(register_button, login_button)
    markup.add(interview_button)

    bot.send_message(
        message.chat.id,
        "Вітання! 👋\n"
        "📝 /register — Зареєструватися\n"
        "🔐 /login — Увійти\n"
        "🧠 /interview — Почати технічне інтервʼю\n",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def fallback(message):
    bot.reply_to(message, "Виберіть існуючу команду ✅")
