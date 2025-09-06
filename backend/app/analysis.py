import pymupdf as fitz
import subprocess
import logging
from typing import Tuple, List, Dict
import xml.etree.ElementTree as ET

from app.common.exceptions import CorruptPDFError, PasswordProtectedPDFError, PDFAnalysisError

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VERAPDF_CONTAINER_NAME = "verapdf_service"

class PdfAnalysis:
    """
    Główna klasa aranżująca proces analizy dostępności pliku PDF.
    """

    def __init__(self, file_bytes: bytes):
        """
        Inicjalizuje analizę, otwierając dokument PDF.
        """
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


    def run_basic_analysis(self) -> Dict:
        """
        Przeprowadza podstawową analizę właściwości dokumentu.
        """
        logger.info(f"Uruchamianie podstawowej analizy dla PDF z {self.doc.page_count} stronami.")
        
        tagged = self._is_tagged()
        image_info = self._get_image_alts()
        metadata_info = self._get_document_metadata()
        
        full_text = ""
        for page in self.doc:
            full_text += page.get_text()

        contains_text = len(full_text.strip()) > 0
        
        return {
            "page_count": self.doc.page_count,
            "is_tagged": tagged,
            "contains_text": contains_text,
            "image_info": image_info,
            **metadata_info,
            "extracted_text_preview": (full_text[:500] + "...") if len(full_text) > 500 else full_text,
        }

    def _is_tagged(self) -> bool:
        """Sprawdza, czy dokument PDF jest otagowany."""
        try:
            catalog_xref = self.doc.pdf_catalog()
            if self.doc.xref_get_key(catalog_xref, "StructTreeRoot")[1] != "null":
                return True
        except Exception:
            return False
        return False
    
    def _get_document_metadata(self) -> dict:
        """Pobiera i weryfikuje metadane dokumentu (tytuł, język)."""
        metadata = self.doc.metadata
        title = metadata.get('title', '')
        
        # Język jest często w katalogu głównym dokumentu
        lang = ''
        try:
            # PyMuPDF zwraca krotkę (typ, wartość), np. ('string', 'pl-PL')
            lang_info = self.doc.pdf_catalog_get_key("Lang")
            if lang_info and lang_info[0] == 'string':
                lang = lang_info[1]
        except Exception:
            lang = '' # Jeśli nie można odczytać, traktujemy jako brak
            
        return {
            "title": title,
            "is_title_defined": bool(title and title.strip()),
            "language": lang,
            "is_lang_defined": bool(lang and lang.strip())
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
    

    def close(self):
        """Zamyka dokument PDF, jeśli jest otwarty."""
        if hasattr(self, 'doc') and self.doc:
            self.doc.close()
            logger.info("Dokument PDF został zamknięty.")


def validate_pdf_ua(pdf_filename: str) -> Tuple[bool, str]:
    """
    Uruchamia walidację pliku PDF pod kątem zgodności z PDF/UA przy użyciu veraPDF w Dockerze.
    """
    shared_path = f"/tmp/pdfs/{pdf_filename}"
    logger.info(f"Rozpoczynanie walidacji PDF/UA dla pliku: {shared_path}")

    command = [
        "docker", "exec", VERAPDF_CONTAINER_NAME,
        "/opt/verapdf/verapdf",
        "--format", "xml",
        "--flavour", "ua1",
        shared_path
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        if result.returncode > 1:
            error_message = f"Błąd wykonania veraPDF. Kod: {result.returncode}. stderr: {result.stderr}"
            logger.error(error_message)
            raise PDFAnalysisError(error_message)

        is_compliant = result.returncode == 0
        status = "ZGODNY" if is_compliant else "NIEZGODNY"
        logger.info(f"Walidacja zakończona. Status: {status}")

        report_output = result.stdout if result.stdout else result.stderr
        return is_compliant, report_output

    except FileNotFoundError:
        error_message = "Polecenie 'docker' nie zostało znalezione."
        logger.critical(error_message)
        raise PDFAnalysisError(error_message)
    except Exception as e:
        error_message = f"Niespodziewany błąd podczas walidacji veraPDF: {e}"
        logger.error(error_message)
        raise PDFAnalysisError(error_message)

def parse_verapdf_report(xml_report: str) -> List[Dict]:
    """
    Parsuje raport XML z veraPDF i wyciąga listę błędów.
    """
    failed_rules = []
    try:
        # Usuwa przestrzeń nazw dla uproszczenia
        xml_report = xml_report.replace('xmlns="http://www.verapdf.org/ValidationProfile"', '')
        root = ET.fromstring(xml_report)

        for rule in root.findall('.//rule[@status="failed"]'):
            error = {
                "specification": rule.get("specification"),
                "clause": rule.get("clause"),
                "testNumber": rule.get("testNumber"),
                "description": rule.find("description").text if rule.find("description") is not None else "No description"
            }
            failed_rules.append(error)
        
        return failed_rules

    except ET.ParseError:
        logger.warning("Nie udało się sparsować raportu XML z veraPDF.")
        return [{"error": "Nie udało się sparsować raportu XML z veraPDF."}]
    except Exception as e:
        logger.error(f"Niespodziewany błąd podczas parsowania XML: {e}")
        return [{"error": f"Niespodziewany błąd podczas parsowania XML: {str(e)}"}]