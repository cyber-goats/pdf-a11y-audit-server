import os
import uuid
from datetime import datetime
from celery import Celery
from app.analysis_enhanced import EnhancedPdfAnalysis
from app.analysis import validate_pdf_ua, parse_verapdf_report
from app.models.analysis_levels import AnalysisLevel
from app.common.exceptions import PDFAnalysisError

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
celery_app = Celery(
    'tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
)

PDF_STORAGE_PATH = "/tmp/pdfs"

@celery_app.task(name='app.tasks.run_enhanced_pdf_analysis')
def run_enhanced_pdf_analysis_task(
    file_bytes: bytes, 
    filename: str,
    analysis_level: str = "standard"
):
    """
    Zadanie Celery wykonujące analizę PDF z wybranym poziomem szczegółowości.
    """
    analysis = None
    level = AnalysisLevel(analysis_level)
    config = level.get_config()
    
    try:
        # Update stanu zadania
        celery_app.current_task.update_state(state='ANALYZING', meta={'progress': 10})
        
        # 1. Analiza z wybranym poziomem
        analysis = EnhancedPdfAnalysis(file_bytes)
        analysis_result = analysis.analyze(level)
        
        # 2. Walidacja PDF/UA (tylko dla STANDARD i PROFESSIONAL)
        pdf_ua_result = None
        if not config["skip_verapdf"]:
            celery_app.current_task.update_state(state='ANALYZING', meta={'progress': 50})
            
            unique_filename = f"{uuid.uuid4()}.pdf"
            file_path = os.path.join(PDF_STORAGE_PATH, unique_filename)
            
            with open(file_path, "wb") as buffer:
                buffer.write(file_bytes)
            
            try:
                is_compliant, report_xml = validate_pdf_ua(unique_filename)
                failed_rules = parse_verapdf_report(report_xml)
                
                pdf_ua_result = {
                    "is_compliant": is_compliant,
                    "failed_rules_count": len(failed_rules),
                    "failed_rules": failed_rules[:5] if level == AnalysisLevel.STANDARD else failed_rules
                }
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        celery_app.current_task.update_state(state='FINALIZING', meta={'progress': 90})
        
        # 3. Generowanie wynikowego raportu
        report = _generate_report(
            filename=filename,
            analysis_result=analysis_result,
            pdf_ua_result=pdf_ua_result,
            level=level,
            file_size=len(file_bytes)
        )
        
        return report
        
    except PDFAnalysisError as e:
        raise e
    finally:
        if analysis:
            analysis.close()

def _generate_report(filename: str, analysis_result: dict, pdf_ua_result: dict, 
                    level: AnalysisLevel, file_size: int) -> dict:
    """
    Generuje raport dostosowany do poziomu analizy
    """
    
    # Podstawowy raport (QUICK)
    report = {
        "metadata": {
            "filename": filename,
            "analysis_date": datetime.now().isoformat(),
            "file_size": file_size,
            "analysis_level": level.value,
            "analysis_time": analysis_result.get("analysis_time", 0)
        },
        "analysis_level": level.value,
        "basic_results": {
            "page_count": analysis_result["page_count"],
            "is_tagged": analysis_result["is_tagged"],
            "contains_text": analysis_result["contains_text"],
            **analysis_result.get("quick_metrics", {})
        }
    }
    
    # Dodaj wyniki STANDARD
    if level in [AnalysisLevel.STANDARD, AnalysisLevel.PROFESSIONAL]:
        report["detailed_results"] = {
            "metadata": analysis_result.get("metadata", {}),
            "image_info": analysis_result.get("image_info", {}),
            "heading_info": analysis_result.get("heading_info", {}),
            "text_preview": analysis_result.get("text_preview", "")
        }
        
        if pdf_ua_result:
            report["pdf_ua_validation"] = pdf_ua_result
        
        # Dodaj rekomendacje
        report["recommendations"] = _generate_recommendations(
            analysis_result, 
            pdf_ua_result
        )
        
        # Oblicz szczegółowy wynik dostępności
        report["accessibility_score"] = _calculate_detailed_score(
            analysis_result,
            pdf_ua_result
        )
    
    # Dodaj wyniki PROFESSIONAL (deep scan)
    if level == AnalysisLevel.PROFESSIONAL:
        report["deep_scan"] = analysis_result.get("deep_scan", {})
        
        # Dodaj szczegółowe rekomendacje WCAG
        report["wcag_compliance"] = _generate_wcag_report(
            analysis_result,
            pdf_ua_result
        )
    
    return report

def _generate_recommendations(analysis: dict, pdf_ua: dict) -> list:
    """Generuje rekomendacje na podstawie analizy"""
    recommendations = []
    
    # Rekomendacje podstawowe
    if not analysis.get("is_tagged"):
        recommendations.append({
            "priority": "high",
            "category": "structure",
            "issue": "Brak tagów struktury",
            "recommendation": "Dodaj tagi struktury do dokumentu PDF używając Adobe Acrobat Pro.",
            "wcag_reference": "WCAG 1.3.1"
        })
    
    # Rekomendacje dla obrazów
    image_info = analysis.get("image_info", {})
    if image_info.get("images_without_alt", 0) > 0:
        recommendations.append({
            "priority": "high",
            "category": "images",
            "issue": f"Brakuje opisów alternatywnych dla {image_info['images_without_alt']} obrazów",
            "recommendation": "Dodaj opisy alternatywne (alt text) do wszystkich znaczących obrazów.",
            "wcag_reference": "WCAG 1.1.1"
        })
    
    # Rekomendacje dla metadanych
    metadata = analysis.get("metadata", {})
    if not metadata.get("is_title_defined"):
        recommendations.append({
            "priority": "medium",
            "category": "metadata",
            "issue": "Brak tytułu dokumentu",
            "recommendation": "Ustaw tytuł dokumentu we właściwościach PDF.",
            "wcag_reference": "WCAG 2.4.2"
        })
    
    if not metadata.get("is_lang_defined"):
        recommendations.append({
            "priority": "medium",
            "category": "metadata",
            "issue": "Brak zdefiniowanego języka dokumentu",
            "recommendation": "Ustaw język dokumentu we właściwościach PDF (np. 'pl-PL' dla polskiego).",
            "wcag_reference": "WCAG 3.1.1"
        })
    
    # Rekomendacje dla nagłówków
    heading_info = analysis.get("heading_info", {})
    if heading_info and not heading_info.get("has_single_h1"):
        recommendations.append({
            "priority": "medium",
            "category": "headings",
            "issue": f"Nieprawidłowa liczba nagłówków H1: {heading_info.get('h1_count', 0)}",
            "recommendation": "Dokument powinien mieć dokładnie jeden nagłówek H1.",
            "wcag_reference": "WCAG 1.3.1"
        })
    
    return recommendations

def _calculate_detailed_score(analysis: dict, pdf_ua: dict) -> dict:
    """Oblicza szczegółowy wynik dostępności"""
    score = 0
    max_score = 100
    details = []
    
    # Tagowanie (25 pkt)
    if analysis.get("is_tagged"):
        tag_score = 25
        # Bonus za jakość tagowania
        if analysis.get("deep_scan", {}).get("tagging_details", {}).get("structure_quality", 0) > 50:
            tag_score = 25
        else:
            tag_score = 15
        score += tag_score
        details.append({"criterion": "Struktura tagów", "points": tag_score, "max": 25})
    else:
        details.append({"criterion": "Struktura tagów", "points": 0, "max": 25})
    
    # Tekst (15 pkt)
    if analysis.get("contains_text"):
        score += 15
        details.append({"criterion": "Zawiera tekst", "points": 15, "max": 15})
    else:
        details.append({"criterion": "Zawiera tekst", "points": 0, "max": 15})
    
    # Alt-teksty (20 pkt)
    image_info = analysis.get("image_info", {})
    if image_info.get("image_count", 0) > 0:
        alt_ratio = image_info.get("images_with_alt", 0) / image_info.get("image_count", 1)
        alt_points = int(20 * alt_ratio)
        score += alt_points
        details.append({"criterion": "Opisy alternatywne", "points": alt_points, "max": 20})
    else:
        score += 20  # Brak obrazów = pełne punkty
        details.append({"criterion": "Opisy alternatywne", "points": 20, "max": 20})
    
    # Metadane (10 pkt)
    metadata = analysis.get("metadata", {})
    metadata_points = 0
    if metadata.get("is_title_defined"):
        metadata_points += 5
    if metadata.get("is_lang_defined"):
        metadata_points += 5
    score += metadata_points
    details.append({"criterion": "Metadane", "points": metadata_points, "max": 10})
    
    # PDF/UA (30 pkt)
    if pdf_ua and pdf_ua.get("is_compliant"):
        score += 30
        details.append({"criterion": "Zgodność PDF/UA", "points": 30, "max": 30})
    elif pdf_ua:
        # Częściowe punkty za mniej błędów
        partial = max(0, 30 - pdf_ua.get("failed_rules_count", 30))
        score += partial
        details.append({"criterion": "Zgodność PDF/UA", "points": partial, "max": 30})
    
    level = "Wysoki" if score >= 80 else "Średni" if score >= 50 else "Niski"
    
    return {
        "total_score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100),
        "level": level,
        "details": details
    }

def _generate_wcag_report(analysis: dict, pdf_ua: dict) -> dict:
    """Generuje szczegółowy raport zgodności WCAG (PROFESSIONAL)"""
    return {
        "wcag_version": "2.1",
        "conformance_level": "AA",
        "passed_criteria": [],
        "failed_criteria": [],
        "not_applicable": [],
        "summary": {
            "total_criteria": 50,  # Przykładowa liczba
            "passed": 0,
            "failed": 0,
            "not_applicable": 0
        }
    }