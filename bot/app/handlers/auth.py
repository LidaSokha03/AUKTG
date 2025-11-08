from app.bot_instance import bot
from telebot import types
from app.db.models.user import User
from app.db.models.profile import Profile
from app.handlers.dashboard import dashboard


registration_state: dict[int, dict] = {}


def show_main_menu(message):
    tg_id = message.from_user.id
    user = User(tg_id)
    user.load()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if not user.exists or not user.is_registered:
        keyboard.add(
            types.KeyboardButton("📝 Register"),
            types.KeyboardButton("🔐 Login")
        )
    else:
        keyboard.add(
            types.KeyboardButton("📄 Dashboard")
        )

    bot.send_message(
        message.chat.id,
        "Choose an option:",
        reply_markup=keyboard
    )


def start_registration(message, user: User):
    tg_id = message.from_user.id

    registration_state[tg_id] = {
        "step": "email",
        "profile": Profile(user_id=tg_id, fullname="", email=""),
        "user": user,
    }

    bot.reply_to(message, "Start registration.\nWrite down your email:")


@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/') and m.from_user.id in registration_state)
def registration_flow(message):
    tg_id = message.from_user.id
    state = registration_state[tg_id]
    step = state["step"]
    profile: Profile = state["profile"]
    user: User = state["user"]

    if step == "email":
        profile.email = message.text.strip()
        profile.save()

        state["step"] = "fullname"
        bot.reply_to(message, "Thank you! Now enter your firstname and surname:")
        return

    if step == "fullname":
        profile.fullname = message.text.strip()
        profile.save()
        user.set_registered()
        registration_state.pop(tg_id, None)

        bot.reply_to(message, "Registration completed ✅")

        show_main_menu(message)   
        dashboard(message) 
        return


@bot.message_handler(commands=['register'])
def register_handler(message):
    tg_id = message.from_user.id
    user = User(tg_id)
    user.load()

    if user.is_registered:
        bot.reply_to(message, "You are already registered ✅")
        show_main_menu(message)
        dashboard(message)
        return

    start_registration(message, user)


@bot.message_handler(commands=['login'])
def login_handler(message):
    tg_id = message.from_user.id
    user = User(tg_id)
    user.load()

    if not user.exists or not user.is_registered:
        bot.reply_to(message, "You are not registered. Please use /register.")
        return

    bot.reply_to(message, "You are logged in ✅")

    show_main_menu(message)
    dashboard(message)


@bot.message_handler(func=lambda m: m.text in ['📝 Register', '🔐 Login', '📄 Dashboard', 'Dashboard'])
def main_menu_buttons(message):
    if message.text in ['📝 Register']:
        return register_handler(message)

    if message.text in ['🔐 Login']:
        return login_handler(message)

    if message.text in ['📄 Dashboard', 'Dashboard']:
        return dashboard(message)
