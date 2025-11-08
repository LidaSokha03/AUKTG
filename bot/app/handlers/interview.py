from app.bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.services.llm_questions import generate_mcq_question
from app.services.interview_history import save_interview_result
import textwrap

user_quiz = {}

MAX_LEN = 28  # оптимально для телефона


def format_text(text):
    text = text.strip()
    if len(text) <= MAX_LEN:
        return text
    return "\n".join(textwrap.wrap(text, MAX_LEN))


@bot.message_handler(commands=["interview"])
def start_mcq(msg):
    user_id = msg.from_user.id

    if user_id in user_quiz:
        bot.send_message(user_id, "⚠️ Ви вже проходите тест! Завершіть його.")
        return

    user_quiz[user_id] = {"score": 0, "q": 0, "questions": []}

    bot.send_message(
        user_id,
        "🧠 Починаємо тест! Тисни на правильну відповідь 👇"
    )
    send_new_question(user_id)


def send_new_question(user_id):
    q = generate_mcq_question()

    # ✅ fallback якщо API недоступне
    if not q or "options" not in q or "correct_index" not in q:
        q = {
            "question": "Що таке ООП?",
            "options": [
                "Парадигма програмування ✅",
                "Мова Python",
                "Операційна система",
                "Тип бази даних"
            ],
            "correct_index": 0
        }

    user_quiz[user_id]["current"] = q
    user_quiz[user_id]["questions"].append(q)

    kb = InlineKeyboardMarkup(row_width=1)

    for i, opt in enumerate(q["options"]):
        pretty = format_text(opt)
        kb.add(InlineKeyboardButton(pretty, callback_data=f"answer_{i}"))

    bot.send_message(
        user_id,
        f"❓ {format_text(q['question'])}",
        reply_markup=kb
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("answer_"))
def handle_answer(call):
    user_id = call.from_user.id

    if user_id not in user_quiz:
        bot.answer_callback_query(call.id, "Натисни /interview щоб почати 🚀")
        return

    chosen = int(call.data.split("_")[1])
    current = user_quiz[user_id]["current"]
    correct = current["correct_index"]

    # ✅ відповідь користувача
    if chosen == correct:
        user_quiz[user_id]["score"] += 1
        bot.answer_callback_query(call.id, "✅ Правильно!")
    else:
        bot.answer_callback_query(
            call.id,
            f"❌ Помилка\n➡️ Правильно: {current['options'][correct]}"
        )

    # ✅ Видаляємо кнопки після відповіді
    try:
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
    except:
        pass

    user_quiz[user_id]["q"] += 1

    # ✅ Якщо тест завершено
    if user_quiz[user_id]["q"] >= 5:
        score = user_quiz[user_id]["score"]

        save_interview_result(user_id, score, user_quiz[user_id]["questions"])

        bot.send_message(
            user_id,
            f"🏁 Готово!\n"
            f"Твій результат: <b>{score}/5</b> ✅\n\n"
            f"Подивитись історію: /history\n"
            f"Хочеш ще? /interview",
            parse_mode="HTML"
        )

        del user_quiz[user_id]
        return

    send_new_question(user_id)
