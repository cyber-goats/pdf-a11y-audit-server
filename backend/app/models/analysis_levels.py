from enum import Enum
from typing import Dict, Any

class AnalysisLevel(str, Enum):
    """Poziomy szczegółowości analizy PDF"""
    QUICK = "quick"           # Szybki skan - podstawowe TAK/NIE
    STANDARD = "standard"     # Standardowa analiza z podsumowaniem  
    PROFESSIONAL = "professional"  # Pełny audyt z deep scan
    
    def get_config(self) -> Dict[str, Any]:
        """Zwraca konfigurację dla danego poziomu analizy"""
        configs = {
            AnalysisLevel.QUICK: {
                "name": "Szybki skan",
                "description": "Podstawowa weryfikacja dostępności (< 1s per PDF)",
                "estimated_time": 1,
                "includes": [
                    "Weryfikacja tagowania (TAK/NIE)",
                    "Obecność tekstu",
                    "Liczba stron",
                    "Podstawowa ocena dostępności"
                ],
                "skip_verapdf": True,  # Pomijamy czasochłonne sprawdzenie PDF/UA
                "deep_scan": False,
                "extract_text": False,  # Nie wyciągamy pełnego tekstu
                "max_pages_to_scan": 10  # Skanujemy max 10 stron
            },
            AnalysisLevel.STANDARD: {
                "name": "Analiza standardowa", 
                "description": "Szczegółowa analiza z rekomendacjami (5-10s)",
                "estimated_time": 10,
                "includes": [
                    "Wszystko z szybkiego skanu",
                    "Analiza struktury nagłówków",
                    "Weryfikacja alt-tekstów",
                    "Sprawdzenie metadanych",
                    "Podstawowe rekomendacje"
                ],
                "skip_verapdf": False,  # Sprawdzamy PDF/UA
                "deep_scan": False,
                "extract_text": True,  # Wyciągamy preview tekstu
                "max_pages_to_scan": 50
            },
            AnalysisLevel.PROFESSIONAL: {
                "name": "Audyt profesjonalny",
                "description": "Kompletny audyt zgodności WCAG/PDF-UA (30s+)",
                "estimated_time": 30,
                "includes": [
                    "Wszystko z analizy standardowej",
                    "Pełne skanowanie wszystkich tagów",
                    "Szczegółowa analiza każdej strony",
                    "Weryfikacja kontrastu kolorów",
                    "Analiza formularzy",
                    "Pełny raport PDF/UA",
                    "Szczegółowe rekomendacje WCAG"
                ],
                "skip_verapdf": False,
                "deep_scan": True,  # Głębokie skanowanie
                "extract_text": True,
                "max_pages_to_scan": None  # Brak limitu
            }
        }
        return configs.get(self, configs[AnalysisLevel.STANDARD])