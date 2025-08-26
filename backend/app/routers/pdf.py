from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from celery.result import AsyncResult
from weasyprint import HTML
import json
import io
from datetime import datetime
from enum import Enum

# Importujemy tylko to, co jest naprawdę potrzebne
from app.tasks import run_full_pdf_analysis_task
from app.services.redis_client import redis_client

# Definicja formatów raportu
class ReportFormat(str, Enum):
    json = "json"
    html = "html"
    pdf = "pdf"

router = APIRouter()

# --- GŁÓWNE ENDPOINTY APLIKACJI ---

@router.post("/upload/", tags=["PDF Processing"], status_code=202)
async def upload_pdf_for_analysis(file: UploadFile = File(...)):
    """
    Przyjmuje plik PDF, uruchamia analizę w tle i zwraca ID zadania.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Nieprawidłowy typ pliku. Proszę przesłać plik PDF."
        )
    try:
        file_bytes = await file.read()
        task = run_full_pdf_analysis_task.delay(file_bytes=file_bytes, filename=file.filename)
        return {"task_id": task.id}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Wystąpił błąd podczas uruchamiania zadania: {str(e)}"}
        )

@router.get("/analysis/{task_id}", tags=["PDF Processing"])
async def get_analysis_status(task_id: str):
    """
    Sprawdza status zadania analizy na podstawie jego ID i zwraca wynik.
    """
    task_result = AsyncResult(task_id)
    if task_result.ready():
        if task_result.successful():
            result = task_result.get()
            return {"status": "SUCCESS", "result": result}
        else:
            return JSONResponse(
                status_code=500,
                content={"status": "FAILURE", "error_message": str(task_result.info)}
            )
    else:
        return {"status": task_result.state}

@router.post("/download-report/{format}", tags=["Reports"])
async def download_report(format: ReportFormat, report_data: dict):
    """
    Pobiera gotowy raport (przesłany w body) w wybranym formacie.
    """
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if format == ReportFormat.json:
        content = json.dumps(report_data, indent=2, ensure_ascii=False)
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}.json"}
        )

    # Generowanie HTML jest potrzebne zarówno dla formatu HTML, jak i PDF
    html_content = generate_html_report(report_data)

    if format == ReportFormat.html:
        return StreamingResponse(
            io.BytesIO(html_content.encode()),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={filename}.html"}
        )

    if format == ReportFormat.pdf:
        pdf_bytes = HTML(string=html_content).write_pdf()
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}.pdf"}
        )

# --- ENDPOINTY DO ZARZĄDZANIA CACHEM ---

@router.get("/cache/status", tags=["Cache Management"])
async def get_cache_status():
    """
    Monitoruje status i metryki cache Redis.
    """
    try:
        metrics = redis_client.get_metrics()
        return {
            "redis_available": metrics.get('redis_available', False),
            "cache_metrics": metrics
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.delete("/cache/clear", tags=["Cache Management"])
async def clear_cache(pattern: str = None):
    """
    Czyści cache według podanego wzorca.
    """
    deleted_count = redis_client.invalidate_cache(pattern)
    return {"status": "success", "deleted_count": deleted_count}


# --- FUNKCJE POMOCNICZE (UŻYWANE PRZEZ ENDPOINTY W TYM PLIKU) ---

def generate_html_report(report_data: dict) -> str:
    """
    Generuje raport w formacie HTML na podstawie danych JSON.
    Pozostaje tutaj, ponieważ jest bezpośrednio używana przez endpoint /download-report/.
    """
    metadata = report_data.get('metadata', {})
    score_data = report_data.get('accessibility_score', {})
    recommendations = report_data.get('recommendations', [])
    filename = metadata.get('filename', 'Brak nazwy')
    analysis_date = metadata.get('analysis_date', 'Brak daty')
    percentage = score_data.get('percentage', 0)
    level = score_data.get('level', 'Niski')
    details = score_data.get('details', [])

    level_map = {
        "Wysoki": {"class": "high", "color": "#10B981"},
        "Średni": {"class": "medium", "color": "#F59E0B"},
        "Niski": {"class": "low", "color": "#EF4444"}
    }
    level_info = level_map.get(level, level_map["Niski"])

    details_rows = ""
    for detail in details:
        details_rows += f"""<tr><td>{detail.get('criterion', 'Brak danych')}</td><td>{detail.get('points', 0)} / {detail.get('max', 0)}</td></tr>"""

    recommendations_list = ""
    if recommendations:
        for rec in recommendations:
            priority = rec.get('priority', 'low')
            recommendations_list += f"""<div class="recommendation {priority}"><span class="priority {priority}">{priority.upper()}</span><div class="content"><strong>{rec.get('issue', 'Brak danych')}</strong><p>{rec.get('recommendation', 'Brak danych')}</p></div></div>"""
    else:
        recommendations_list = "<p>Brak rekomendacji. Dobra robota!</p>"

    html = f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <title>Raport Dostępności PDF</title>
        <style>
            body {{ font-family: 'Lato', sans-serif; background-color: #f8f9fa; color: #212529; margin: 0; padding: 2rem; }}
            .container {{ max-width: 800px; margin: auto; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); overflow: hidden; }}
            .header {{ background-color: #4A5568; color: #ffffff; padding: 2rem; }}
            .header h1 {{ margin: 0; }} .header p {{ opacity: 0.8; }}
            .section {{ padding: 2rem; border-bottom: 1px solid #e9ecef; }} .section:last-child {{ border-bottom: none; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.5rem; }}
            .score-card {{ text-align: center; padding: 2rem; border: 1px solid {level_info['color']}; background-color: {level_info['color']}1A; border-radius: 8px; }}
            .score {{ font-size: 4.5rem; font-weight: 700; color: {level_info['color']}; }}
            .score-level {{ font-size: 1.25rem; font-weight: 700; color: {level_info['color']}; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 1.5rem; }}
            th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #dee2e6; }}
            th {{ background-color: #f1f3f5; }}
            .recommendation {{ display: flex; gap: 1rem; margin-bottom: 1rem; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; border-left: 5px solid; }}
            .recommendation.high {{ border-color: #EF4444; }} .recommendation.medium {{ border-color: #F59E0B; }} .recommendation.low {{ border-color: #10B981; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header class="header"><h1>Raport Dostępności PDF</h1><p><strong>Plik:</strong> {filename}</p><p><strong>Data analizy:</strong> {analysis_date}</p></header>
            <section class="section"><h2>Wynik Dostępności</h2><div class="score-card"><div class="score">{percentage}%</div><div class="score-level">Poziom: {level}</div></div></section>
            <section class="section"><h2>Szczegóły Analizy</h2><table><thead><tr><th>Kryterium</th><th>Wynik</th></tr></thead><tbody>{details_rows}</tbody></table></section>
            <section class="section"><h2>Rekomendacje</h2>{recommendations_list}</section>
        </div>
    </body>
    </html>
    """
    return html