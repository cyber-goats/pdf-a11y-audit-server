import os
import uuid
from datetime import datetime
from celery import Celery
from app.services import pdf_analyzer

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
celery_app = Celery(
    'tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
)
celery_app.conf.update(
    task_track_started=True,
)

PDF_STORAGE_PATH = "/tmp/pdfs"

def calculate_accessibility_score(analysis: dict, is_pdf_ua_compliant: bool) -> dict:
    score = 0
    max_score = 100
    details = []
    if analysis.get("is_tagged"):
        score += 20
        details.append({"criterion": "Dokument otagowany", "points": 20, "max": 20})
    else:
        details.append({"criterion": "Dokument otagowany", "points": 0, "max": 20})
    if analysis.get("contains_text"):
        score += 20
        details.append({"criterion": "Zawiera tekst", "points": 20, "max": 20})
    else:
        details.append({"criterion": "Zawiera tekst", "points": 0, "max": 20})
    image_info = analysis.get("image_info", {})
    if image_info.get("image_count", 0) > 0:
        alt_ratio = image_info.get("images_with_alt", 0) / image_info.get("image_count", 1)
        image_points = int(30 * alt_ratio)
        score += image_points
        details.append({"criterion": "Opisy alternatywne obrazów", "points": image_points, "max": 30})
    else:
        score += 30
        details.append({"criterion": "Opisy alternatywne obrazów", "points": 30, "max": 30})
    if is_pdf_ua_compliant:
        score += 30
        details.append({"criterion": "Zgodność z PDF/UA", "points": 30, "max": 30})
    else:
        details.append({"criterion": "Zgodność z PDF/UA", "points": 0, "max": 30})
    
    level = "Wysoki" if score >= 80 else "Średni" if score >= 50 else "Niski"
    return {
        "total_score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100),
        "level": level,
        "details": details
    }

def generate_recommendations(analysis: dict, failed_rules: list) -> list:
    recommendations = []
    if not analysis.get("is_tagged"):
        recommendations.append({
            "priority": "high", "issue": "Brak tagów struktury",
            "recommendation": "Dodaj tagi struktury do dokumentu PDF używając Adobe Acrobat Pro lub podobnego narzędzia."
        })
    image_info = analysis.get("image_info", {})
    if image_info.get("images_without_alt", 0) > 0:
        recommendations.append({
            "priority": "high", "issue": f"Brakuje opisów alternatywnych dla {image_info['images_without_alt']} obrazów",
            "recommendation": "Dodaj opisy alternatywne (alt text) do wszystkich obrazów w dokumencie."
        })
    if len(failed_rules) > 0:
        for rule in failed_rules[:5]:
            recommendations.append({
                "priority": "medium", "issue": f"Naruszenie PDF/UA: {rule.get('description', 'Brak opisu')}",
                "recommendation": f"Napraw błąd związany z klauzulą {rule.get('clause', 'N/A')}"
            })
    return recommendations


@celery_app.task(name='app.tasks.run_full_pdf_analysis')
def run_full_pdf_analysis_task(file_bytes: bytes, filename: str):
    """
    Zadanie Celery, które wykonuje PEŁNĄ, kompleksową analizę pliku PDF w tle.
    """
    # 1. Analiza podstawowa z pdf_analyzer.py
    analysis_result = pdf_analyzer.analyze_pdf(file_bytes)
    if analysis_result is None:
        raise Exception("Podstawowa analiza pliku PDF nie powiodła się.")

    # 2. Walidacja PDF/UA
    unique_filename_task = f"{uuid.uuid4()}.pdf"
    file_path_task = os.path.join(PDF_STORAGE_PATH, unique_filename_task)
    
    try:
        with open(file_path_task, "wb") as buffer:
               buffer.write(file_bytes)
        is_compliant, report_xml = pdf_analyzer.validate_pdf_ua(unique_filename_task)
        failed_rules = pdf_analyzer.parse_verapdf_report(report_xml)
    finally:
        if os.path.exists(file_path_task):
            os.remove(file_path_task)

    # 3. Złożenie finalnego raportu (logika z /generate-report/)
    report = {
        "metadata": {
            "filename": filename,
            "analysis_date": datetime.now().isoformat(),
            "file_size": len(file_bytes)
        },
        "basic_analysis": analysis_result,
        "pdf_ua_validation": {
            "is_compliant": is_compliant,
            "failed_rules_count": len(failed_rules),
            "failed_rules": failed_rules
        },
        "accessibility_score": calculate_accessibility_score(analysis_result, is_compliant),
        "recommendations": generate_recommendations(analysis_result, failed_rules)
    }
    
    return report