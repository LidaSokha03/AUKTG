import telebot
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("API_TOKEN")
bot = telebot.TeleBot(token)
