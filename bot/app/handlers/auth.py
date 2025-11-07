from bot import bot

@bot.message_handler(commands=['/register', '/login'])
def send_welcome(message):
	bot.reply_to(message, "Вітання! Виберіть одну опцію з двох нижче:\n")
