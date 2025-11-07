import telebot
from dotenv import load_dotenv
import os
from app.handlers import start

load_dotenv()
token = os.getenv("API_TOKEN")
bot = telebot.TeleBot(token)

print("✅...")
bot.infinity_polling()