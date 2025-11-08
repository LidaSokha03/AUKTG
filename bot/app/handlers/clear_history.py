from app.bot_instance import bot
from app.services.interview_history import clear_interview_history

@bot.message_handler(commands=["clear_history"])
def clear_history(msg):
    user_id = msg.from_user.id
    
    try:
        deleted_count = clear_interview_history(user_id)
        bot.send_message(
            user_id, 
            f"History cleared successfully!\nDeleted {deleted_count} record(s)."
        )
    except Exception as e:
        bot.send_message(user_id, f"Error clearing history: {str(e)}")