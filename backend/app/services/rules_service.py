import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from app.models.rules import WCAGRule, RuleNotFoundError
from app.services.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)

class RulesService:
    """Serwis zarządzający bazą wiedzy WCAG/PDF-UA"""
    
    def __init__(self):
        self.rules_cache: Dict[str, WCAGRule] = {}
        self.data_path = Path(__file__).parent.parent / "data" / "wcag_rules.json"
        self._load_rules()
    
    def _load_rules(self) -> None:
        """Ładuje reguły z pliku JSON do pamięci"""
        try:
            if not self.data_path.exists():
                logger.warning(f"Brak pliku z regułami: {self.data_path}")
                self._create_sample_rules()
                return
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
                
            for rule_dict in rules_data.get('rules', []):
                rule = WCAGRule(**rule_dict)
                self.rules_cache[rule.id] = rule
                
            logger.info(f"Załadowano {len(self.rules_cache)} reguł WCAG/PDF-UA")
            
        except Exception as e:
            logger.error(f"Błąd ładowania reguł: {e}")
            self._create_sample_rules()
    
    def _create_sample_rules(self) -> None:
        """Tworzy przykładowe reguły dla demonstracji"""
        sample_rules = [
            WCAGRule(
                id="wcag_1.1.1",
                title="Treść nietekstowa",
                description="Cała treść nietekstowa przedstawiona użytkownikowi ma swoją tekstową alternatywę",
                level="A",
                category="perceivable",
                pdf_specific=True,
                pdf_ua_mapping="7.1",
                techniques=["PDF1", "PDF4"],
                failures=["F30", "F38"],
                recommendations=[
                    "Dodaj tekst alternatywny do wszystkich obrazów",
                    "Użyj atrybutu /Alt w tagach Figure"
                ],
                last_updated="2024-01-15"
            ),
            WCAGRule(
                id="wcag_1.3.1",
                title="Informacje i relacje",
                description="Informacje, struktura i relacje przekazywane przez prezentację mogą być określone programowo",
                level="A", 
                category="perceivable",
                pdf_specific=True,
                pdf_ua_mapping="7.2",
                techniques=["PDF6", "PDF9"],
                failures=["F2", "F33"],
                recommendations=[
                    "Użyj właściwych tagów struktury (H1-H6 dla nagłówków)",
                    "Oznacz listy tagami L, LI",
                    "Zachowaj logiczną kolejność czytania"
                ],
                last_updated="2024-01-15"
            )
        ]
        
        for rule in sample_rules:
            self.rules_cache[rule.id] = rule
    
    async def get_rule(self, rule_id: str) -> WCAGRule:
        """
        Pobiera pojedynczą regułę z cache lub Redis
        
        Args:
            rule_id: Identyfikator reguły (np. 'wcag_1.1.1')
            
        Returns:
            WCAGRule: Obiekt reguły
            
        Raises:
            RuleNotFoundError: Gdy reguła nie istnieje
        """
        # Najpierw sprawdź lokalny cache
        if rule_id in self.rules_cache:
            return self.rules_cache[rule_id]
        
        # Sprawdź Redis cache
        cache_key = f"rule:{rule_id}"
        cached_rule = redis_client.get_cache(cache_key)
        
        if cached_rule:
            logger.info(f"Pobrano regułę {rule_id} z Redis cache")
            return WCAGRule(**cached_rule)
        
        # Jeśli nie znaleziono
        raise RuleNotFoundError(f"Reguła o ID '{rule_id}' nie została znaleziona")
    
    async def get_all_rules(self, 
                           level: Optional[str] = None,
                           category: Optional[str] = None,
                           pdf_specific: Optional[bool] = None) -> List[WCAGRule]:
        """
        Pobiera wszystkie reguły z opcjonalnym filtrowaniem
        
        Args:
            level: Filtruj po poziomie (A, AA, AAA)
            category: Filtruj po kategorii POUR
            pdf_specific: Tylko reguły specyficzne dla PDF
            
        Returns:
            Lista reguł spełniających kryteria
        """
        rules = list(self.rules_cache.values())
        
        if level:
            rules = [r for r in rules if r.level == level]
        
        if category:
            rules = [r for r in rules if r.category == category]
            
        if pdf_specific is not None:
            rules = [r for r in rules if r.pdf_specific == pdf_specific]
        
        return rules
    
    async def search_rules(self, query: str) -> List[WCAGRule]:
        """
        Wyszukuje reguły po tekście
        
        Args:
            query: Tekst do wyszukania
            
        Returns:
            Lista pasujących reguł
        """
        query_lower = query.lower()
        results = []
        
        for rule in self.rules_cache.values():
            if (query_lower in rule.title.lower() or 
                query_lower in rule.description.lower() or
                query_lower in rule.id.lower()):
                results.append(rule)
        
        return results
    
    def get_rules_for_pdf_analysis(self, analysis_results: dict) -> List[Dict]:
        """
        Zwraca reguły relevantne dla wyników analizy PDF
        
        Args:
            analysis_results: Wyniki analizy z pdf_analyzer
            
        Returns:
            Lista rekomendowanych reguł z priorytetem
        """
        relevant_rules = []
        
        # Jeśli brak tagów - priorytet dla reguł struktury
        if not analysis_results.get('is_tagged'):
            rule = self.rules_cache.get('wcag_1.3.1')
            if rule:
                relevant_rules.append({
                    'rule': rule.dict(),
                    'priority': 'high',
                    'reason': 'Dokument nie posiada tagów struktury'
                })
        
        # Jeśli są obrazy bez alt tekstów
        image_info = analysis_results.get('image_info', {})
        if image_info.get('images_without_alt', 0) > 0:
            rule = self.rules_cache.get('wcag_1.1.1')
            if rule:
                relevant_rules.append({
                    'rule': rule.dict(),
                    'priority': 'high',
                    'reason': f"Znaleziono {image_info['images_without_alt']} obrazów bez tekstu alternatywnego"
                })
        
        return relevant_rules

# Singleton instance
rules_service = RulesService()