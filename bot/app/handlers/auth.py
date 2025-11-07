from app.bot_instance import bot
from telebot import types
from app.db.models.user import User
from app.db.models.profile import Profile
from app.handlers.dashboard import dashboard

registration_state: dict[int, dict] = {}

def start_registration(message, user: User):
    tg_id = message.from_user.id

    registration_state[tg_id] = {
        "step": "email",
        "profile": Profile(user_id=tg_id, fullname="", email=""),
        "user": user,
    }

    bot.reply_to(message, "Почнемо реєстрацію.\n"
                          "Спочатку введіть, будь ласка, ваш email:")

@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/') and m.from_user.id in registration_state)
def registration_flow(message):
    tg_id = message.from_user.id

    if tg_id not in registration_state:
        return

    state = registration_state[tg_id]
    step = state["step"]
    profile: Profile = state["profile"]
    user: User = state["user"]

    if step == "email":
        email = message.text.strip()
        profile.email = email
        profile.save()

        state["step"] = "fullname"
        bot.reply_to(message, "Дякую! Тепер введіть, будь ласка, ваше імʼя та прізвище:")
        return

    if step == "fullname":
        fullname = message.text.strip()
        profile.fullname = fullname
        profile.save()


        user.set_registered()


        registration_state.pop(tg_id, None)
        bot.reply_to(message, "Реєстрація завершена ✅")
        dashboard(message)
        return



@bot.message_handler(commands=['register'])
def register_handler(message):
    tg_id = message.from_user.id
    user = User(tg_id)
    user.load()

    if user.is_registered:
        bot.reply_to(message, "Ви вже зареєстровані ✅")
        dashboard
        return

    start_registration(message, user)


@bot.message_handler(commands=['login'])
def login_handler(message):
    tg_id = message.from_user.id
    user = User(tg_id)
    user.load()

    if not user.is_registered:
        bot.reply_to(message, "Ви ще не зареєстровані. Спочатку використайте /register.")
        return

    bot.reply_to(message, "Ви увійшли в систему ✅")
