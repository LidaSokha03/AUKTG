from app.services.docx_export import cv_to_docx
from app.bot_instance import bot
from app.db.models.cv import CV
from pathlib import Path


@bot.message_handler(commands=['export_docx'])
def export_docx(message):
    chat_id = message.chat.id

    cv_data = CV(
        user_id=str(chat_id),
        firstname="Lida",
        lastname="Sokha",
        email="lidasosokha@gmail.com",
        phone="+380964692379",
        experience=(
            "Marketing Intern: SoftServe (June 2023 - September 2023)\n \
- Assisted with digital marketing campaigns focusing on social media and content analytics.\n\
- Created 15+ social posts that increased engagement by 25%.\n\
- Helped prepare performance reports and worked with the creative team on visual identity.\n\n\
Project Assistant: UCU Career Center (February 2022 - May 2023)\n\
- Coordinated internal communication between student bodies and employer partners.\n\
- Contributed to organizing the university job fair with over 40 companies.\n\
- Provided administrative support and event logistics management."
        ),
        education=(
            "Ukrainian Catholic University: Lviv, Ukraine\n\
Bachelor's Degree in Business Analytics (2021 - 2025)\n\
- Coursework: Data Visualization, Machine Learning, Project Management, Marketing Analytics.\n\
- GPA: 3.8 / 4.0"
        ),
        courses=(
            "Google Data Analytics Professional Certificate - Coursera (2023)\n\
- Hands-on training in SQL, Tableau, and data cleaning techniques.\n\n\
Soft Skills Training - EPAM University (2022)\n\
- Focused on teamwork, personal productivity, and structured problem-solving.\n\n\
LinkedIn Learning - Data Visualization with Python and Pandas (2023)"
        ),
        skills=(
            "Python, SQL, Excel, Tableau, Data Analysis, Communication, Project Coordination, \
Public Speaking, Critical Thinking, Teamwork"
        )
    )

    docx_path = cv_to_docx(cv_data)

    with open(docx_path, "rb") as file:
        bot.send_document(chat_id, file, caption="Your DOCX CV is ready!")

    exports_dir = Path("exports")
    for f in exports_dir.glob("*.docx"):
        if f != docx_path and f.stat().st_mtime < docx_path.stat().st_mtime - 300:
            try:
                f.unlink()
            except Exception:
                pass
