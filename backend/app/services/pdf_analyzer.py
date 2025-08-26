import pymupdf as fitz
import subprocess
import logging
from typing import Tuple, List, Dict
import xml.etree.ElementTree as ET

from app.common.exceptions import CorruptPDFError, PasswordProtectedPDFError, PDFAnalysisError
from app.services.redis_client import redis_client


def is_pdf_tagged(doc: fitz.Document) -> bool:
    """Sprawdza, czy dokument PDF jest otagowany."""
    try:
        catalog_xref = doc.pdf_catalog()
        if doc.xref_get_key(catalog_xref, "StructTreeRoot")[1] != "null":
            return True
    except Exception:
        return False
    return False

def find_all_alts_recursively(element, found_alts):
    """
    Funkcja rekursywna do znalezienia WSZYSTKICH kluczy 'alt' w drzewie.
    """
    if isinstance(element, dict):
        if "alt" in element and element["alt"]:
            found_alts.append(element["alt"])
        
        if "kids" in element and isinstance(element["kids"], list):
            for kid in element["kids"]:
                find_all_alts_recursively(kid, found_alts)

def get_image_alts(doc: fitz.Document) -> dict:
    """
    Analizuje tagi struktury w poszukiwaniu obrazów i tekstów alternatywnych.
    """
    image_analysis = {
        "image_count": 0, "images_with_alt": 0,
        "images_without_alt": 0, "alt_texts": []
    }
    
    # Zliczamy wszystkie obrazy
    for page in doc:
        image_analysis["image_count"] += len(page.get_images(full=True))
        
    if not is_pdf_tagged(doc):
        image_analysis["images_without_alt"] = image_analysis["image_count"]
        return image_analysis

    # Alternatywne podejście - sprawdzamy metadane obrazów
    try:
        all_alt_texts = []
        
        # Próbujemy różne metody dostępu do struktury
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Sprawdzamy obrazy na stronie
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                try:
                    # Próbujemy pobrać xref obrazu
                    xref = img[0]
                    
                    # Sprawdzamy czy obraz ma alt text w metadanych
                    img_dict = doc.xref_object(xref)
                    if "/Alt" in img_dict:
                        alt_text = img_dict["/Alt"]
                        if isinstance(alt_text, str) and alt_text.strip():
                            all_alt_texts.append(alt_text)
                except:
                    continue
        
        # Alternatywna metoda - sprawdzamy marked content
        try:
            for page in doc:
                # Pobieramy tekst z tagami
                blocks = page.get_text("dict")
                for block in blocks.get("blocks", []):
                    if block.get("type") == 1:  # Image block
                        # Sprawdzamy czy jest alt text
                        if "alt" in block:
                            all_alt_texts.append(block["alt"])
        except:
            pass
        
        image_analysis["alt_texts"] = all_alt_texts
        image_analysis["images_with_alt"] = len(all_alt_texts)
        image_analysis["images_without_alt"] = max(0, image_analysis["image_count"] - len(all_alt_texts))

    except Exception as e:
        print(f"Nie można analizować alt tekstów: {e}")
        # Jeśli nie możemy analizować, zakładamy że brak alt tekstów
        image_analysis["images_without_alt"] = image_analysis["image_count"]

    return image_analysis

def analyze_pdf(file_bytes: bytes) -> dict:
    """Główna funkcja analityczna z inteligentnym cache."""
    
    # Sprawdź rozmiar pliku
    file_size = len(file_bytes)
    logger.info(f"Starting PDF analysis for file of size: {file_size} bytes")
    
    # Cache logic z pełną obsługą błędów
    cached_result = None
    cache_key = None
    should_cache = redis_client.should_cache_file(file_size)
    
    if should_cache:
        try:
            cache_key = redis_client.generate_file_key(file_bytes)
            cached_result = redis_client.get_cache(cache_key)
            
            if cached_result:
                logger.info(f"Returning cached result for {cache_key}")
                # Dodaj informację o cache do wyniku
                cached_result['_cache_info'] = {
                    'from_cache': True,
                    'cache_key': cache_key
                }
                return cached_result
                
        except Exception as e:
            logger.warning(f"Redis cache read failed, proceeding without cache: {e}")
            cache_key = None
    else:
        logger.info(f"File too large ({file_size} bytes) for caching, proceeding without cache")

    try:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        
        # Sprawdzenie, czy plik jest chroniony hasłem
        if pdf_document.is_encrypted:
            pdf_document.close()
            raise PasswordProtectedPDFError()

        page_count = pdf_document.page_count
        
        # Sprawdzenie, czy dokument ma strony (prosta walidacja)
        if page_count == 0:
            pdf_document.close()
            raise CorruptPDFError("Plik PDF nie zawiera żadnych stron.")

        logger.info(f"Analyzing PDF with {page_count} pages")
        
        tagged = is_pdf_tagged(pdf_document)
        image_info = get_image_alts(pdf_document)
        
        full_text = ""
        for page in pdf_document:
            full_text += page.get_text() + "\n--- Page Break ---\n"
            
        pdf_document.close()
        
        contains_text = len(full_text.strip()) > 0
        
        analysis_result = {
            "page_count": page_count, 
            "is_tagged": tagged,
            "contains_text": contains_text, 
            "image_info": image_info,
            "extracted_text_preview": full_text[:500] + "..." if len(full_text) > 500 else full_text,
            "_cache_info": {
                'from_cache': False,
                'cache_key': cache_key,
                'cacheable': should_cache
            }
        }

        # Zapisz do cache - ale tylko jeśli można i powinno się
        if should_cache and cache_key:
            try:
                cache_success = redis_client.set_cache(cache_key, analysis_result, 3600)
                if cache_success:
                    logger.info(f"Successfully cached analysis result for {cache_key}")
                else:
                    logger.warning(f"Failed to cache analysis result for {cache_key}")
            except Exception as e:
                logger.warning(f"Redis cache write failed, but analysis completed: {e}")
        
        logger.info("PDF analysis completed successfully")
        return analysis_result
        
    except fitz.errors.FzError as e:
        logger.error(f"Błąd PyMuPDF podczas analizy: {e}")
        raise CorruptPDFError()
    except PDFAnalysisError:
        # Przekaż nasze własne wyjątki dalej bez zmian
        raise
    except Exception as e:
        logger.error(f"Error during PDF analysis: {e}")
        raise PDFAnalysisError(f"Wystąpił nieoczekiwany błąd serwera: {e}", "ERR_UNKNOWN")  
    
# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Nazwa kontenera zdefiniowana w docker-compose.yml
VERAPDF_CONTAINER_NAME = "verapdf_service"

def validate_pdf_ua(pdf_filename: str) -> Tuple[bool, str]:
    """
    Uruchamia walidację pliku PDF pod kątem zgodności z PDF/UA (WCAG).
    """
    shared_path = f"/tmp/pdfs/{pdf_filename}"
    logger.info(f"Rozpoczynanie walidacji PDF/UA dla pliku: {shared_path}")

    command = [
        "docker", "exec", VERAPDF_CONTAINER_NAME,
        "/opt/verapdf/verapdf",
        "--format", "xml",
        "--flavour", "2b",
        shared_path
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False 
        )

        if result.returncode > 1:
            error_message = f"Błąd wykonania veraPDF. Kod: {result.returncode}. stderr: {result.stderr}"
            logger.error(error_message)
            return False, f"<error>{error_message}</error>"

        is_compliant = result.returncode == 0
        status = "ZGODNY" if is_compliant else "NIEZGODNY"
        logger.info(f"Walidacja zakończona. Status: {status}")

        report_output = result.stdout if result.stdout else result.stderr
        return is_compliant, report_output

    except FileNotFoundError:
        error_message = "Polecenie 'docker' nie zostało znalezione w kontenerze backendu."
        logger.critical(error_message)
        return False, f"<error>{error_message}</error>"
    except Exception as e:
        error_message = f"Niespodziewany błąd podczas walidacji: {e}"
        logger.error(error_message)
        return False, f"<error>{error_message}</error>"
    
def parse_verapdf_report(xml_report: str) -> List[Dict]:
    """
    Parsuje raport XML z veraPDF i wyciąga listę błędów.

    Args:
        xml_report: Raport z walidacji w formacie XML jako string.

    Returns:
        Lista słowników, gdzie każdy słownik reprezentuje jeden błąd.
    """
    failed_rules = []
    try:
        # Usuwamy przestrzeń nazw, jeśli istnieje, dla uproszczenia
        xml_report = xml_report.replace('xmlns="http://www.verapdf.org/ValidationProfile"', '')
        root = ET.fromstring(xml_report)

        # Szukamy wszystkich reguł, które nie przeszły walidacji
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
        # Zdarza się, gdy veraPDF zwróci błąd zamiast XML
        return [{"error": "Failed to parse veraPDF XML report."}]
    except Exception as e:
        return [{"error": f"An unexpected error occurred during XML parsing: {str(e)}"}]