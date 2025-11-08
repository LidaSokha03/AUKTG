from fpdf import FPDF
from pathlib import Path
from app.db.models.cv import CV
import datetime

def cv_to_pdf(cv_obj: CV, out_path:Path = Path('exports')) -> Path:
    out_path.mkdir(exist_ok=True)
    file_path = out_path / f"cv_{cv_obj.user_id}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Times", "B", 18)
    pdf.cell(0, 10, f"{cv_obj.firstname} {cv_obj.lastname}", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Personal Information:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 8,
        f"Email: {cv_obj.email}\n"
        f"Phone: {cv_obj.phone}\n"
    )
    pdf.ln(4)

    # Освіта та досвід
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Education & Experience:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 8,
        f"Education: {cv_obj.education}\n"
        f"Experience: {cv_obj.experience} years\n"
    )
    pdf.ln(4)

    # Скіли
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Skills:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 8, cv_obj.skills, ln=True)
    pdf.ln(4)

    # Мови
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Languages:", ln=True)
    pdf.set_font("Times", "", 12)
    # for lang_curr in cv_obj.languages:
    #     lang, level = lang_curr.split(', ')
    pdf.multi_cell(0, 8, cv_obj.languages, ln=True)
    pdf.ln(4)

    # Проєкти
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Projects:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 8, cv_obj.projects, ln=True)
    pdf.ln(10)

    # Нижній колонтитул часу
    pdf.set_font("Times", "I", 10)
    made_time = datetime.datetime.now()

    pdf.output(str(file_path))
    return file_path, made_time

# our_curr = CV("auto_generated", "Lida", "Sokha", "lidasosokha@gmail.com", "380964692379", "Bachelor's Degree in BA, UCU", "8", "['skill1', 'skill2']", "['language1, level', 'language2, level']", "text")
# print(cv_to_pdf(our_curr))