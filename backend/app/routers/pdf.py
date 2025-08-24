from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from app.services import pdf_analyzer
from app.common.exceptions import PDFAnalysisError
from datetime import datetime
from weasyprint import HTML
import shutil
import os
import uuid
import json
import io
from enum import Enum

class ReportFormat(str, Enum):
    json = "json"
    html = "html"
    pdf = "pdf"



router = APIRouter()

# Katalog do przechowywania plików w wolumenie Dockera
PDF_STORAGE_PATH = "/tmp/pdfs"
os.makedirs(PDF_STORAGE_PATH, exist_ok=True)

@router.post("/upload/pdf/", tags=["PDF Processing"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint do przyjmowania i analizowania plików PDF.
    """
    if file.content_type != "application/pdf":
        return JSONResponse(
            status_code=400,
            content={
                "detail": {
                    "error_code": "ERR_INVALID_FILE_TYPE",
                    "message": "Nieprawidłowy typ pliku. Proszę przesłać plik PDF."
                }
            }
        )

    try:
        file_bytes = await file.read()
        analysis_result = pdf_analyzer.analyze_pdf(file_bytes)
        
        if analysis_result is None:
             raise HTTPException(status_code=422, detail="Could not process the PDF file.")

        analysis_result["filename"] = file.filename
        return analysis_result

    except PDFAnalysisError as e:
        return JSONResponse(
            status_code=422, # Unprocessable Entity
            content={"detail": {"error_code": e.error_code, "message": e.message}}
        )
    except Exception as e:
        print(f"Krytyczny, nieobsłużony błąd serwera: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": {
                    "error_code": "ERR_UNKNOWN",
                    "message": "Wystąpił nieoczekiwany błąd wewnętrzny serwera."
                }
            }
        )

@router.post("/validate/pdf-ua", tags=["Validation"])
async def validate_pdf_ua_endpoint(file: UploadFile = File(...)):
    unique_filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(PDF_STORAGE_PATH, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Uruchamiamy walidację, która zwraca XML
    is_compliant, report_xml = pdf_analyzer.validate_pdf_ua(unique_filename)
    # PARSUJEMY XML, ABY UZYSKAĆ LISTĘ BŁĘDÓW
    failed_rules = pdf_analyzer.parse_verapdf_report(report_xml)

    os.remove(file_path)

    # Zwracamy czyste i ustrukturyzowane dane
    return {
        "filename": file.filename,
        "is_compliant_with_pdf_ua": is_compliant,
        "failed_rules_count": len(failed_rules),
        "failed_rules": failed_rules
    }

@router.post("/generate-report/", tags=["Reports"])
async def generate_report(file: UploadFile = File(...)):
    """
    Generuje kompleksowy raport dostępności PDF
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type.")
    
    file_bytes = await file.read()
    
    # Analiza podstawowa
    analysis_result = pdf_analyzer.analyze_pdf(file_bytes)
    
    if analysis_result is None:
        raise HTTPException(status_code=422, detail="Could not process the PDF file.")
    
    # Walidacja PDF/UA
    unique_filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(PDF_STORAGE_PATH, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_bytes)
        
        is_compliant, report_xml = pdf_analyzer.validate_pdf_ua(unique_filename)
        failed_rules = pdf_analyzer.parse_verapdf_report(report_xml)
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Tworzenie kompleksowego raportu
    report = {
        "metadata": {
            "filename": file.filename,
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

@router.post("/download-report/{format}", tags=["Reports"])
async def download_report(format: ReportFormat, report_data: dict): # Zmieniony typ parametru
    """
    Pobiera raport w wybranym formacie (json, html, pdf)
    """
    if format == ReportFormat.json:
        content = json.dumps(report_data, indent=2, ensure_ascii=False)
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
        )

    elif format == ReportFormat.html:
        html_content = generate_html_report(report_data)
        return StreamingResponse(
            io.BytesIO(html_content.encode()),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"}
        )

    elif format == ReportFormat.pdf:
        html_content = generate_html_report(report_data)
        pdf_bytes = HTML(string=html_content).write_pdf()
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
        )

def calculate_accessibility_score(analysis: dict, is_pdf_ua_compliant: bool) -> dict:
    """Oblicza szczegółowy wynik dostępności"""
    score = 0
    max_score = 100
    details = []
    
    # Struktura dokumentu (40 pkt)
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
    
    # Obrazy (30 pkt)
    image_info = analysis.get("image_info", {})
    if image_info.get("image_count", 0) > 0:
        alt_ratio = image_info.get("images_with_alt", 0) / image_info.get("image_count", 1)
        image_points = int(30 * alt_ratio)
        score += image_points
        details.append({"criterion": "Opisy alternatywne obrazów", "points": image_points, "max": 30})
    else:
        score += 30  # Brak obrazów = pełne punkty
        details.append({"criterion": "Opisy alternatywne obrazów", "points": 30, "max": 30})
    
    # PDF/UA compliance (30 pkt)
    if is_pdf_ua_compliant:
        score += 30
        details.append({"criterion": "Zgodność z PDF/UA", "points": 30, "max": 30})
    else:
        details.append({"criterion": "Zgodność z PDF/UA", "points": 0, "max": 30})
    
    return {
        "total_score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100),
        "level": get_accessibility_level(score),
        "details": details
    }

def get_accessibility_level(score: int) -> str:
    if score >= 80:
        return "Wysoki"
    elif score >= 50:
        return "Średni"
    else:
        return "Niski"

def generate_recommendations(analysis: dict, failed_rules: list) -> list:
    recommendations = []
    
    if not analysis.get("is_tagged"):
        recommendations.append({
            "priority": "high",
            "issue": "Brak tagów struktury",
            "recommendation": "Dodaj tagi struktury do dokumentu PDF używając Adobe Acrobat Pro lub podobnego narzędzia."
        })
    
    image_info = analysis.get("image_info", {})
    if image_info.get("images_without_alt", 0) > 0:
        recommendations.append({
            "priority": "high",
            "issue": f"Brakuje opisów alternatywnych dla {image_info['images_without_alt']} obrazów",
            "recommendation": "Dodaj opisy alternatywne (alt text) do wszystkich obrazów w dokumencie."
        })
    
    if len(failed_rules) > 0:
        for rule in failed_rules[:5]:  # Top 5 błędów
            recommendations.append({
                "priority": "medium",
                "issue": f"Naruszenie PDF/UA: {rule.get('description', 'Brak opisu')}",
                "recommendation": f"Napraw błąd związany z klauzulą {rule.get('clause', 'N/A')}"
            })
    
    return recommendations

def generate_html_report(report_data: dict) -> str:
    """Generuje nowoczesny i poprawnie ostylowany raport w formacie HTML."""

    # Bezpieczne pobieranie danych z raportu
    metadata = report_data.get('metadata', {})
    score_data = report_data.get('accessibility_score', {})
    recommendations = report_data.get('recommendations', [])

    filename = metadata.get('filename', 'Brak nazwy')
    analysis_date = metadata.get('analysis_date', 'Brak daty')

    percentage = score_data.get('percentage', 0)
    level = score_data.get('level', 'Niski')
    details = score_data.get('details', [])

    # Mapowanie poziomów na klasy CSS i kolory
    level_map = {
        "Wysoki": {"class": "high", "color": "#10B981"},
        "Średni": {"class": "medium", "color": "#F59E0B"},
        "Niski": {"class": "low", "color": "#EF4444"}
    }
    level_info = level_map.get(level, level_map["Niski"])

    # Generowanie wierszy tabeli ze szczegółami wyników
    details_rows = ""
    for detail in details:
        details_rows += f"""
            <tr>
                <td>{detail.get('criterion', 'Brak danych')}</td>
                <td>{detail.get('points', 0)} / {detail.get('max', 0)}</td>
            </tr>
        """

    # Generowanie listy rekomendacji
    recommendations_list = ""
    if recommendations:
        for rec in recommendations:
            priority = rec.get('priority', 'low')
            recommendations_list += f"""
                <div class="recommendation {priority}">
                    <span class="priority {priority}">{priority.upper()}</span>
                    <div class="content">
                        <strong>{rec.get('issue', 'Brak danych')}</strong>
                        <p>{rec.get('recommendation', 'Brak danych')}</p>
                    </div>
                </div>
            """
    else:
        recommendations_list = "<p>Brak rekomendacji. Dobra robota!</p>"

    # Kompletny szablon HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Raport Dostępności PDF</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
            body {{
                font-family: 'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8f9fa;
                color: #212529;
                margin: 0;
                padding: 2rem;
                line-height: 1.6;
            }}
            .container {{
                max-width: 800px;
                margin: auto;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.05);
                overflow: hidden;
            }}
            .header {{
                background-color: #4A5568;
                color: #ffffff;
                padding: 2rem;
            }}
            .header h1 {{ margin: 0; font-size: 2.25rem; }}
            .header p {{ margin: 0.25rem 0 0; opacity: 0.8; }}
            .section {{ padding: 2rem; border-bottom: 1px solid #e9ecef; }}
            .section:last-child {{ border-bottom: none; }}
            h2 {{ font-size: 1.75rem; color: #2c3e50; margin-top: 0; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.5rem; }}
            .score-card {{
                text-align: center;
                padding: 2rem;
                border: 1px solid {level_info['color']};
                background-color: color-mix(in srgb, {level_info['color']} 10%, transparent);
                border-radius: 8px;
            }}
            .score {{
                font-size: 4.5rem;
                font-weight: 700;
                color: {level_info['color']};
            }}
            .score-level {{ font-size: 1.25rem; color: {level_info['color']}; font-weight: 700; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 1.5rem;
            }}
            th, td {{
                padding: 0.75rem 1rem;
                text-align: left;
                border-bottom: 1px solid #dee2e6;
            }}
            th {{ background-color: #f1f3f5; font-weight: 700; }}
            .recommendation {{
                display: flex;
                align-items: flex-start;
                gap: 1rem;
                margin-bottom: 1rem;
                padding: 1rem;
                background-color: #f8f9fa;
                border-radius: 8px;
                border-left: 5px solid;
            }}
            .recommendation .priority {{
                flex-shrink: 0;
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.8rem;
                font-weight: 700;
                color: #fff;
            }}
            .recommendation .priority.high {{ background-color: #EF4444; }}
            .recommendation .priority.medium {{ background-color: #F59E0B; }}
            .recommendation .priority.low {{ background-color: #10B981; }}
            .recommendation strong {{ display: block; margin-bottom: 0.25rem; font-size: 1.1rem; }}
            .recommendation p {{ margin: 0; }}
            .recommendation.high {{ border-color: #EF4444; }}
            .recommendation.medium {{ border-color: #F59E0B; }}
            .recommendation.low {{ border-color: #10B981; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header class="header">
                <h1>Raport Dostępności PDF</h1>
                <p><strong>Plik:</strong> {filename}</p>
                <p><strong>Data analizy:</strong> {analysis_date}</p>
            </header>

            <section class="section">
                <h2>Wynik Dostępności</h2>
                <div class="score-card">
                    <div class="score">{percentage}%</div>
                    <div class="score-level">Poziom: {level}</div>
                </div>
            </section>

            <section class="section">
                <h2>Szczegóły Analizy</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Kryterium</th>
                            <th>Wynik</th>
                        </tr>
                    </thead>
                    <tbody>
                        {details_rows}
                    </tbody>
                </table>
            </section>

            <section class="section">
                <h2>Rekomendacje</h2>
                {recommendations_list}
            </section>
        </div>
    </body>
    </html>
    """

    return html