from docx import Document
from pathlib import Path
from app.db.models.cv import CV
from app.services.docx_templates import cv_to_docx_template


def cv_to_docx(cv_obj: CV, out_path: Path = Path("exports"), template: str = 'classic') -> Path:
    """
    Генерує CV у форматі DOCX (Microsoft Word) з підтримкою темплейтів
    
    Args:
        cv_obj: CV object
        out_path: Output directory
        template: Template name ('classic', 'modern', 'professional')
    """
    return cv_to_docx_template(cv_obj, template, out_path)