from app.bot_instance import bot
from telebot import types
from app.db.models.user import User

@bot.message_handler(commands=['register'])
def register_handler(message):
    tg_id = message.from_user.id
    user = User(tg_id)
    user.load()

    if user.is_registered:
        bot.reply_to(message, "Ви вже зареєстровані ✅")
        return


    user.set_registered()
    bot.reply_to(message, "Реєстрація успішна ✅")


@bot.message_handler(commands=['login'])
def login_handler(message):
    tg_id = message.from_user.id
    user = User(tg_id)
    user.load()

    if not user.is_registered:
        bot.reply_to(message, "Ви ще не зареєстровані. Спочатку використайте /register.")
        return

    # логіка логіну
    bot.reply_to(message, "Ви увійшли в систему ✅")