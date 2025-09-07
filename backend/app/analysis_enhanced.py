import logging
from typing import Dict, Any
import time
from app.models.analysis_levels import AnalysisLevel
from app.analysis import PdfAnalysis

logger = logging.getLogger(__name__)

class EnhancedPdfAnalysis(PdfAnalysis):
    """
    Rozszerzona klasa analizy PDF z obsługą poziomów szczegółowości.
    Dziedziczy po PdfAnalysis, aby uniknąć duplikacji kodu.
    """
    
    def analyze(self, level: AnalysisLevel = AnalysisLevel.STANDARD) -> Dict[str, Any]:
        """
        Główna metoda analizy z obsługą poziomów
        """
        start_time = time.time()
        config = level.get_config()
        
        logger.info(f"Rozpoczynanie analizy PDF - poziom: {level.value}")
        logger.info(f"Konfiguracja: {config['name']}")
        
        # Podstawowe informacje (dla wszystkich poziomów)
        results = {
            "analysis_level": level.value,
            "analysis_config": config,
            "page_count": min(self.doc.page_count, config['max_pages_to_scan'] or self.doc.page_count),
            "total_pages": self.doc.page_count,
            "is_tagged": self._is_tagged(),
            "contains_text": self._check_text_presence(config['max_pages_to_scan']),
        }
        
        # QUICK - tylko podstawy
        if level == AnalysisLevel.QUICK:
            results.update(self._quick_analysis())
            
        # STANDARD - dodajemy szczegóły
        elif level == AnalysisLevel.STANDARD:
            results.update(self._quick_analysis())
            results.update(self._standard_analysis())
            
        # PROFESSIONAL - pełna analiza
        elif level == AnalysisLevel.PROFESSIONAL:
            results.update(self._quick_analysis())
            results.update(self._standard_analysis())
            results.update(self._professional_analysis())
        
        # Czas analizy
        results["analysis_time"] = round(time.time() - start_time, 2)
        logger.info(f"Analiza zakończona w {results['analysis_time']}s")
        
        return results
    
    def _quick_analysis(self) -> Dict[str, Any]:
        """Szybka analiza - podstawowe metryki"""
        return {
            "quick_metrics": {
                "has_images": self._count_images() > 0,
                "image_count": self._count_images(),
                "is_scanned_pdf": self._is_scanned_pdf(),
                "file_size_ok": self.doc.page_count < 100,  # Prosty check
            }
        }
    
    def _standard_analysis(self) -> Dict[str, Any]:
        """Standardowa analiza - więcej szczegółów"""
        results = {}
        
        # Metadane - używamy rozszerzonej wersji
        metadata = self._get_extended_metadata()
        results["metadata"] = metadata
        results["is_title_defined"] = metadata.get("is_title_defined", False)
        results["is_lang_defined"] = metadata.get("is_lang_defined", False)
        
        # Obrazy i alt-teksty - używamy metody z klasy bazowej
        if self._count_images() > 0:
            results["image_info"] = self._get_image_alts()
        
        # Nagłówki - używamy metody z klasy bazowej
        if self._is_tagged():
            results["heading_info"] = self._analyze_headings()
        
        # Preview tekstu
        results["text_preview"] = self._extract_text_preview(max_chars=500)
        
        return results
    
    def _professional_analysis(self) -> Dict[str, Any]:
        """Profesjonalna analiza - deep scan"""
        results = {
            "deep_scan": {}
        }
        
        # Szczegółowa analiza tagowania
        if self._is_tagged():
            results["deep_scan"]["tagging_details"] = self._get_tagging_details()
        
        # Analiza każdej strony
        results["deep_scan"]["page_analysis"] = self._analyze_all_pages()
        
        # Analiza formularzy
        results["deep_scan"]["forms"] = self._analyze_forms()
        
        # Analiza tabel
        results["deep_scan"]["tables"] = self._analyze_tables()
        
        # Analiza linków
        results["deep_scan"]["links"] = self._analyze_links()
        
        # Ocena kontrastu (jeśli są obrazy)
        if self._count_images() > 0:
            results["deep_scan"]["contrast_issues"] = self._check_contrast()
        
        return results
    
    # ===== METODY POMOCNICZE UNIKALNE DLA ENHANCED =====
    
    def _check_text_presence(self, max_pages: int = None) -> bool:
        """Sprawdza obecność tekstu"""
        pages_to_check = min(self.doc.page_count, max_pages or self.doc.page_count)
        for i in range(pages_to_check):
            if self.doc[i].get_text().strip():
                return True
        return False
    
    def _count_images(self) -> int:
        """Liczy obrazy w dokumencie"""
        count = 0
        for page in self.doc:
            count += len(page.get_images(full=True))
        return count
    
    def _is_scanned_pdf(self) -> bool:
        """Sprawdza czy to zeskanowany PDF (tylko obrazy bez tekstu)"""
        has_images = self._count_images() > 0
        has_text = self._check_text_presence(max_pages=3)  # Sprawdź pierwsze 3 strony
        return has_images and not has_text
    
    def _extract_text_preview(self, max_chars: int = 500) -> str:
        """Wyciąga preview tekstu"""
        text = ""
        for page in self.doc:
            text += page.get_text()
            if len(text) > max_chars:
                return text[:max_chars] + "..."
        return text
    
    def _get_extended_metadata(self) -> dict:
        """
        Rozszerzone metadane - używa metody bazowej i dodaje więcej informacji.
        """
        # Pobierz podstawowe metadane z klasy bazowej
        basic_metadata = self._get_document_metadata()
        
        # Dodaj rozszerzone informacje
        metadata = self.doc.metadata
        basic_metadata.update({
            "author": metadata.get('author', ''),
            "subject": metadata.get('subject', ''),
            "keywords": metadata.get('keywords', ''),
            "creator": metadata.get('creator', ''),
            "producer": metadata.get('producer', ''),
            "creation_date": str(metadata.get('creationDate', '')),
            "modification_date": str(metadata.get('modDate', ''))
        })
        
        return basic_metadata
    
    def _get_tagging_details(self) -> Dict:
        """Szczegółowa analiza tagowania (PROFESSIONAL)"""
        details = {
            "total_tags": 0,
            "tag_types": {},
            "structure_quality": 0,
            "has_role_map": False,
            "has_artifacts": False,
            "reading_order_defined": False
        }
        
        try:
            # Sprawdź RoleMap
            catalog_xref = self.doc.pdf_catalog()
            role_map = self.doc.xref_get_key(catalog_xref, "RoleMap")
            details["has_role_map"] = role_map[1] != "null"
            
            # Policz i kategoryzuj tagi
            tag_counts = {}
            for xref in range(1, min(self.doc.xref_length(), 1000)):
                try:
                    obj_str = self.doc.xref_object(xref, compressed=False)
                    if obj_str:
                        for tag in ['P', 'H1', 'H2', 'H3', 'Figure', 'Table', 'List']:
                            if f"/{tag}" in obj_str or f"<{tag}" in obj_str:
                                tag_counts[tag] = tag_counts.get(tag, 0) + 1
                                details["total_tags"] += 1
                except:
                    continue
            
            details["tag_types"] = tag_counts
            
            # Ocena jakości struktury (0-100)
            quality = 0
            if details["total_tags"] > 0:
                quality += 20
            if details["has_role_map"]:
                quality += 10
            if "H1" in tag_counts:
                quality += 20
            if "Figure" in tag_counts:
                quality += 15
            if "Table" in tag_counts:
                quality += 15
            if len(tag_counts) >= 4:
                quality += 20
            
            details["structure_quality"] = min(quality, 100)
            
        except Exception as e:
            logger.error(f"Błąd w deep scan tagowania: {e}")
        
        return details
    
    def _analyze_all_pages(self) -> list:
        """Analizuje każdą stronę osobno (PROFESSIONAL)"""
        pages_analysis = []
        
        for i, page in enumerate(self.doc):
            if i >= 10:  # Limit dla demo - analizuj max 10 stron
                break
                
            page_info = {
                "page_number": i + 1,
                "has_text": bool(page.get_text().strip()),
                "image_count": len(page.get_images()),
                "link_count": len(page.get_links()),
                "annotation_count": len(page.annots()),
                "rotation": page.rotation,
                "mediabox": list(page.mediabox)
            }
            pages_analysis.append(page_info)
        
        return pages_analysis
    
    def _analyze_forms(self) -> Dict:
        """Analizuje formularze w PDF (PROFESSIONAL)"""
        forms = {
            "has_forms": False,
            "field_count": 0,
            "field_types": {},
            "unlabeled_fields": 0,
            "issues": []
        }
        
        try:
            # Sprawdź czy są formularze
            for page in self.doc:
                widgets = page.widgets()
                if widgets:
                    forms["has_forms"] = True
                    for widget in widgets:
                        forms["field_count"] += 1
                        field_type = widget.field_type_string
                        forms["field_types"][field_type] = forms["field_types"].get(field_type, 0) + 1
                        
                        # Sprawdź czy pole ma etykietę
                        if not widget.field_label:
                            forms["unlabeled_fields"] += 1
            
            if forms["unlabeled_fields"] > 0:
                forms["issues"].append(f"{forms['unlabeled_fields']} pól formularza bez etykiet")
                
        except Exception as e:
            logger.error(f"Błąd analizy formularzy: {e}")
        
        return forms
    
    def _analyze_tables(self) -> Dict:
        """Analizuje tabele w PDF (PROFESSIONAL)"""
        return {
            "table_count": 0,  # Wymaga głębszej analizy tagów
            "tables_with_headers": 0,
            "issues": []
        }
    
    def _analyze_links(self) -> Dict:
        """Analizuje linki w PDF (PROFESSIONAL)"""
        links = {
            "total_links": 0,
            "internal_links": 0,
            "external_links": 0,
            "email_links": 0,
            "broken_links": []
        }
        
        for page in self.doc:
            for link in page.get_links():
                links["total_links"] += 1
                if link.get("uri", "").startswith("http"):
                    links["external_links"] += 1
                elif link.get("uri", "").startswith("mailto:"):
                    links["email_links"] += 1
                else:
                    links["internal_links"] += 1
        
        return links
    
    def _check_contrast(self) -> list:
        """Sprawdza potencjalne problemy z kontrastem (PROFESSIONAL)"""
        # To wymagałoby analizy obrazów - placeholder
        return []