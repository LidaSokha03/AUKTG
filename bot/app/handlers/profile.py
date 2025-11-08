from app.bot_instance import bot
from app.db.models.profile import Profile, CV
from telebot import types

cv_cache = {}


@bot.message_handler(commands=["profile"])
def start_profile(message):
    ask_full_name(message)


@bot.callback_query_handler(func=lambda c: c.data == "profile")
def start_profile_callback(call):
    ask_full_name(call.message)
def ask_full_name(message):
    bot.send_message(
        message.chat.id,
        "✏️ Enter your *Full Name* (First + Last):\n\n"
        "-> Example:\n"
        "**Lida Sokha**",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(message, save_full_name)


def save_full_name(message):
    full_name = message.text.strip()

    if " " not in full_name:
        bot.send_message(message.chat.id, "⚠️ Format must be: *First name + Last name*. Try again.")
        return bot.register_next_step_handler(message, save_full_name)

    firstname, lastname = full_name.split(" ", 1)
    ask_email(message, firstname, lastname)
def ask_email(message, firstname, lastname):
    bot.send_message(
        message.chat.id,
        "📧 Enter your *Email*:\n\n-> Example:\n**lidasokha@gmail.com**",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(message, save_email, firstname, lastname)


def save_email(message, firstname, lastname):
    email = message.text.strip()
    ask_phone(message, firstname, lastname, email)

def ask_phone(message, firstname, lastname, email):
    bot.send_message(
        message.chat.id,
        "📱 Enter your *Phone Number*:\n\n-> Example:\n**+380964692379**",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(message, save_phone, firstname, lastname, email)


def save_phone(message, firstname, lastname, email):
    phone = message.text.strip()
    ask_education(message, firstname, lastname, email, phone)


def ask_education(message, firstname, lastname, email, phone):
    bot.send_message(
        message.chat.id,
        "🎓 Enter your *Education*:\n\n-> Example:\n"
        "**Ukrainian Catholic University: Lviv, Ukraine\n\
Bachelor's Degree in Business Analytics (2021 - 2025)\n\
- Coursework: Data Visualization, Machine Learning, Project Management, Marketing Analytics. etc...**",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(message, save_education, firstname, lastname, email, phone)


def save_education(message, firstname, lastname, email, phone):
    education = message.text.strip()
    ask_experience(message, firstname, lastname, email, phone, education)


def ask_experience(message, firstname, lastname, email, phone, education):
    bot.send_message(
        message.chat.id,
        "💼 Describe your *Experience*:\n\n-> Example:\n"
        "**Marketing Intern: SoftServe (June 2023 - September 2023)\n \
- Assisted with digital marketing campaigns focusing on social media and content analytics.\n\
- Created 15+ social posts that increased engagement by 25%. etc...**",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(message, save_experience, firstname, lastname, email, phone, education)


def save_experience(message, firstname, lastname, email, phone, education):
    experience = message.text.strip()
    ask_skills(message, firstname, lastname, email, phone, education, experience)


def ask_skills(message, firstname, lastname, email, phone, education, experience):
    bot.send_message(
        message.chat.id,
        "💪 Enter your *Skills* (comma separated):\n\n-> Example:\n"
        "**Python, SQL, Excel, Communication etc...**",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(message, save_skills, firstname, lastname, email, phone, education, experience)


def save_skills(message, firstname, lastname, email, phone, education, experience):
    skills = message.text.strip()
    ask_courses(message, firstname, lastname, email, phone, education, experience, skills)


def ask_courses(message, firstname, lastname, email, phone, education, experience, skills):
    bot.send_message(
        message.chat.id,
        "📚 Enter *Courses / Certifications*:\n\n-> Example:\n"
        "**Google Data Analytics Professional Certificate - Coursera (2023)\n\
- Hands-on training in SQL, Tableau, and data cleaning techniques. etc...**",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(message, finish_profile, firstname, lastname, email, phone, education, experience, skills)


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
        courses=courses,
    )

    preview = (
        f"✅ *CV Preview:*\n\n"
        f"*Name:* {firstname} {lastname}\n"
        f"*Email:* {email}\n"
        f"*Phone:* {phone}\n"
        f"*Education:* {education}\n"
        f"*Experience:* {experience}\n"
        f"*Skills:* {skills}\n"
        f"*Courses:* {courses}\n"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Save CV", callback_data="save_cv"),
        types.InlineKeyboardButton("✏️ Start over", callback_data="restart_cv"),
    )

    cv_cache[message.from_user.id] = cv

    bot.send_message(message.chat.id, preview, parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == "save_cv")
def save_cv(call):
    cv = cv_cache.get(call.from_user.id)
    Profile.save_profile(
        tg_id=call.from_user.id,
        full_name=f"{cv.firstname} {cv.lastname}",
        email=cv.email,
        cv=cv,
    )

    bot.edit_message_text(
        "✅ CV Saved.\n➡ Return to /dashboard",
        call.message.chat.id,
        call.message.message_id,
    )

    cv_cache.pop(call.from_user.id, None)

@bot.callback_query_handler(func=lambda c: c.data == "restart_cv")
def restart_cv(call):
    cv_cache.pop(call.from_user.id, None)

    bot.edit_message_text(
        "✏️ Okay, let's start again.\n\nEnter your *Full name* (Firstname Lastname):",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

    bot.register_next_step_handler(call.message, save_full_name)
