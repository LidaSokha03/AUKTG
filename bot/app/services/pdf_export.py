from fpdf import FPDF
from pathlib import Path
from app.db.models.cv import CV

def cv_to_pdf(cv_obj: CV, out_path:Path = Path('exports')) -> Path:
    out_path.mkdir(exist_ok=True)
    file_path = out_path / f"cv_{cv_obj.user_id}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Times", "B", 18)
    pdf.cell(0, 10, f"{cv_obj.firstname} {cv_obj.lastname}", ln=True, align="C")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 8, f"Email: {cv_obj.email}", ln=True, align="C")
    pdf.cell(0, 8, f"Phone: {cv_obj.phone}", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Experience:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 8, cv_obj.experience, ln = True)
    pdf.ln(4)

    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Education:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 8, cv_obj.education, ln = True)
    pdf.ln(4)

    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Courses and Languages:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 8, cv_obj.courses, ln=True)
    pdf.ln(4)

    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Skills:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 8, cv_obj.skills, ln=True)
    pdf.ln(4)

    pdf.output(str(file_path))
    return file_path
