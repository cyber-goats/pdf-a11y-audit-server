import os
import uuid
from datetime import datetime
from celery import Celery
from app.analysis import PdfAnalysis, validate_pdf_ua, parse_verapdf_report
from app.common.exceptions import PDFAnalysisError

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
    """
    Oblicza wynik dostępności uwzględniając wszystkie aspekty analizy.
    Maksymalnie 100 punktów rozdzielonych na kategorie.
    """
    score = 0
    max_score = 100
    details = []
    
    # 1. STRUKTURA TAGÓW (15 pkt)
    if analysis.get("is_tagged"):
        score += 15
        details.append({"criterion": "Dokument otagowany", "points": 15, "max": 15})
    else:
        details.append({"criterion": "Dokument otagowany", "points": 0, "max": 15})
    
    # 2. ZAWARTOŚĆ TEKSTOWA (10 pkt)
    if analysis.get("contains_text"):
        score += 10
        details.append({"criterion": "Zawiera tekst", "points": 10, "max": 10})
    else:
        details.append({"criterion": "Zawiera tekst", "points": 0, "max": 10})
    
    # 3. METADANE (10 pkt)
    metadata_points = 0
    # Tytuł dokumentu (5 pkt)
    if analysis.get("is_title_defined"):
        metadata_points += 5
    # Język dokumentu (5 pkt)
    if analysis.get("is_lang_defined"):
        metadata_points += 5
    score += metadata_points
    details.append({"criterion": "Metadane dokumentu", "points": metadata_points, "max": 10})
    
    # 4. NAGŁÓWKI (15 pkt)
    heading_points = 0
    heading_info = analysis.get("heading_info", {})
    if heading_info:
        # Pojedynczy H1 (7 pkt)
        if heading_info.get("has_single_h1"):
            heading_points += 7
        elif heading_info.get("h1_count", 0) > 0:
            heading_points += 3  # Częściowe punkty za H1
        
        # Poprawna hierarchia (8 pkt)
        if not heading_info.get("has_skipped_levels"):
            heading_points += 8
        elif heading_info.get("heading_structure"):
            heading_points += 4  # Częściowe punkty za jakąkolwiek strukturę
    
    score += heading_points
    details.append({"criterion": "Struktura nagłówków", "points": heading_points, "max": 15})
    
    # 5. OPISY ALTERNATYWNE OBRAZÓW (20 pkt)
    image_points = 0
    image_info = analysis.get("image_info", {})
    if image_info.get("image_count", 0) > 0:
        alt_ratio = image_info.get("images_with_alt", 0) / image_info.get("image_count", 1)
        image_points = int(20 * alt_ratio)
        score += image_points
        details.append({"criterion": "Opisy alternatywne obrazów", "points": image_points, "max": 20})
    else:
        # Brak obrazów = pełne punkty (nie ma czego sprawdzać)
        score += 20
        details.append({"criterion": "Opisy alternatywne obrazów", "points": 20, "max": 20})
    
    # 6. ZGODNOŚĆ Z PDF/UA (30 pkt)
    if is_pdf_ua_compliant:
        score += 30
        details.append({"criterion": "Zgodność z PDF/UA", "points": 30, "max": 30})
    else:
        details.append({"criterion": "Zgodność z PDF/UA", "points": 0, "max": 30})
    
    # Określenie poziomu dostępności
    percentage = round((score / max_score) * 100)
    if percentage >= 85:
        level = "Wysoki"
    elif percentage >= 60:
        level = "Średni"
    elif percentage >= 40:
        level = "Niski"
    else:
        level = "Bardzo niski"
    
    return {
        "total_score": score,
        "max_score": max_score,
        "percentage": percentage,
        "level": level,
        "details": details
    }

def generate_recommendations(analysis: dict, failed_rules: list) -> list:
    """
    Generuje spersonalizowane rekomendacje na podstawie wszystkich aspektów analizy.
    Priorytetyzacja: high = krytyczne, medium = ważne, low = dobre praktyki
    """
    recommendations = []
    
    # 1. STRUKTURA TAGÓW (krytyczne)
    if not analysis.get("is_tagged"):
        recommendations.append({
            "priority": "high",
            "issue": "Brak tagów struktury",
            "recommendation": "Dodaj tagi struktury do dokumentu PDF używając Adobe Acrobat Pro lub podobnego narzędzia. To podstawa dostępności!",
            "wcag_reference": "WCAG 1.3.1"
        })
    
    # 2. METADANE DOKUMENTU
    # Tytuł (ważne)
    if not analysis.get("is_title_defined"):
        recommendations.append({
            "priority": "medium",
            "issue": "Brak tytułu dokumentu",
            "recommendation": "Ustaw opisowy tytuł dokumentu we właściwościach PDF. Tytuł pomaga użytkownikom zidentyfikować dokument.",
            "wcag_reference": "WCAG 2.4.2"
        })
    
    # Język (ważne)
    if not analysis.get("is_lang_defined"):
        recommendations.append({
            "priority": "medium",
            "issue": "Niezdefiniowany język dokumentu",
            "recommendation": "Ustaw język dokumentu we właściwościach PDF (np. 'pl-PL' dla polskiego). Czytniki ekranu potrzebują tej informacji.",
            "wcag_reference": "WCAG 3.1.1"
        })
    
    # 3. STRUKTURA NAGŁÓWKÓW
    heading_info = analysis.get("heading_info", {})
    if heading_info:
        # Brak H1 (ważne)
        if heading_info.get("h1_count", 0) == 0:
            recommendations.append({
                "priority": "medium",
                "issue": "Brak głównego nagłówka H1",
                "recommendation": "Dodaj dokładnie jeden nagłówek H1 na początku dokumentu. To tytuł główny całego dokumentu.",
                "wcag_reference": "WCAG 1.3.1, 2.4.6"
            })
        # Wiele H1 (średnie)
        elif heading_info.get("h1_count", 0) > 1:
            recommendations.append({
                "priority": "low",
                "issue": f"Za dużo nagłówków H1 ({heading_info.get('h1_count')})",
                "recommendation": "Użyj tylko jednego H1 jako głównego tytułu. Pozostałe nagłówki zamień na H2.",
                "wcag_reference": "WCAG 1.3.1"
            })
        
        # Pominięte poziomy (średnie)
        if heading_info.get("has_skipped_levels"):
            recommendations.append({
                "priority": "medium",
                "issue": "Nieprawidłowa hierarchia nagłówków",
                "recommendation": "Zachowaj logiczną kolejność nagłówków (H1→H2→H3). Nie pomijaj poziomów.",
                "wcag_reference": "WCAG 1.3.1"
            })
    
    # 4. OBRAZY BEZ ALT-TEKSTÓW (krytyczne)
    image_info = analysis.get("image_info", {})
    if image_info.get("images_without_alt", 0) > 0:
        count = image_info['images_without_alt']
        recommendations.append({
            "priority": "high",
            "issue": f"Brakuje opisów alternatywnych dla {count} {'obrazu' if count == 1 else 'obrazów'}",
            "recommendation": "Dodaj opisy alternatywne (alt text) do wszystkich znaczących obrazów. Dla obrazów dekoracyjnych użyj pustego alt=\"\".",
            "wcag_reference": "WCAG 1.1.1"
        })
    
    # 5. BRAK TEKSTU (krytyczne dla zeskanowanych PDF)
    if not analysis.get("contains_text") and image_info.get("image_count", 0) > 0:
        recommendations.append({
            "priority": "high",
            "issue": "Dokument zeskanowany bez warstwy tekstowej",
            "recommendation": "Przeprowadź OCR (rozpoznawanie tekstu) na dokumencie. Zeskanowane obrazy bez tekstu są niedostępne.",
            "wcag_reference": "WCAG 1.4.5"
        })
    
    # 6. BŁĘDY PDF/UA (grupowane)
    if len(failed_rules) > 0:
        # Pokaż max 3 najważniejsze błędy
        for rule in failed_rules[:3]:
            recommendations.append({
                "priority": "medium",
                "issue": f"Naruszenie PDF/UA: {rule.get('description', 'Brak opisu')}",
                "recommendation": f"Napraw błąd związany z klauzulą {rule.get('clause', 'N/A')}",
                "wcag_reference": f"PDF/UA {rule.get('clause', '')}"
            })
        
        # Jeśli jest więcej błędów, dodaj zbiorczą rekomendację
        if len(failed_rules) > 3:
            recommendations.append({
                "priority": "low",
                "issue": f"Pozostałe {len(failed_rules) - 3} błędy zgodności PDF/UA",
                "recommendation": "Przeprowadź pełną walidację PDF/UA używając narzędzia PAC 3 lub Adobe Acrobat Pro.",
                "wcag_reference": "ISO 14289-1"
            })
    
    # 7. POZYTYWNE WSKAZÓWKI (gdy dokument jest dobry)
    if not recommendations:
        recommendations.append({
            "priority": "info",
            "issue": "Gratulacje! Dokument spełnia podstawowe wymogi dostępności",
            "recommendation": "Rozważ przeprowadzenie testów z użytkownikami korzystającymi z technologii asystujących dla pełnej weryfikacji.",
            "wcag_reference": "WCAG 2.1 AA"
        })
    
    # Sortuj rekomendacje według priorytetu
    priority_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
    
    return recommendations

@celery_app.task(name='app.tasks.run_full_pdf_analysis')
def run_full_pdf_analysis_task(file_bytes: bytes, filename: str):
    """
    Zadanie Celery, które wykonuje kompleksową analizę pliku PDF.
    """
    analysis = None
    try:
        # 1. Analiza podstawowa
        analysis = PdfAnalysis(file_bytes)
        basic_analysis_result = analysis.run_basic_analysis()

        # 2. Walidacja PDF/UA
        unique_filename = f"{uuid.uuid4()}.pdf"
        file_path = os.path.join(PDF_STORAGE_PATH, unique_filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(file_bytes)
        
        is_compliant, report_xml = validate_pdf_ua(unique_filename)
        failed_rules = parse_verapdf_report(report_xml)

    except PDFAnalysisError as e:
        raise e  
    finally:
        if analysis:
            analysis.close() 
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

    # 3. Złożenie finalnego raportu
    report = {
        "metadata": {
            "filename": filename,
            "analysis_date": datetime.now().isoformat(),
            "file_size": len(file_bytes)
        },
        "basic_analysis": basic_analysis_result,
        "pdf_ua_validation": {
            "is_compliant": is_compliant,
            "failed_rules_count": len(failed_rules),
            "failed_rules": failed_rules
        },
        "accessibility_score": calculate_accessibility_score(basic_analysis_result, is_compliant),
        "recommendations": generate_recommendations(basic_analysis_result, failed_rules)
    }
    
    return report