import os
import telebot
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("API_TOKEN")

if not token:
    raise RuntimeError("API_TOKEN не знайдений у .env")

bot = telebot.TeleBot(token)