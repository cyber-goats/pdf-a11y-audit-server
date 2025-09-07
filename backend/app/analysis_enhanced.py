import pymupdf as fitz
import logging
from typing import Dict, Any
import time
from app.models.analysis_levels import AnalysisLevel
from app.common.exceptions import CorruptPDFError, PasswordProtectedPDFError

logger = logging.getLogger(__name__)

class EnhancedPdfAnalysis:
    """
    Rozszerzona klasa analizy PDF z obsługą poziomów szczegółowości
    """
    
    def __init__(self, file_bytes: bytes):
        """Inicjalizuje analizę, otwierając dokument PDF."""
        try:
            self.doc = fitz.open(stream=file_bytes, filetype="pdf")
            if self.doc.is_encrypted:
                raise PasswordProtectedPDFError()
            if self.doc.page_count == 0:
                raise CorruptPDFError("Plik PDF nie zawiera żadnych stron.")
        except fitz.errors.FzError as e:
            logger.error(f"Błąd PyMuPDF podczas otwierania pliku: {e}")
            raise CorruptPDFError()
        except (PasswordProtectedPDFError, CorruptPDFError) as e:
            self.close()
            raise e
    
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
        
        # Metadane
        metadata = self._get_document_metadata()
        results["metadata"] = metadata
        results["is_title_defined"] = metadata.get("is_title_defined", False)
        results["is_lang_defined"] = metadata.get("is_lang_defined", False)
        
        # Obrazy i alt-teksty
        if self._count_images() > 0:
            results["image_info"] = self._get_image_alts()
        
        # Nagłówki
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
    
    def _is_tagged(self) -> bool:
        """Sprawdza czy PDF jest otagowany"""
        try:
            catalog_xref = self.doc.pdf_catalog()
            if self.doc.xref_get_key(catalog_xref, "StructTreeRoot")[1] != "null":
                return True
        except Exception:
            return False
        return False
    
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
    
    def _get_document_metadata(self) -> dict:
        """Pobiera metadane dokumentu"""
        metadata = self.doc.metadata
        title = metadata.get('title', '')
        
        lang = ''
        try:
            lang_info = self.doc.pdf_catalog_get_key("Lang")
            if lang_info and lang_info[0] == 'string':
                lang = lang_info[1]
        except Exception:
            lang = ''
            
        return {
            "title": title,
            "is_title_defined": bool(title and title.strip()),
            "language": lang,
            "is_lang_defined": bool(lang and lang.strip()),
            "author": metadata.get('author', ''),
            "subject": metadata.get('subject', ''),
            "keywords": metadata.get('keywords', ''),
            "creator": metadata.get('creator', ''),
            "producer": metadata.get('producer', ''),
            "creation_date": str(metadata.get('creationDate', '')),
            "modification_date": str(metadata.get('modDate', ''))
        }
    
    def _get_image_alts(self) -> Dict:
        """
        Analizuje dokument w poszukiwaniu obrazków i ich tekstów alternatywnych.
        Obsługuje alt-teksty w formacie hex UTF-16 rozłożone na wiele linii.
        """
        image_analysis = {
            "image_count": 0,
            "images_with_alt": 0,
            "images_without_alt": 0,
            "alt_texts": []
        }
        all_alt_texts = set()
        
        # Zlicz wszystkie obrazki
        for page in self.doc:
            image_list = page.get_images(full=True)
            image_analysis["image_count"] += len(image_list)
        
        # Przeszukaj wszystkie obiekty w PDF szukając /Alt
        for xref in range(1, self.doc.xref_length()):
            try:
                # Pobierz obiekt jako string
                obj_str = self.doc.xref_object(xref, compressed=False)
                
                if obj_str and "/Alt" in obj_str:
                    alt_text = None
                    
                    # Sprawdź czy to hex string (najczęstsze w PDF)
                    if "/Alt <" in obj_str or "/Alt<" in obj_str:
                        # Znajdź początek hex stringa
                        if "/Alt <" in obj_str:
                            start = obj_str.find("/Alt <") + 6
                        else:
                            start = obj_str.find("/Alt<") + 5
                        
                        # Zbierz wszystkie znaki hex aż do '>'
                        hex_chars = []
                        i = start
                        while i < len(obj_str):
                            char = obj_str[i]
                            if char == '>':
                                break
                            elif char in '0123456789ABCDEFabcdef':
                                hex_chars.append(char)
                            # Ignoruj białe znaki (spacje, nowe linie)
                            i += 1
                        
                        hex_text = ''.join(hex_chars)
                        
                        if hex_text:
                            try:
                                # Dekoduj hex do bajtów, potem do tekstu
                                if hex_text.upper().startswith('FEFF'):
                                    # UTF-16 BE z BOM
                                    alt_text = bytes.fromhex(hex_text).decode('utf-16-be')
                                elif hex_text.upper().startswith('FFFE'):
                                    # UTF-16 LE z BOM
                                    alt_text = bytes.fromhex(hex_text).decode('utf-16-le')
                                else:
                                    # Spróbuj UTF-16 BE (domyślne dla PDF)
                                    alt_text = bytes.fromhex(hex_text).decode('utf-16-be')
                            except Exception as e:
                                logger.debug(f"Błąd dekodowania hex w xref {xref}: {e}")
                    
                    # Alternatywna metoda: string w nawiasach
                    elif "/Alt(" in obj_str:
                        start = obj_str.find("/Alt(") + 5
                        # Znajdź pasujący nawias zamykający
                        depth = 1
                        i = start
                        text_chars = []
                        while i < len(obj_str) and depth > 0:
                            if obj_str[i:i+2] == '\\(':
                                text_chars.append('(')
                                i += 2
                            elif obj_str[i:i+2] == '\\)':
                                text_chars.append(')')
                                i += 2
                            elif obj_str[i:i+2] == '\\n':
                                text_chars.append(' ')
                                i += 2
                            elif obj_str[i:i+2] == '\\r':
                                text_chars.append(' ')
                                i += 2
                            elif obj_str[i] == '(':
                                depth += 1
                                text_chars.append(obj_str[i])
                                i += 1
                            elif obj_str[i] == ')':
                                depth -= 1
                                if depth > 0:
                                    text_chars.append(obj_str[i])
                                i += 1
                            else:
                                text_chars.append(obj_str[i])
                                i += 1
                        
                        alt_text = ''.join(text_chars)
                    
                    # Jeśli znaleźliśmy tekst, dodaj go do zbioru
                    if alt_text:
                        # Oczyść tekst
                        alt_text = alt_text.replace('\ufeff', '')  # Usuń BOM
                        alt_text = alt_text.strip()
                        
                        if len(alt_text) > 5:  # Ignoruj bardzo krótkie teksty
                            all_alt_texts.add(alt_text)
                            logger.info(f"Znaleziono alt-tekst w xref {xref}: {alt_text[:50]}...")
                            
            except Exception as e:
                logger.debug(f"Błąd przy przetwarzaniu xref {xref}: {e}")
                continue
        
        # Podsumowanie
        image_analysis["alt_texts"] = list(all_alt_texts)
        image_analysis["images_with_alt"] = min(len(all_alt_texts), image_analysis["image_count"])
        image_analysis["images_without_alt"] = max(0, 
            image_analysis["image_count"] - image_analysis["images_with_alt"])
        
        logger.info(f"Analiza obrazków: znaleziono {image_analysis['image_count']} obrazków, "
                    f"{len(all_alt_texts)} alt-tekstów")
        
        return image_analysis
    
    def _analyze_headings(self) -> Dict:
        """
        Analizuje hierarchię nagłówków w dokumencie PDF.
        Używa podobnego podejścia jak przy alt-tekstach - przeszukuje surowe obiekty.
        """
        analysis = {
            "h1_count": 0,
            "has_single_h1": False,
            "has_skipped_levels": False,
            "heading_structure": [],  # Lista poziomów w kolejności: [1, 2, 2, 3, 2, ...]
            "issues": []
        }
        
        if not self._is_tagged():
            analysis["issues"].append("Dokument nie jest otagowany - brak struktury nagłówków")
            return analysis
        
        try:
            # Zbierz wszystkie nagłówki przeszukując obiekty PDF
            headings_found = []
            
            # Przeszukaj obiekty PDF szukając tagów nagłówków
            for xref in range(1, min(self.doc.xref_length(), 2000)):  # Limit dla wydajności
                try:
                    obj_str = self.doc.xref_object(xref, compressed=False)
                    if obj_str:
                        # Szukaj tagów H1-H6 w różnych formatach
                        # Format 1: /H1, /H2, etc.
                        for level in range(1, 7):
                            patterns = [
                                f"/H{level} ",
                                f"/H{level}\n",
                                f"/H{level}<<",
                                f"/H{level}/",
                                f"/H{level}>>",
                                f"<H{level}>",
                                f"<H{level} "
                            ]
                            
                            for pattern in patterns:
                                if pattern in obj_str:
                                    headings_found.append(level)
                                    if level == 1:
                                        analysis["h1_count"] += 1
                                    logger.debug(f"Znaleziono nagłówek H{level} w xref {xref}")
                                    break
                                
                except Exception as e:
                    logger.debug(f"Błąd przy przetwarzaniu xref {xref}: {e}")
                    continue
            
            # Alternatywna metoda: sprawdź StructTreeRoot jeśli istnieje
            try:
                catalog_xref = self.doc.pdf_catalog()
                struct_tree = self.doc.xref_get_key(catalog_xref, "StructTreeRoot")
                
                if struct_tree[0] == "xref":
                    struct_tree_xref = int(struct_tree[1].split()[0])
                    struct_obj_str = self.doc.xref_object(struct_tree_xref, compressed=False)
                    
                    # Szukaj nagłówków w drzewie struktury
                    if struct_obj_str:
                        for level in range(1, 7):
                            count = struct_obj_str.count(f"/H{level}")
                            for _ in range(count):
                                headings_found.append(level)
                                if level == 1:
                                    analysis["h1_count"] += 1
                                    
            except Exception as e:
                logger.debug(f"Nie udało się przeanalizować StructTreeRoot: {e}")
            
            # Analiza wyników
            if headings_found:
                analysis["heading_structure"] = sorted(headings_found)
                analysis["has_single_h1"] = analysis["h1_count"] == 1
                
                # Sprawdź czy nie ma pominiętych poziomów
                unique_levels = sorted(set(headings_found))
                for i in range(len(unique_levels) - 1):
                    if unique_levels[i+1] - unique_levels[i] > 1:
                        analysis["has_skipped_levels"] = True
                        analysis["issues"].append(
                            f"Pominięty poziom: H{unique_levels[i]} → H{unique_levels[i+1]}"
                        )
                
                # Dodatkowe sprawdzenia
                if analysis["h1_count"] == 0:
                    analysis["issues"].append("Brak nagłówka H1")
                elif analysis["h1_count"] > 1:
                    analysis["issues"].append(f"Za dużo nagłówków H1: {analysis['h1_count']}")
                    
            else:
                analysis["issues"].append("Nie znaleziono żadnych nagłówków w dokumencie")
                
        except Exception as e:
            logger.warning(f"Błąd podczas analizy hierarchii nagłówków: {e}")
            analysis["issues"].append(f"Błąd analizy: {str(e)}")
        
        return analysis
    
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
    
    def close(self):
        """Zamyka dokument PDF"""
        if hasattr(self, 'doc') and self.doc:
            self.doc.close()
            logger.info("Dokument PDF został zamknięty.")