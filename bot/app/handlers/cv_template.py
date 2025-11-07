from telebot import types
from app.bot_instance import bot
from app.db.models.profile import Profile

@bot.callback_query_handler(func=lambda c: c.data == "template")
def choose_template(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🟦 Template A", callback_data="tmpl_A"))
    markup.add(types.InlineKeyboardButton("🟩 Template B", callback_data="tmpl_B"))

    bot.edit_message_text("Обери шаблон:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("tmpl_"))
def save_template(call):
    template = call.data[-1]

    Profile.save_template(call.from_user.id, template)

    bot.answer_callback_query(call.id, text="✅ Шаблон збережено")
    bot.edit_message_text("✅ Готово! Шаблон вибрано ✅", call.message.chat.id, call.message.message_id)
