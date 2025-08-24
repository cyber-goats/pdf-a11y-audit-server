from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from app.services import pdf_analyzer
from datetime import datetime
import shutil
import os
import uuid
import json
import io

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
        raise HTTPException(status_code=400, detail="Invalid file type.")

    file_bytes = await file.read()
    
    analysis_result = pdf_analyzer.analyze_pdf(file_bytes)
    
    if analysis_result is None:
        raise HTTPException(status_code=422, detail="Could not process the PDF file.")
    
    analysis_result["filename"] = file.filename
    return analysis_result

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
async def download_report(format: str, report_data: dict):
    """
    Pobiera raport w wybranym formacie (json, html)
    """
    if format == "json":
        content = json.dumps(report_data, indent=2, ensure_ascii=False)
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
        )
    
    elif format == "html":
        html_content = generate_html_report(report_data)
        return StreamingResponse(
            io.BytesIO(html_content.encode()),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

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
    """Generuje raport w formacie HTML"""
    html = f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <title>Raport dostępności PDF</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            .score {{ font-size: 48px; font-weight: bold; }}
            .high {{ color: #10b981; }}
            .medium {{ color: #f59e0b; }}
            .low {{ color: #ef4444; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f3f4f6; }}
        </style>
    </head>
    <body>
        <h1>Raport dostępności PDF</h1>
        <p><strong>Plik:</strong> {report_data['metadata']['filename']}</p>
        <p><strong>Data analizy:</strong> {report_data['metadata']['analysis_date']}</p>
        
        <h2>Wynik dostępności</h2>
        <div class="score {report_data['accessibility_score']['level'].lower()}">
            {report_data['accessibility_score']['percentage']}%
        </div>
        <p>Poziom: {report_data['accessibility_score']['level']}</p>
        
        <h2>Szczegóły analizy</h2>
        <table>
            <tr><th>Kryterium</th><th>Punkty</th><th>Max</th></tr>
    """
    
    for detail in report_data['accessibility_score']['details']:
        html += f"""
            <tr>
                <td>{detail['criterion']}</td>
                <td>{detail['points']}</td>
                <td>{detail['max']}</td>
            </tr>
        """
    
    html += """
        </table>
        
        <h2>Rekomendacje</h2>
        <ul>
    """
    
    for rec in report_data['recommendations']:
        html += f"<li><strong>[{rec['priority'].upper()}]</strong> {rec['issue']}: {rec['recommendation']}</li>"
    
    html += """
        </ul>
    </body>
    </html>
    """
    
    return html