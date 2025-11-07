from app.bot_instance import bot
from telebot import types
from app.db.models.user import User
from app.db.models.cv import CV
from app.services.pdf_export import cv_to_pdf
from pathlib import Path


@bot.message_handler(commands=['form_pdf'])
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
        "Вітання! 👋\n"
        "Виберіть одну опцію з нижче: \n"
        "/register — Зареєструватися\n"
        "/login — Увійти\n"
        "/export_pdf — Згенерувати PDF вашого CV",
        reply_markup=markup
    )


@bot.message_handler(commands=['export_pdf'])
def export_pdf(message):
    chat_id = message.chat.id

    # 1️⃣ Тут ти можеш дістати реальне CV користувача з БД (поки ставимо шаблон)
    cv_data = CV(
        user_id="message.from_user.id",
        firstname="Lida",
        lastname="Sokha",
        email="lidasosokha@gmail.com",
        phone="+380964692379",
        education="Bachelor's Degree in BA, UCU",
        experience='8',
        skills='nu9coiuetbvequio;qttttttttttttttttttiewrueiboyceiocecioeityctyuycw4iul tvq34 iutyq34tuiqcl4c34n834nox5y34c5834yn534y8c5n8nynttyuioljhfdsdfhjkljgfdssxdfghjkhgfdrtjkl;outedfvbkli76tghjkl;[p0o8uhjkl;[p0987yhjkl;[-0865rtyikop;oiytredfghjk]]]',
        languages='oeoooooooooooooooooooooooooooooooobcccccccccccccccccccccccccccc',
        projects="steeeeeeeeeeeeeeeeeeeeeeeeeeeb sssssssssssssssssssssssgrfghhhhhhhhhhhhhhhzzzzzzzzzzzzzzzzzzzzzzzzzzzzsghhhhhhhhhhhhhhhhhhhhhhhhhhhhhhjsdghkkkkkkkkkkkkkkkk"
    )

    # 2️⃣ Створюємо PDF
    pdf_path, created_at = cv_to_pdf(cv_data)

    # 3️⃣ Відправляємо файл користувачу
    with open(pdf_path, "rb") as file:
        bot.send_document(chat_id, file, caption=f"📄 Ваш CV створено!\nСтворено: {created_at:%Y-%m-%d %H:%M}")

    # 4️⃣ (опційно) видаляємо зайві старі файли
    exports_dir = Path("exports")
    for f in exports_dir.glob("*.pdf"):
        if f != pdf_path and f.stat().st_mtime < pdf_path.stat().st_mtime - 300:
            try:
                f.unlink()
            except Exception:
                pass


@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def echo_all(message):
    bot.reply_to(message, "Виберіть існуючу команду")