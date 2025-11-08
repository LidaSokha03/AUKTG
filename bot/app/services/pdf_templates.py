from fpdf import FPDF
from pathlib import Path
from app.db.models.cv import CV


class PDFTemplate:
    """Base class for PDF templates"""
    
    def __init__(self, cv_obj: CV):
        self.cv = cv_obj
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)
    
    def generate(self, output_path: Path) -> Path:
        raise NotImplementedError


class ClassicTemplate(PDFTemplate):
    """Classic CV template - your current one"""
    
    def generate(self, output_path: Path) -> Path:
        pdf = self.pdf
        
        # Header
        pdf.set_font("Times", "B", 18)
        pdf.cell(0, 10, f"{self.cv.firstname} {self.cv.lastname}", ln=True, align="C")
        
        pdf.set_font("Times", "", 12)
        pdf.cell(0, 8, f"Email: {self.cv.email}", ln=True, align="C")
        pdf.cell(0, 8, f"Phone: {self.cv.phone}", ln=True, align="C")
        pdf.ln(8)
        
        # Experience
        pdf.set_font("Times", "B", 14)
        pdf.cell(0, 10, "Experience:", ln=True)
        pdf.set_font("Times", "", 12)
        pdf.multi_cell(0, 8, self.cv.experience)
        pdf.ln(4)
        
        # Education
        pdf.set_font("Times", "B", 14)
        pdf.cell(0, 10, "Education:", ln=True)
        pdf.set_font("Times", "", 12)
        pdf.multi_cell(0, 8, self.cv.education)
        pdf.ln(4)
        
        # Courses
        pdf.set_font("Times", "B", 14)
        pdf.cell(0, 10, "Courses and Languages:", ln=True)
        pdf.set_font("Times", "", 12)
        pdf.multi_cell(0, 8, self.cv.courses)
        pdf.ln(4)
        
        # Skills
        pdf.set_font("Times", "B", 14)
        pdf.cell(0, 10, "Skills:", ln=True)
        pdf.set_font("Times", "", 12)
        pdf.multi_cell(0, 8, self.cv.skills)
        
        pdf.output(str(output_path))
        return output_path


class ModernTemplate(PDFTemplate):
    """Modern minimalist template"""
    
    def generate(self, output_path: Path) -> Path:
        pdf = self.pdf
        
        # Header with background
        pdf.set_fill_color(41, 128, 185)  # Blue background
        pdf.set_text_color(255, 255, 255)  # White text
        pdf.set_font("Helvetica", "B", 22)
        pdf.cell(0, 20, f"{self.cv.firstname} {self.cv.lastname}", ln=True, align="C", fill=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"{self.cv.email} | {self.cv.phone}", ln=True, align="C")
        pdf.ln(10)
        
        # Sections
        sections = [
            ("EXPERIENCE", self.cv.experience),
            ("EDUCATION", self.cv.education),
            ("COURSES & LANGUAGES", self.cv.courses),
            ("SKILLS", self.cv.skills)
        ]
        
        for title, content in sections:
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(41, 128, 185)
            pdf.cell(0, 10, title, ln=True)
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, content)
            pdf.ln(5)
        
        pdf.output(str(output_path))
        return output_path


class ProfessionalTemplate(PDFTemplate):
    """Professional two-column template"""
    
    def generate(self, output_path: Path) -> Path:
        pdf = self.pdf
        
        # Header
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 12, f"{self.cv.firstname} {self.cv.lastname}", ln=True)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, f"{self.cv.email} | {self.cv.phone}", ln=True)
        
        # Line separator
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
        pdf.ln(8)
        
        # Reset color
        pdf.set_text_color(0, 0, 0)
        
        # Experience
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Professional Experience", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, self.cv.experience)
        pdf.ln(5)
        
        # Education
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Education", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, self.cv.education)
        pdf.ln(5)
        
        # Skills
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Skills & Languages", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, self.cv.skills)
        pdf.ln(5)
        
        # Courses
        if self.cv.courses:
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 8, "Courses & Certifications", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, self.cv.courses)
        
        pdf.output(str(output_path))
        return output_path


# Template registry
TEMPLATES = {
    'classic': ClassicTemplate,
    'modern': ModernTemplate,
    'professional': ProfessionalTemplate
}


def cv_to_pdf_template(cv_obj: CV, template: str = 'classic', out_path: Path = Path('exports')) -> Path:
    """Generate CV PDF with selected template"""
    out_path.mkdir(exist_ok=True)
    file_path = out_path / f"cv_{cv_obj.user_id}_{template}.pdf"
    
    template_class = TEMPLATES.get(template, ClassicTemplate)
    template_instance = template_class(cv_obj)
    
    return template_instance.generate(file_path)