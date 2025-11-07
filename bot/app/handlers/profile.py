from app.bot_instance import bot
from app.db.models.profile import Profile

# коли користувач вводить /profile
@bot.message_handler(commands=["profile"])
def start_profile_command(message):
    bot.send_message(message.chat.id, "✏️ Введи ПІБ:")
    bot.register_next_step_handler(message, get_name)

# коли користувач натискає кнопку "✏️ Заповнити CV"
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def start_profile_callback(call):
    bot.send_message(call.message.chat.id, "✏️ Введи ПІБ:")
    bot.register_next_step_handler(call.message, get_name)

def get_name(message):
    full_name = message.text
    bot.send_message(message.chat.id, "📧 Email:")
    bot.register_next_step_handler(message, get_email, full_name)

def get_email(message, full_name):
    email = message.text
    bot.send_message(message.chat.id, "💪 Скіли через кому:")
    bot.register_next_step_handler(message, get_skills, full_name, email)

def get_skills(message, full_name, email):
    skills = message.text
    bot.send_message(message.chat.id, "🚀 Опиши свій проєкт:")
    bot.register_next_step_handler(message, finish_profile, full_name, email, skills)

def finish_profile(message, full_name, email, skills):
    project = message.text

    Profile.save(
        tg_id=message.from_user.id,
        full_name=full_name,
        email=email,
        skills=skills,
        project=project
    )

    bot.send_message(message.chat.id, "✅ CV збережено!\n➡️ /dashboard")


from app.bot_instance import bot
from app.db.database import db
from pprint import pprint

@bot.message_handler(commands=["debug"])
def debug(message):
    tg_id = message.from_user.id
    user = db.profiles.find_one({"tg_id": tg_id})

    if not user:
        bot.send_message(message.chat.id, "❌ Даних не знайдено у MongoDB")
        return

    pprint(user)  # це в консоль
    bot.send_message(
        message.chat.id,
        f"✅ Знайдені дані у MongoDB:\n\n{user}"
    )
