from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from typing import Optional
from enum import Enum

from app.tasks import run_enhanced_pdf_analysis_task
from app.models.analysis_levels import AnalysisLevel

router = APIRouter()

@router.post("/upload/", tags=["PDF Processing"], status_code=202)
async def upload_pdf_for_analysis(
    file: UploadFile = File(...),
    analysis_level: AnalysisLevel = Query(
        default=AnalysisLevel.STANDARD,
        description="Poziom szczegółowości analizy"
    )
):
    """
    Przyjmuje plik PDF i uruchamia analizę z wybranym poziomem szczegółowości.
    
    Poziomy analizy:
    - **quick**: Szybki skan (<1s) - podstawowe TAK/NIE
    - **standard**: Standardowa analiza (5-10s) - szczegóły i rekomendacje  
    - **professional**: Pełny audyt (30s+) - deep scan wszystkich elementów
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Nieprawidłowy typ pliku. Proszę przesłać plik PDF."
        )
    
    # Sprawdź rozmiar pliku dla różnych poziomów
    file_bytes = await file.read()
    file_size_mb = len(file_bytes) / (1024 * 1024)
    
    # Limity rozmiaru dla poziomów
    size_limits = {
        AnalysisLevel.QUICK: 50,  # 50MB dla quick
        AnalysisLevel.STANDARD: 20,  # 20MB dla standard
        AnalysisLevel.PROFESSIONAL: 10  # 10MB dla professional
    }
    
    if file_size_mb > size_limits[analysis_level]:
        raise HTTPException(
            status_code=413,
            detail=f"Plik jest za duży dla poziomu {analysis_level.value}. "
                   f"Maksymalny rozmiar: {size_limits[analysis_level]}MB"
        )
    
    try:
        # Uruchom zadanie Celery z poziomem analizy
        task = run_enhanced_pdf_analysis_task.delay(
            file_bytes=file_bytes,
            filename=file.filename,
            analysis_level=analysis_level.value
        )
        
        return {
            "task_id": task.id,
            "analysis_level": analysis_level.value,
            "estimated_time": analysis_level.get_config()["estimated_time"],
            "message": f"Analiza rozpoczęta - poziom: {analysis_level.get_config()['name']}"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Wystąpił błąd podczas uruchamiania zadania: {str(e)}"}
        )

@router.get("/analysis-levels", tags=["PDF Processing"])
async def get_analysis_levels():
    """
    Zwraca dostępne poziomy analizy z opisami.
    """
    levels = []
    for level in AnalysisLevel:
        config = level.get_config()
        levels.append({
            "value": level.value,
            "name": config["name"],
            "description": config["description"],
            "estimated_time": config["estimated_time"],
            "includes": config["includes"]
        })
    
    return {"levels": levels}

@router.get("/analysis/{task_id}", tags=["PDF Processing"])
async def get_analysis_status(task_id: str):
    """
    Sprawdza status zadania analizy.
    Zwraca różne szczegóły w zależności od wybranego poziomu analizy.
    """
    task_result = AsyncResult(task_id)
    
    if task_result.ready():
        if task_result.successful():
            result = task_result.get()
            
            # Formatuj odpowiedź w zależności od poziomu
            analysis_level = result.get("analysis_level", "standard")
            
            response = {
                "status": "SUCCESS",
                "analysis_level": analysis_level,
                "result": result
            }
            
            # Dodaj podsumowanie dla łatwiejszego odczytu
            if analysis_level == AnalysisLevel.QUICK:
                response["summary"] = {
                    "accessible": result.get("is_tagged", False) and result.get("contains_text", False),
                    "quick_score": _calculate_quick_score(result)
                }
            
            return response
        else:
            return JSONResponse(
                status_code=500,
                content={"status": "FAILURE", "error_message": str(task_result.info)}
            )
    else:
        # Zwróć postęp w zależności od poziomu
        progress_info = {
            "status": task_result.state,
            "progress": _estimate_progress(task_result.state)
        }
        
        return progress_info

def _calculate_quick_score(result: dict) -> int:
    """Oblicza szybki wynik dostępności (0-100)"""
    score = 0
    if result.get("is_tagged"):
        score += 50
    if result.get("contains_text"):
        score += 30
    if not result.get("quick_metrics", {}).get("is_scanned_pdf"):
        score += 20
    return score

def _estimate_progress(state: str) -> int:
    """Szacuje postęp analizy na podstawie stanu"""
    progress_map = {
        "PENDING": 0,
        "STARTED": 10,
        "ANALYZING": 50,
        "FINALIZING": 90,
        "SUCCESS": 100
    }
    return progress_map.get(state, 50)