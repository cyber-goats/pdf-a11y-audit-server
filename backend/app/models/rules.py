from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RuleLevel(str, Enum):
    """Poziomy zgodności WCAG"""
    A = "A"
    AA = "AA" 
    AAA = "AAA"

class RuleCategory(str, Enum):
    """Kategorie zasad dostępności"""
    PERCEIVABLE = "perceivable"
    OPERABLE = "operable"
    UNDERSTANDABLE = "understandable"
    ROBUST = "robust"

class WCAGRule(BaseModel):
    """Model pojedynczej reguły WCAG/PDF-UA"""
    id: str = Field(..., description="Unikalny identyfikator reguły, np. 'wcag_1.1.1'")
    title: str = Field(..., description="Tytuł reguły")
    description: str = Field(..., description="Szczegółowy opis reguły")
    level: RuleLevel = Field(..., description="Poziom zgodności")
    category: RuleCategory = Field(..., description="Kategoria POUR")
    
    # Szczegóły techniczne
    techniques: List[str] = Field(default_factory=list, description="Techniki implementacji")
    failures: List[str] = Field(default_factory=list, description="Typowe błędy")
    
    # Kontekst PDF
    pdf_specific: bool = Field(False, description="Czy dotyczy specyficznie PDF")
    pdf_ua_mapping: Optional[str] = Field(None, description="Mapowanie na PDF/UA")
    
    # Przykłady i rekomendacje
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Metadane
    version: str = Field("2.1", description="Wersja WCAG")
    last_updated: Optional[str] = Field(None, description="Data ostatniej aktualizacji")
    references: List[str] = Field(default_factory=list, description="Linki referencyjne")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "wcag_1.1.1",
                "title": "Treść nietekstowa",
                "description": "Cała treść nietekstowa przedstawiona użytkownikowi...",
                "level": "A",
                "category": "perceivable",
                "pdf_specific": True,
                "pdf_ua_mapping": "7.1"
            }
        }

class RuleNotFoundError(Exception):
    """Wyjątek gdy reguła nie została znaleziona"""
    pass