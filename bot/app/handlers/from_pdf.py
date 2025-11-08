from app.bot_instance import bot
from telebot import types
from app.db.models.user import User
from app.db.models.cv import CV
from app.services.pdf_export import cv_to_pdf
from pathlib import Path


@bot.message_handler(commands=['form_pdf_docx'])
def send_welcome(message):
    tg_id = message.from_user.id
    user = User(tg_id)

    if not user.exists():
        user.save()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    register_button = types.KeyboardButton('/register')
    login_button = types.KeyboardButton('/login')
    pdf_button = types.KeyboardButton('/export_pdf')
    markup.add(register_button, login_button, pdf_button)

    bot.send_message(
        message.chat.id,
        "Hello!\n"
        "Choose one from the options: \n"
        "/register - Register in the system\n"
        "/login - Log in to your account\n"
        "/export_pdf - Generate PDF of your CV\n"
        "/export_docx - Generate DOCX of your CV",
        reply_markup=markup
    )


@bot.message_handler(commands=['export_pdf'])
def export_pdf(message):
    chat_id = message.chat.id

    cv_data = CV(
        user_id=str(chat_id),
        firstname="Lida",
        lastname="Sokha",
        email="lidasosokha@gmail.com",
        phone="+380964692379",
        experience=(
            "Marketing Intern: SoftServe (June 2023 - September 2023)\n \
- Assisted with digital marketing campaigns focusing on social media and content analytics.\n\
- Created 15+ social posts that increased engagement by 25%.\n\
- Helped prepare performance reports and worked with the creative team on visual identity.\n\n\
Project Assistant: UCU Career Center (February 2022 - May 2023)\n\
- Coordinated internal communication between student bodies and employer partners.\n\
- Contributed to organizing the university job fair with over 40 companies.\n\
- Provided administrative support and event logistics management."
        ),
        education=(
            "Ukrainian Catholic University: Lviv, Ukraine\n\
Bachelor's Degree in Business Analytics (2021 - 2025)\n\
- Coursework: Data Visualization, Machine Learning, Project Management, Marketing Analytics.\n\
- GPA: 3.8 / 4.0"
        ),
        courses=(
            "Google Data Analytics Professional Certificate - Coursera (2023)\n\
- Hands-on training in SQL, Tableau, and data cleaning techniques.\n\n\
Soft Skills Training - EPAM University (2022)\n\
- Focused on teamwork, personal productivity, and structured problem-solving.\n\n\
LinkedIn Learning - Data Visualization with Python and Pandas (2023)"
        ),
        skills=(
            "Python, SQL, Excel, Tableau, Data Analysis, Communication, Project Coordination, \
Public Speaking, Critical Thinking, Teamwork"
        )
    )


    pdf_path = cv_to_pdf(cv_data)

    with open(pdf_path, "rb") as file:
        bot.send_document(chat_id, file, caption="Your PDF CV is ready!")

    exports_dir = Path("exports")
    for f in exports_dir.glob("*.pdf"):
        if f != pdf_path and f.stat().st_mtime < pdf_path.stat().st_mtime - 300:
            try:
                f.unlink()
            except Exception:
                pass


@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def echo_all(message):
    bot.reply_to(message, "Choose existing command")
