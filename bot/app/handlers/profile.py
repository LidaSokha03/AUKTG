from app.bot_instance import bot
from app.db.models.profile import Profile, CV
from telebot import types


# коли користувач вводить /profile
@bot.message_handler(commands=["profile"])
def start_profile_command(message):
    ask_full_name(message)


# коли користувач натискає кнопку "✏️ Заповнити CV"
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def start_profile_callback(call):

    ask_full_name(call.message)


def ask_full_name(message):
    bot.send_message(
        message.chat.id,
        "✏️ Введи ПІБ (Ім'я Прізвище)\n\n"
        "Наприклад:\n"
        "-> **Віктор Сирок**",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, get_full_name)


def get_full_name(message):
    full_name = message.text.strip()

    if " " not in full_name:
        bot.send_message(message.chat.id, "❗ Формат: Ім'я + Прізвище\n➡ Спробуй знову.")
        return bot.register_next_step_handler(message, get_full_name)

    firstname, lastname = full_name.split(" ", 1)

    bot.send_message(
        message.chat.id,
        "📧 Введи email\n\n"
        "Наприклад:\n-> **lidasokha@gmail.com**",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, get_email, firstname, lastname)


def get_email(message, firstname, lastname):
    email = message.text.strip()

    bot.send_message(
        message.chat.id,
        "📱 Введи номер телефону\n\n"
        "Наприклад:\n-> **+380963469659**",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, get_phone, firstname, lastname, email)


def get_phone(message, firstname, lastname, email):
    phone = message.text.strip()

    bot.send_message(
        message.chat.id,
        "🎓 Введи свою освіту\n\n"
        "Наприклад:\n-> **Bachelor’s Degree in Business Analytics, UCU (2022–2026)**",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, get_education, firstname, lastname, email, phone)


def get_education(message, firstname, lastname, email, phone):
    education = message.text.strip()

    bot.send_message(
        message.chat.id,
        "💼 Опиши досвід (може бути навчальний)\n\n"
        "Наприклад:\n-> **Intern Data Analyst в SoftServe (3 місяці)**",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, get_experience, firstname, lastname, email, phone, education)


def get_experience(message, firstname, lastname, email, phone, education):
    experience = message.text.strip()

    bot.send_message(
        message.chat.id,
        "💪 Введи скіли (через кому)\n\n"
        "Приклад:\n-> **Python, SQL, Excel, Communication**",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, get_skills, firstname, lastname, email, phone, education, experience)


def get_skills(message, firstname, lastname, email, phone, education, experience):
    skills = message.text.strip()

    bot.send_message(
        message.chat.id,
        "📚 Введи курси / сертифікації (через кому)\n\n"
        "Приклад:\n-> **Google Data Analytics, Prometheus BA course**",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(
        message,
        finish_profile,
        firstname, lastname, email, phone, education, experience, skills
    )

def finish_profile(message, firstname, lastname, email, phone, education, experience, skills):
    courses = message.text.strip()

    cv = CV(
        user_id=message.from_user.id,
        firstname=firstname,
        lastname=lastname,
        email=email,
        phone=phone,
        education=education,
        experience=experience,
        skills=skills,
        courses=courses
    )

    # ✅ формуємо превʼю CV
    preview = (
        f"✅ *Ось що я зібрав:*\n\n"
        f"*Імʼя:* {firstname} {lastname}\n"
        f"*Email:* {email}\n"
        f"*Телефон:* {phone}\n"
        f"*Освіта:* {education}\n"
        f"*Досвід:* {experience}\n"
        f"*Скіли:* {skills}\n"
        f"*Курси:* {courses}\n"
    )

    # ✅ кнопки: зберегти або перезаповнити
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Зберегти", callback_data="save_cv"),
        types.InlineKeyboardButton("✏️ Заповнити заново", callback_data="restart_cv")
    )

    # тимчасово зберігаємо CV для підтвердження
    cv_cache[message.from_user.id] = cv

    bot.send_message(
        message.chat.id,
        preview,
        reply_markup=markup,
        parse_mode="Markdown"
    )

# DEBUG — дивитись що в БД
from app.db.database import db
from pprint import pprint

@bot.message_handler(commands=["debug"])
def debug(message):
    tg_id = message.from_user.id
    user = db.profiles.find_one({"tg_id": tg_id})

    if not user:
        bot.send_message(message.chat.id, "❌ Даних не знайдено у MongoDB")
        return

    pprint(user)
    bot.send_message(message.chat.id, f"✅ Дані з MongoDB:\n\n{user}")

cv_cache = {}  # тимчасове сховище

@bot.callback_query_handler(func=lambda c: c.data == "save_cv")
def save_cv(call):
    cv = cv_cache.get(call.from_user.id)
    if not cv:
        bot.answer_callback_query(call.id, "❌ Немає CV для збереження")
        return

    Profile.save_profile(
    tg_id=call.from_user.id,
    full_name=f"{cv.firstname} {cv.lastname}",
    email=cv.email,
    cv=cv
    )


    bot.edit_message_text(
        "✅ CV збережено!\n➡️ Перейди у меню /dashboard",
        call.message.chat.id,
        call.message.message_id
    )
    cv_cache.pop(call.from_user.id, None)


@bot.callback_query_handler(func=lambda c: c.data == "restart_cv")
def restart_cv(call):
    bot.edit_message_text(
        "✏️ Ок, заповнюємо спочатку.\nВведи ПІБ:",
        call.message.chat.id,
        call.message.message_id
    )
    bot.register_next_step_handler(call.message, get_full_name)
