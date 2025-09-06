from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from app.models.rules import WCAGRule, RuleNotFoundError
from app.services.rules_service import rules_service

router = APIRouter(
    prefix="/rules",
    tags=["Knowledge Base"],
    responses={404: {"description": "Rule not found"}}
)

@router.get("/{rule_id}", response_model=WCAGRule)
async def get_rule(
    rule_id: str = Path(
        ...,
        description="ID reguły WCAG/PDF-UA (np. wcag_1.1.1)",
        example="wcag_1.1.1"
    )
):
    """
    Pobiera szczegóły pojedynczej reguły WCAG/PDF-UA.
    
    - **rule_id**: Unikalny identyfikator reguły
    
    Zwraca kompletne informacje o regule włączając:
    - Opis i wymagania
    - Poziom zgodności (A, AA, AAA)
    - Techniki implementacji
    - Przykłady i rekomendacje
    - Mapowanie na PDF/UA
    """
    try:
        rule = await rules_service.get_rule(rule_id)
        return rule
    except RuleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")

@router.get("/", response_model=List[WCAGRule])
async def list_rules(
    level: Optional[str] = Query(None, description="Filtruj po poziomie (A, AA, AAA)"),
    category: Optional[str] = Query(None, description="Filtruj po kategorii POUR"),
    pdf_specific: Optional[bool] = Query(None, description="Tylko reguły dla PDF"),
    search: Optional[str] = Query(None, description="Wyszukaj w tytule i opisie"),
    limit: int = Query(100, ge=1, le=500, description="Maksymalna liczba wyników"),
    offset: int = Query(0, ge=0, description="Offset dla paginacji")
):
    """
    Pobiera listę reguł z opcjonalnym filtrowaniem.
    
    Możliwe filtry:
    - **level**: A, AA, lub AAA
    - **category**: perceivable, operable, understandable, robust
    - **pdf_specific**: true dla reguł specyficznych dla PDF
    - **search**: tekst do wyszukania
    """
    try:
        if search:
            rules = await rules_service.search_rules(search)
        else:
            rules = await rules_service.get_all_rules(
                level=level,
                category=category, 
                pdf_specific=pdf_specific
            )
        
        # Paginacja
        total = len(rules)
        rules = rules[offset:offset + limit]
        
        return rules
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")

@router.get("/analysis/{task_id}/recommendations", response_model=List[dict])
async def get_recommendations_for_analysis(
    task_id: str = Path(..., description="ID zadania analizy PDF")
):
    """
    Zwraca rekomendacje reguł WCAG na podstawie wyników analizy PDF.
    
    Endpoint integruje się z istniejącą analizą i sugeruje,
    które reguły WCAG są najbardziej istotne dla danego dokumentu.
    """
    # Tu możesz pobrać wyniki analizy z Redis/Celery
    # Na potrzeby przykładu zakładam, że masz już wyniki
    
    analysis_results = {
        "is_tagged": False,
        "image_info": {"images_without_alt": 5}
    }
    
    recommendations = rules_service.get_rules_for_pdf_analysis(analysis_results)
    return recommendations