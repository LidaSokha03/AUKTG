from bot import bot

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Вітання! Виберіть одну опцію з двох нижче:\n"
    "/register - Зареєструватися в системі\n"
    "/login - Увійти в систему")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, "Виберіть існуючу команду")
