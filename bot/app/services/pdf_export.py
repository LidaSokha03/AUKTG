from fpdf import FPDF
from pathlib import Path
from app.db.models.cv import CV
from app.services.pdf_templates import cv_to_pdf_template


def cv_to_pdf(cv_obj: CV, out_path: Path = Path('exports'), template: str = 'classic') -> Path:
    """
    Generate CV PDF with template support
    
    Args:
        cv_obj: CV object
        out_path: Output directory
        template: Template name ('classic', 'modern', 'professional')
    """
    return cv_to_pdf_template(cv_obj, template, out_path)