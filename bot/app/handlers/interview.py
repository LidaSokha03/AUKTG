from app.bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.services.llm_questions import generate_mcq_question
from app.services.interview_history import save_interview_result, clear_interview_history
import textwrap
import threading
import time
from datetime import datetime

user_quiz = {}
user_timers = {}

MAX_LEN = 28
QUESTION_TIMEOUT = 60

# Налаштування складності
DIFFICULTY_SETTINGS = {
    "easy": {"questions": 5, "time": 90, "emoji": "🟢"},
    "medium": {"questions": 7, "time": 60, "emoji": "🟡"},
    "hard": {"questions": 10, "time": 45, "emoji": "🔴"}
}

# Категорії питань
CATEGORIES = {
    "python": "🐍 Python",
    "javascript": "💛 JavaScript",
    "algorithms": "🧮 Algorithms",
    "databases": "🗄️ Databases",
    "system_design": "🏗️ System Design",
    "mixed": "🎲 Mixed"
}


def format_text(text):
    text = text.strip()
    if len(text) <= MAX_LEN:
        return text
    return "\n".join(textwrap.wrap(text, MAX_LEN))


def cleanup_user_state(user_id):
    """Очищає стейт користувача"""
    if user_id in user_timers:
        try:
            user_timers[user_id].cancel()
        except:
            pass
        del user_timers[user_id]
    
    if user_id in user_quiz:
        del user_quiz[user_id]


@bot.message_handler(commands=["interview"])
def start_mcq(call_or_msg):
    user_id = call_or_msg.from_user.id
    cleanup_user_state(user_id)

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🚀 Quick Start", callback_data="quick_start"),
        InlineKeyboardButton("⚙️ Custom", callback_data="select_difficulty")
    )
    kb.add(InlineKeyboardButton("📊 Statistics", callback_data="show_stats"))

    bot.send_message(
        user_id,
        "🎯 <b>Technical Interview Bot</b>\n\n"
        "Choose your mode:\n"
        "• Quick Start - Medium difficulty, mixed topics\n"
        "• Custom - Choose difficulty and category\n"
        "• Statistics - View your progress",
        reply_markup=kb,
        parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda c: c.data == "quick_start")
def quick_start(call: CallbackQuery):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    
    cleanup_user_state(user_id)
    
    user_quiz[user_id] = {
        "score": 0,
        "q": 0,
        "questions": [],
        "answered": [],
        "processing": False,
        "difficulty": "medium",
        "category": "mixed",
        "start_time": datetime.now(),
        "time_spent": []
    }
    
    try:
        bot.edit_message_text(
            "🚀 Starting Quick Interview!\n\n"
            "Difficulty: Medium 🟡\n"
            "Questions: 7\n"
            "Time per question: 60s\n\n"
            "Get ready...",
            call.message.chat.id,
            call.message.message_id
        )
    except:
        bot.send_message(user_id, "Starting Quick Interview!")
    
    time.sleep(1)
    send_new_question(user_id)


@bot.callback_query_handler(func=lambda c: c.data == "interview")
def interview_callback(call):
    bot.answer_callback_query(call.id)
    start_mcq(call)

@bot.callback_query_handler(func=lambda c: c.data == "select_difficulty")
def select_difficulty(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    
    kb = InlineKeyboardMarkup(row_width=1)
    for diff, settings in DIFFICULTY_SETTINGS.items():
        kb.add(InlineKeyboardButton(
            f"{settings['emoji']} {diff.title()} - {settings['questions']} questions, {settings['time']}s each",
            callback_data=f"diff_{diff}"
        ))
    kb.add(InlineKeyboardButton("⬅️ Back", callback_data="back_to_start"))
    
    bot.edit_message_text(
        "⚙️ <b>Select Difficulty:</b>",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb,
        parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("diff_"))
def handle_difficulty(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    difficulty = call.data.split("_")[1]
    
    kb = InlineKeyboardMarkup(row_width=2)
    for cat_id, cat_name in CATEGORIES.items():
        kb.add(InlineKeyboardButton(cat_name, callback_data=f"cat_{difficulty}_{cat_id}"))
    kb.add(InlineKeyboardButton("⬅️ Back", callback_data="select_difficulty"))
    
    bot.edit_message_text(
        f"📚 <b>Select Category:</b>\n\n"
        f"Difficulty: {DIFFICULTY_SETTINGS[difficulty]['emoji']} {difficulty.title()}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb,
        parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
def start_custom_interview(call: CallbackQuery):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    
    parts = call.data.split("_")
    difficulty = parts[1]
    category = parts[2]
    
    cleanup_user_state(user_id)
    
    settings = DIFFICULTY_SETTINGS[difficulty]
    
    user_quiz[user_id] = {
        "score": 0,
        "q": 0,
        "questions": [],
        "answered": [],
        "processing": False,
        "difficulty": difficulty,
        "category": category,
        "start_time": datetime.now(),
        "time_spent": [],
        "total_questions": settings["questions"],
        "time_per_question": settings["time"]
    }
    
    bot.edit_message_text(
        f"🎯 <b>Custom Interview Starting!</b>\n\n"
        f"{settings['emoji']} Difficulty: {difficulty.title()}\n"
        f"{CATEGORIES[category]} Category: {category.title()}\n"
        f"📝 Questions: {settings['questions']}\n"
        f"⏱ Time: {settings['time']}s per question\n\n"
        f"Good luck! 🍀",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )
    
    time.sleep(2)
    send_new_question(user_id)


@bot.callback_query_handler(func=lambda c: c.data == "back_to_start")
def back_to_start(call: CallbackQuery):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🚀 Quick Start", callback_data="quick_start"),
        InlineKeyboardButton("⚙️ Custom", callback_data="select_difficulty")
    )
    kb.add(InlineKeyboardButton("📊 Statistics", callback_data="show_stats"))
    
    bot.edit_message_text(
        "🎯 <b>Technical Interview Bot</b>\n\n"
        "Choose your mode:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb,
        parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda c: c.data == "show_stats")
def show_stats(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    
    from app.services.interview_history import get_interview_history
    
    user_id = call.from_user.id
    records = get_interview_history(user_id)
    
    if not records:
        bot.edit_message_text(
            "📊 <b>Your Statistics</b>\n\n"
            "No interviews completed yet!\n"
            "Start your first interview to see stats.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        return
    
    total = len(records)
    total_score = sum(r['score'] for r in records)
    total_possible = sum(r.get('total', 5) for r in records)
    avg_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
    
    # Streak calculation
    current_streak = 0
    best_streak = 0
    temp_streak = 0
    
    for r in records:
        percentage = (r['score'] / r.get('total', 5)) * 100
        if percentage >= 60:
            temp_streak += 1
            best_streak = max(best_streak, temp_streak)
        else:
            temp_streak = 0
    
    # Last interview
    last = records[-1]
    last_percentage = (last['score'] / last.get('total', 5)) * 100
    
    if last_percentage >= 60:
        current_streak = temp_streak
    
    # Determine rank
    if avg_percentage >= 90:
        rank = "🏆 Master"
    elif avg_percentage >= 80:
        rank = "💎 Expert"
    elif avg_percentage >= 70:
        rank = "⭐ Advanced"
    elif avg_percentage >= 60:
        rank = "📚 Intermediate"
    else:
        rank = "🌱 Beginner"
    
    text = (
        f"📊 <b>Your Statistics</b>\n\n"
        f"🎖 Rank: {rank}\n\n"
        f"📈 Overall Performance:\n"
        f"• Total Interviews: {total}\n"
        f"• Average Score: {avg_percentage:.1f}%\n"
        f"• Total Questions: {total_possible}\n"
        f"• Correct Answers: {total_score}\n\n"
        f"🔥 Streaks:\n"
        f"• Current: {current_streak}\n"
        f"• Best: {best_streak}\n\n"
        f"📅 Last Interview:\n"
        f"• Score: {last['score']}/{last.get('total', 5)}\n"
        f"• Date: {last['timestamp'].strftime('%d.%m.%Y %H:%M')}"
    )
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📜 Full History", callback_data="view_history"),
        InlineKeyboardButton("🎯 New Interview", callback_data="quick_start")
    )
    kb.add(InlineKeyboardButton("⬅️ Back", callback_data="back_to_start"))
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb,
        parse_mode="HTML"
    )


def update_timer(user_id, msg_id, chat_id, question_text, time_left):
    if user_id not in user_quiz:
        return
    
    current_q = user_quiz[user_id]["q"]
    if current_q in user_quiz[user_id]["answered"]:
        return
    
    if user_quiz[user_id].get("processing", False):
        return
    
    if time_left <= 0:
        timeout_question(user_id)
        return
    
    try:
        kb = InlineKeyboardMarkup(row_width=1)
        for i, opt in enumerate(user_quiz[user_id]["current"]["options"]):
            pretty = format_text(opt)
            kb.add(InlineKeyboardButton(pretty, callback_data=f"answer_{i}_{current_q}"))
        
        # Додаємо кнопку Skip
        kb.add(InlineKeyboardButton("⏭️ Skip Question", callback_data=f"skip_{current_q}"))
        
        # Emoji для таймера
        if time_left <= 10:
            timer_emoji = "🔴"
        elif time_left <= 30:
            timer_emoji = "🟡"
        else:
            timer_emoji = "🟢"
        
        total_q = user_quiz[user_id].get("total_questions", 5)
        
        bot.edit_message_text(
            f"❓ Question {user_quiz[user_id]['q'] + 1}/{total_q}\n\n"
            f"{question_text}\n\n"
            f"{timer_emoji} Time: {time_left}s",
            chat_id,
            msg_id,
            reply_markup=kb
        )
    except:
        pass
    
    timer = threading.Timer(1.0, update_timer, args=[user_id, msg_id, chat_id, question_text, time_left - 1])
    user_timers[user_id] = timer
    timer.start()


def send_new_question(user_id):
    if user_id not in user_quiz:
        return
    
    if user_id in user_timers:
        try:
            user_timers[user_id].cancel()
        except:
            pass
        del user_timers[user_id]

    # Зберігаємо час початку питання
    user_quiz[user_id]["question_start_time"] = datetime.now()

    category = user_quiz[user_id].get("category", "mixed")
    difficulty = user_quiz[user_id].get("difficulty", "medium")
    
    # Тут можна передати category та difficulty в generate_mcq_question
    q = generate_mcq_question()  # TODO: add category and difficulty params

    if not q or "options" not in q or "correct_index" not in q:
        q = {
            "question": "What is OOP?",
            "options": [
                "Programming paradigm",
                "Python language",
                "Operating system",
                "Database type"
            ],
            "correct_index": 0
        }

    user_quiz[user_id]["current"] = q
    user_quiz[user_id]["questions"].append(q)

    kb = InlineKeyboardMarkup(row_width=1)

    for i, opt in enumerate(q["options"]):
        pretty = format_text(opt)
        kb.add(InlineKeyboardButton(pretty, callback_data=f"answer_{i}_{user_quiz[user_id]['q']}"))
    
    kb.add(InlineKeyboardButton("⏭️ Skip Question", callback_data=f"skip_{user_quiz[user_id]['q']}"))

    question_text = format_text(q['question'])
    timeout = user_quiz[user_id].get("time_per_question", QUESTION_TIMEOUT)
    total_q = user_quiz[user_id].get("total_questions", 5)
    
    msg = bot.send_message(
        user_id,
        f"❓ Question {user_quiz[user_id]['q'] + 1}/{total_q}\n\n"
        f"{question_text}\n\n"
        f"🟢 Time: {timeout}s",
        reply_markup=kb
    )

    user_quiz[user_id]["current_msg_id"] = msg.message_id
    
    timer = threading.Timer(1.0, update_timer, args=[user_id, msg.message_id, msg.chat.id, question_text, timeout - 1])
    user_timers[user_id] = timer
    timer.start()


@bot.callback_query_handler(func=lambda c: c.data.startswith("skip_"))
def handle_skip(call: CallbackQuery):
    user_id = call.from_user.id
    
    if user_id not in user_quiz:
        bot.answer_callback_query(call.id, "Press /interview to start")
        return
    
    question_num = int(call.data.split("_")[1])
    if question_num != user_quiz[user_id]["q"]:
        bot.answer_callback_query(call.id, "Old question!")
        return
    
    current_q = user_quiz[user_id]["q"]
    
    if current_q in user_quiz[user_id]["answered"]:
        bot.answer_callback_query(call.id, "Already answered!")
        return
    
    if user_quiz[user_id].get("processing", False):
        bot.answer_callback_query(call.id, "Please wait...")
        return
    
    user_quiz[user_id]["processing"] = True
    user_quiz[user_id]["answered"].append(current_q)
    
    if user_id in user_timers:
        try:
            user_timers[user_id].cancel()
        except:
            pass
        del user_timers[user_id]
    
    bot.answer_callback_query(call.id, "⏭️ Skipped")
    
    current = user_quiz[user_id]["current"]
    
    try:
        bot.edit_message_text(
            f"⏭️ Skipped\n\n{format_text(current['question'])}\n\n"
            f"Correct answer was: {current['options'][current['correct_index']]}",
            call.message.chat.id,
            call.message.message_id
        )
    except:
        pass
    
    user_quiz[user_id]["q"] += 1
    total_q = user_quiz[user_id].get("total_questions", 5)
    
    if user_quiz[user_id]["q"] >= total_q:
        finish_interview(user_id)
    else:
        time.sleep(1)
        user_quiz[user_id]["processing"] = False
        send_new_question(user_id)


def timeout_question(user_id):
    if user_id not in user_quiz:
        return

    current_q = user_quiz[user_id]["q"]
    
    if current_q in user_quiz[user_id]["answered"]:
        return

    if user_quiz[user_id].get("processing", False):
        return
    
    user_quiz[user_id]["processing"] = True

    try:
        bot.edit_message_text(
            "⏰ Time's up! Moving to next question...",
            user_id,
            user_quiz[user_id]["current_msg_id"]
        )
    except:
        pass

    user_quiz[user_id]["answered"].append(current_q)
    user_quiz[user_id]["q"] += 1
    
    total_q = user_quiz[user_id].get("total_questions", 5)

    if user_quiz[user_id]["q"] >= total_q:
        finish_interview(user_id)
    else:
        user_quiz[user_id]["processing"] = False
        send_new_question(user_id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("answer_"))
def handle_answer(call: CallbackQuery):
    user_id = call.from_user.id

    if user_id not in user_quiz:
        bot.answer_callback_query(call.id, "Press /interview to start")
        return

    parts = call.data.split("_")
    chosen = int(parts[1])
    
    if len(parts) > 2:
        question_num = int(parts[2])
        if question_num != user_quiz[user_id]["q"]:
            bot.answer_callback_query(call.id, "Old question!")
            return
    
    current_q = user_quiz[user_id]["q"]
    
    if current_q in user_quiz[user_id]["answered"]:
        bot.answer_callback_query(call.id, "Already answered!")
        return
    
    if user_quiz[user_id].get("processing", False):
        bot.answer_callback_query(call.id, "Please wait...")
        return
    
    user_quiz[user_id]["processing"] = True
    user_quiz[user_id]["answered"].append(current_q)
    
    # Рахуємо час відповіді
    question_start = user_quiz[user_id].get("question_start_time")
    if question_start:
        time_spent = (datetime.now() - question_start).total_seconds()
        user_quiz[user_id]["time_spent"].append(time_spent)

    if user_id in user_timers:
        try:
            user_timers[user_id].cancel()
        except:
            pass
        del user_timers[user_id]

    current = user_quiz[user_id]["current"]
    correct = current["correct_index"]

    if chosen == correct:
        user_quiz[user_id]["score"] += 1
        result_text = "✅ Correct!"
        bot.answer_callback_query(call.id, "✅ Correct!")
    else:
        result_text = f"❌ Wrong! Correct: {current['options'][correct]}"
        bot.answer_callback_query(call.id, "❌ Wrong!")

    try:
        bot.edit_message_text(
            f"{result_text}\n\n{format_text(current['question'])}",
            call.message.chat.id,
            call.message.message_id
        )
    except:
        pass

    user_quiz[user_id]["q"] += 1
    total_q = user_quiz[user_id].get("total_questions", 5)

    if user_quiz[user_id]["q"] >= total_q:
        finish_interview(user_id)
    else:
        time.sleep(1)
        user_quiz[user_id]["processing"] = False
        send_new_question(user_id)


def finish_interview(user_id):
    score = user_quiz[user_id]["score"]
    questions = user_quiz[user_id]["questions"]
    total_q = user_quiz[user_id].get("total_questions", 5)
    difficulty = user_quiz[user_id].get("difficulty", "medium")
    category = user_quiz[user_id].get("category", "mixed")
    
    # Рахуємо загальний час
    start_time = user_quiz[user_id].get("start_time")
    total_time = (datetime.now() - start_time).total_seconds() if start_time else 0
    
    # Середній час на питання
    time_spent = user_quiz[user_id].get("time_spent", [])
    avg_time = sum(time_spent) / len(time_spent) if time_spent else 0

    save_interview_result(user_id, score, total_q, questions)

    percentage = (score / total_q) * 100
    
    if percentage >= 80:
        grade = "Excellent! 🌟"
        emoji = "🎉"
    elif percentage >= 60:
        grade = "Good! 👍"
        emoji = "✨"
    elif percentage >= 40:
        grade = "Fair 📚"
        emoji = "💪"
    else:
        grade = "Need more practice 💪"
        emoji = "📖"

    report = (
        f"{emoji} <b>Interview Complete!</b>\n\n"
        f"📊 <b>Results:</b>\n"
        f"Score: <b>{score}/{total_q}</b> ({percentage:.0f}%)\n"
        f"Grade: {grade}\n\n"
        f"⚙️ <b>Settings:</b>\n"
        f"{DIFFICULTY_SETTINGS[difficulty]['emoji']} Difficulty: {difficulty.title()}\n"
        f"{CATEGORIES.get(category, '🎲')} Category: {category.title()}\n\n"
        f"⏱ <b>Time Stats:</b>\n"
        f"Total time: {int(total_time // 60)}m {int(total_time % 60)}s\n"
        f"Avg per question: {int(avg_time)}s\n\n"
        f"✅ Correct: {score}\n"
        f"❌ Wrong: {total_q - score}\n"
    )

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 View Stats", callback_data="show_stats"),
        InlineKeyboardButton("🎯 New Interview", callback_data="quick_start")
    )
    kb.add(
        InlineKeyboardButton("📜 History", callback_data="view_history"),
        InlineKeyboardButton("⚙️ Custom", callback_data="select_difficulty")
    )

    bot.send_message(user_id, report, parse_mode="HTML", reply_markup=kb)

    cleanup_user_state(user_id)


@bot.callback_query_handler(func=lambda c: c.data == "view_history")
def callback_view_history(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    
    from app.services.interview_history import get_interview_history
    
    user_id = call.from_user.id
    records = get_interview_history(user_id)

    if not records:
        bot.send_message(user_id, "You haven't taken any interviews yet.")
        return

    total_interviews = len(records)
    
    valid_records = []
    for r in records:
        total = r.get('total', 5)
        if isinstance(total, list):
            total = len(total)
        r['total'] = total
        valid_records.append(r)
    
    # Рахуємо середній бал правильно
    total_score = sum(r['score'] for r in valid_records)
    total_possible = sum(r['total'] for r in valid_records)
    avg_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0

    text = f"📜 <b>Interview History</b>\n\n"
    text += f"Total: {total_interviews} interview(s)\n"
    text += f"Average: {avg_percentage:.1f}%\n\n"

    # Показуємо останні 5 інтерв'ю
    recent_records = valid_records[-5:]
    
    kb = InlineKeyboardMarkup(row_width=1)
    
    for idx, r in enumerate(recent_records):
        # Правильна нумерація: якщо всього 10 інтерв'ю, а показуємо останні 5, то це 6, 7, 8, 9, 10
        interview_number = total_interviews - len(recent_records) + idx + 1
        
        percentage = (r['score'] / r['total']) * 100
        
        if percentage >= 80:
            result_emoji = "🌟"
        elif percentage >= 60:
            result_emoji = "✨"
        else:
            result_emoji = "📚"
        
        text += f"{result_emoji} <b>Interview #{interview_number}</b>\n"
        text += f"Score: {r['score']}/{r['total']} ({percentage:.0f}%) | {r['timestamp'].strftime('%d.%m %H:%M')}\n"
        
        # Додаємо кнопку для детального перегляду
        kb.add(InlineKeyboardButton(
            f"📖 View Interview #{interview_number} Details",
            callback_data=f"view_interview_{interview_number - 1}"  # Індекс в масиві
        ))
        
        text += "\n"

    kb.add(
        InlineKeyboardButton("🎯 New Interview", callback_data="quick_start"),
        InlineKeyboardButton("🗑️ Clear History", callback_data="clear_history")
    )
    kb.add(InlineKeyboardButton("⬅️ Back", callback_data="show_stats"))

    bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("view_interview_"))
def view_interview_details(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    
    from app.services.interview_history import get_interview_history
    
    user_id = call.from_user.id
    interview_idx = int(call.data.split("_")[2])
    
    records = get_interview_history(user_id)
    
    if not records or interview_idx >= len(records):
        bot.send_message(user_id, "❌ Interview not found!")
        return
    
    r = records[interview_idx]
    total = r.get('total', 5)
    if isinstance(total, list):
        total = len(total)
    
    percentage = (r['score'] / total) * 100
    interview_number = interview_idx + 1
    
    if percentage >= 80:
        result_emoji = "🌟"
        grade = "Excellent!"
    elif percentage >= 60:
        result_emoji = "✨"
        grade = "Good!"
    else:
        result_emoji = "📚"
        grade = "Keep practicing!"
    
    text = (
        f"{result_emoji} <b>Interview #{interview_number} Details</b>\n\n"
        f"📊 Score: <b>{r['score']}/{total}</b> ({percentage:.0f}%)\n"
        f"🎯 Grade: {grade}\n"
        f"📅 Date: {r['timestamp'].strftime('%d.%m.%Y %H:%M')}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    # Додаємо всі питання
    questions = r.get('questions', [])
    
    if questions:
        text += f"<b>Questions & Answers:</b>\n\n"
        
        for i, q in enumerate(questions, 1):
            if isinstance(q, dict):
                question_text = q.get('question', 'N/A')
                options = q.get('options', [])
                correct_idx = q.get('correct_index', 0)
                
                text += f"<b>{i}. {question_text}</b>\n"
                
                # Показуємо всі варіанти з позначкою правильної відповіді
                for idx, opt in enumerate(options):
                    if idx == correct_idx:
                        text += f"   ✅ {opt}\n"
                    else:
                        text += f"   • {opt}\n"
                
                text += "\n"
    else:
        text += "<i>No questions data available</i>\n"
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📜 Back to History", callback_data="view_history"),
        InlineKeyboardButton("🎯 New Interview", callback_data="quick_start")
    )
    
    # Розбиваємо на частини, якщо текст занадто довгий
    if len(text) > 4000:
        # Відправляємо першу частину
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts[:-1]:
            bot.send_message(call.message.chat.id, part, parse_mode="HTML")
        # Останню частину з кнопками
        bot.send_message(call.message.chat.id, parts[-1], parse_mode="HTML", reply_markup=kb)
    else:
        bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data == "clear_history")
def callback_clear_history(call: CallbackQuery):
    user_id = call.from_user.id
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Yes, clear", callback_data="confirm_clear_history"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_clear_history")
    )
    
    bot.answer_callback_query(call.id)
    bot.send_message(
        user_id,
        "⚠️ Are you sure you want to clear all interview history?\n\nThis action cannot be undone!",
        reply_markup=kb
    )


@bot.callback_query_handler(func=lambda c: c.data == "confirm_clear_history")
def callback_confirm_clear(call: CallbackQuery):
    user_id = call.from_user.id
    
    try:
        deleted_count = clear_interview_history(user_id)
        bot.answer_callback_query(call.id, "History cleared!")
        bot.edit_message_text(
            f"✅ History cleared successfully!\nDeleted {deleted_count} record(s).",
            call.message.chat.id,
            call.message.message_id
        )
    except Exception as e:
        bot.answer_callback_query(call.id, "Error!")
        bot.send_message(user_id, f"❌ Error clearing history: {str(e)}")


@bot.callback_query_handler(func=lambda c: c.data == "cancel_clear_history")
def callback_cancel_clear(call: CallbackQuery):
    bot.answer_callback_query(call.id, "Cancelled")
    bot.edit_message_text(
        "❌ Clear history cancelled.",
        call.message.chat.id,
        call.message.message_id
    )