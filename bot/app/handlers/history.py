from app.bot_instance import bot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.services.interview_history import get_interview_history

@bot.message_handler(commands=["history"])
def history(msg):
    user_id = msg.from_user.id
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
    
    avg_score = sum(r['score'] for r in valid_records) / total_interviews if total_interviews > 0 else 0

    text = f"<b>Interview History</b>\n\n"
    text += f"Total: {total_interviews} interview(s)\n"
    text += f"Average: {avg_score:.1f}/5\n\n"

    for idx, r in enumerate(valid_records[-3:], 1):
        text += f"<b>Interview #{len(valid_records) - 3 + idx}</b>\n"
        text += f"Score: {r['score']}/{r['total']} | {r['timestamp'].strftime('%d.%m %H:%M')}\n\n"
        
        questions = r.get('questions', [])
        for i, q in enumerate(questions, 1):
            if isinstance(q, dict) and 'question' in q:
                question_text = q['question']
                if len(question_text) > 60:
                    question_text = question_text[:60] + "..."
                text += f"{i}. {question_text}\n"
        
        text += "\n"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("New Interview", callback_data="start_interview_again"))

    bot.send_message(msg.chat.id, text, parse_mode="HTML", reply_markup=kb)