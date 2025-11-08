from app.bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.db.database import db
from app.services.pdf_export import cv_to_pdf
from app.services.docx_export import cv_to_docx
from app.services.llm_cv import improve_cv_with_llm
from app.db.models.cv import CV
import os


def _send_no_cv(chat_id):
    bot.send_message(chat_id, "You don't have CV yet 💾")


def _safe_str(value, default=''):
    """Safely convert value to string"""
    if value is None:
        return default
    if isinstance(value, dict):
        return str(value)
    return str(value)


def send_cv_history(tg_id: int, chat_id: int):
    query = {"tg_id": str(tg_id)}
    profile_doc = db.profiles.find_one(query)
    
    if profile_doc is None:
        _send_no_cv(chat_id)
        return
    
    history = profile_doc.get("cv_history") or []
    if not history:
        cv_doc = profile_doc.get("cv")
        if not cv_doc:
            _send_no_cv(chat_id)
            return
        history = [cv_doc]
    
    lines = ["📚 CV history:\n"]
    markup = InlineKeyboardMarkup(row_width=1)
    
    for i, cv in enumerate(history):
        version = cv.get("version", "?")
        firstname = cv.get("firstname", "")
        lastname = cv.get("lastname", "")
        email = cv.get("email", "")
        
        lines.append(f"• Version {version}: {firstname} {lastname} ({email})")
        
        btn = InlineKeyboardButton(
            text=f"📄 Version {version}",
            callback_data=f"cv_view:{i}"
        )
        markup.add(btn)
    
    text = "\n".join(lines)
    bot.send_message(chat_id, text, reply_markup=markup)


def send_cv_details(tg_id: int, chat_id: int, cv_index: int, message_id: int = None):
    query = {"tg_id": str(tg_id)}
    profile_doc = db.profiles.find_one(query)
    
    if profile_doc is None:
        _send_no_cv(chat_id)
        return
    
    history = profile_doc.get("cv_history") or []
    if not history:
        cv_doc = profile_doc.get("cv")
        if not cv_doc:
            _send_no_cv(chat_id)
            return
        history = [cv_doc]
    
    if cv_index >= len(history):
        bot.send_message(chat_id, "❌ CV version not found")
        return
    
    cv = history[cv_index]
    version = cv.get("version", "?")
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    btn_view = InlineKeyboardButton(
        text="👁 View Markdown",
        callback_data=f"cv_markdown:{cv_index}"
    )
    btn_export = InlineKeyboardButton(
        text="📥 Export",
        callback_data=f"cv_export_menu:{cv_index}"
    )
    btn_improve = InlineKeyboardButton(
        text="✨ Improve with AI",
        callback_data=f"cv_improve:{cv_index}"
    )
    btn_back = InlineKeyboardButton(
        text="⬅️ Back to history",
        callback_data="cv_history"
    )
    
    markup.add(btn_view, btn_export)
    markup.add(btn_improve)
    markup.add(btn_back)
    
    text = f"📄 CV Version {version}\n\nChoose an action:"
    
    if message_id:
        try:
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup
            )
        except:
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)


def send_cv_markdown(tg_id: int, chat_id: int, cv_index: int):
    query = {"tg_id": str(tg_id)}
    profile_doc = db.profiles.find_one(query)
    
    if profile_doc is None:
        _send_no_cv(chat_id)
        return
    
    history = profile_doc.get("cv_history") or []
    if not history:
        cv_doc = profile_doc.get("cv")
        if not cv_doc:
            _send_no_cv(chat_id)
            return
        history = [cv_doc]
    
    if cv_index >= len(history):
        bot.send_message(chat_id, "❌ CV version not found")
        return
    
    cv = history[cv_index]
    
    # Формуємо markdown текст CV
    markdown_lines = []
    markdown_lines.append(f"*{cv.get('firstname', '')} {cv.get('lastname', '')}*")
    markdown_lines.append(f"📧 {cv.get('email', '')}")
    
    if cv.get('phone'):
        markdown_lines.append(f"📱 {cv.get('phone', '')}")
    
    markdown_lines.append("")
    
    if cv.get('experience'):
        markdown_lines.append("*Experience*")
        markdown_lines.append(cv.get('experience', ''))
        markdown_lines.append("")
    
    if cv.get('education'):
        markdown_lines.append("*Education*")
        markdown_lines.append(cv.get('education', ''))
        markdown_lines.append("")
    
    if cv.get('courses'):
        markdown_lines.append("*Courses and Languages*")
        markdown_lines.append(cv.get('courses', ''))
        markdown_lines.append("")
    
    if cv.get('skills'):
        markdown_lines.append("*Skills*")
        markdown_lines.append(cv.get('skills', ''))
        markdown_lines.append("")
    
    markdown_text = "\n".join(markdown_lines)
    
    markup = InlineKeyboardMarkup()
    btn_back = InlineKeyboardButton(
        text="⬅️ Back",
        callback_data=f"cv_view:{cv_index}"
    )
    markup.add(btn_back)
    
    bot.send_message(chat_id, markdown_text, parse_mode="Markdown", reply_markup=markup)


def send_export_menu(chat_id: int, cv_index: int, message_id: int = None):
    markup = InlineKeyboardMarkup(row_width=1)
    
    btn_pdf = InlineKeyboardButton(
        text="📄 Export PDF",
        callback_data=f"cv_template_select:pdf:{cv_index}"
    )
    btn_docx = InlineKeyboardButton(
        text="📝 Export DOCX",
        callback_data=f"cv_template_select:docx:{cv_index}"
    )
    btn_back = InlineKeyboardButton(
        text="⬅️ Back",
        callback_data=f"cv_view:{cv_index}"
    )
    
    markup.add(btn_pdf, btn_docx)
    markup.add(btn_back)
    
    text = "Choose export format:"
    
    if message_id:
        try:
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup
            )
        except:
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)


def send_template_select(chat_id: int, format_type: str, cv_index: int, message_id: int = None):
    """Menu for selecting template (PDF or DOCX)"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    templates = [
        ("📋 Classic", "classic"),
        ("🎨 Modern", "modern"),
        ("💼 Professional", "professional")
    ]
    
    for name, template in templates:
        btn = InlineKeyboardButton(
            text=name,
            callback_data=f"cv_export_{format_type}:{cv_index}:{template}"
        )
        markup.add(btn)
    
    btn_back = InlineKeyboardButton(
        text="⬅️ Back",
        callback_data=f"cv_export_menu:{cv_index}"
    )
    markup.add(btn_back)
    
    format_name = "PDF" if format_type == "pdf" else "DOCX"
    text = f"Choose {format_name} template:"
    
    if message_id:
        try:
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup
            )
        except:
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)


def improve_cv_with_ai(tg_id: int, chat_id: int, cv_index: int):
    """Improve CV using LLM"""
    query = {"tg_id": str(tg_id)}
    profile_doc = db.profiles.find_one(query)
    
    if profile_doc is None:
        _send_no_cv(chat_id)
        return
    
    history = profile_doc.get("cv_history") or []
    if not history:
        cv_doc = profile_doc.get("cv")
        if not cv_doc:
            _send_no_cv(chat_id)
            return
        history = [cv_doc]
    
    if cv_index >= len(history):
        bot.send_message(chat_id, "❌ CV version not found")
        return
    
    cv_dict = history[cv_index]
    
    bot.send_message(chat_id, "✨ Improving your CV with AI... Please wait...")
    
    try:
        improved_cv = improve_cv_with_llm(cv_dict)
        
        # Add version number
        improved_cv['version'] = len(history) + 1
        
        # Save to history
        history.append(improved_cv)
        db.profiles.update_one(
            {"tg_id": str(tg_id)},
            {"$set": {"cv_history": history, "cv": improved_cv}}
        )
        
        bot.send_message(
            chat_id,
            f"✅ CV improved! Created as Version {improved_cv['version']}\n\n"
            "You can now view or export the improved version."
        )
        
        # Show the new CV
        send_cv_details(tg_id, chat_id, len(history) - 1)
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error improving CV: {str(e)}")


def export_cv(tg_id: int, chat_id: int, cv_index: int, format_type: str, template: str = 'classic'):
    query = {"tg_id": str(tg_id)}
    profile_doc = db.profiles.find_one(query)
    
    if profile_doc is None:
        _send_no_cv(chat_id)
        return
    
    history = profile_doc.get("cv_history") or []
    if not history:
        cv_doc = profile_doc.get("cv")
        if not cv_doc:
            _send_no_cv(chat_id)
            return
        history = [cv_doc]
    
    if cv_index >= len(history):
        bot.send_message(chat_id, "❌ CV version not found")
        return
    
    cv_dict = history[cv_index]
    
    try:
        bot.send_message(chat_id, "⏳ Generating your CV...")
        
        # CRITICAL FIX: Safely convert dict values to strings
        cv_obj = CV(
            user_id=str(tg_id),
            firstname=_safe_str(cv_dict.get('firstname'), ''),
            lastname=_safe_str(cv_dict.get('lastname'), ''),
            email=_safe_str(cv_dict.get('email'), ''),
            phone=_safe_str(cv_dict.get('phone'), ''),
            experience=_safe_str(cv_dict.get('experience'), ''),
            education=_safe_str(cv_dict.get('education'), ''),
            courses=_safe_str(cv_dict.get('courses'), ''),
            skills=_safe_str(cv_dict.get('skills'), ''),
            version=cv_dict.get('version', 1)
        )
        
        if format_type == "pdf":
            filepath = cv_to_pdf(cv_obj, template=template)
            caption = f"📄 Your CV in PDF format ({template.title()} template)"
        elif format_type == "docx":
            filepath = cv_to_docx(cv_obj, template=template)
            caption = f"📝 Your CV in DOCX format ({template.title()} template)"
        else:
            bot.send_message(chat_id, "❌ Unknown format type")
            return
        
        with open(filepath, 'rb') as doc:
            bot.send_document(chat_id, doc, caption=caption)
        
        # Видаляємо файл після відправки
        if os.path.exists(filepath):
            os.remove(filepath)
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error generating CV: {str(e)}")
        import traceback
        print(traceback.format_exc())  # For debugging


# ==================== HANDLERS ====================

@bot.message_handler(commands=["cv_history"])
def cv_history_command(message):
    send_cv_history(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "cv_history")
def cv_history_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    send_cv_history(call.from_user.id, call.message.chat.id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cv_view:"))
def cv_view_callback(call):
    cv_index = int(call.data.split(":")[1])
    send_cv_details(
        call.from_user.id, 
        call.message.chat.id, 
        cv_index,
        call.message.message_id
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cv_markdown:"))
def cv_markdown_callback(call):
    cv_index = int(call.data.split(":")[1])
    send_cv_markdown(call.from_user.id, call.message.chat.id, cv_index)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cv_export_menu:"))
def cv_export_menu_callback(call):
    cv_index = int(call.data.split(":")[1])
    send_export_menu(call.message.chat.id, cv_index, call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cv_template_select:"))
def cv_template_select_callback(call):
    parts = call.data.split(":")
    format_type = parts[1]
    cv_index = int(parts[2])
    send_template_select(call.message.chat.id, format_type, cv_index, call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cv_export_pdf:"))
def cv_export_pdf_callback(call):
    parts = call.data.split(":")
    cv_index = int(parts[1])
    template = parts[2] if len(parts) > 2 else 'classic'
    
    bot.answer_callback_query(call.id, f"Generating PDF ({template})...")
    export_cv(call.from_user.id, call.message.chat.id, cv_index, "pdf", template)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cv_export_docx:"))
def cv_export_docx_callback(call):
    parts = call.data.split(":")
    cv_index = int(parts[1])
    template = parts[2] if len(parts) > 2 else 'classic'
    
    bot.answer_callback_query(call.id, f"Generating DOCX ({template})...")
    export_cv(call.from_user.id, call.message.chat.id, cv_index, "docx", template)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cv_improve:"))
def cv_improve_callback(call):
    cv_index = int(call.data.split(":")[1])
    bot.answer_callback_query(call.id, "Improving CV with AI...")
    improve_cv_with_ai(call.from_user.id, call.message.chat.id, cv_index)