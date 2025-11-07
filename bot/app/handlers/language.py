from telebot import types
from app.bot_instance import bot
from app.db.database import db


@bot.message_handler(commands=["language"])
def choose_language(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_uk"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    )

    bot.send_message(
        message.chat.id,
        "🌐 Обери мову:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def save_language(call):
    user_lang = call.data.split("_")[1]  # uk / en
    tg_id = call.from_user.id

    db.users.update_one(
        {"tg_id": tg_id},
        {"$set": {"language": user_lang}},
        upsert=True
    )

    lang_full = "Українська" if user_lang == "uk" else "English"

    bot.answer_callback_query(call.id, f"✅ Мову змінено на {lang_full}")
    bot.edit_message_text(
        f"✅ Мову збережено: <b>{lang_full}</b>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )
