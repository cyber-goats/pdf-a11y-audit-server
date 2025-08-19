import pymupdf as fitz
import subprocess
import logging
from typing import Tuple
import xml.etree.ElementTree as ET
from typing import List, Dict

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
    
    for page in doc:
        image_analysis["image_count"] += len(page.get_images(full=True))
        
    if not is_pdf_tagged(doc):
        image_analysis["images_without_alt"] = image_analysis["image_count"]
        return image_analysis

    try:
        # PRAWIDŁOWA NAZWA FUNKCJI
        struct_tree = doc.structure_csirt()
        all_alt_texts = []
        
        for element in struct_tree:
            find_all_alts_recursively(element, all_alt_texts)
        
        image_analysis["alt_texts"] = all_alt_texts
        image_analysis["images_with_alt"] = len(all_alt_texts)
        image_analysis["images_without_alt"] = image_analysis["image_count"] - len(all_alt_texts)

    except Exception as e:
        print(f"BŁĄD KRYTYCZNY: {e}")
        image_analysis["images_without_alt"] = image_analysis["image_count"]

    return image_analysis

def analyze_pdf(file_bytes: bytes) -> dict:
    """Główna funkcja analityczna."""
    try:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        
        page_count = pdf_document.page_count
        tagged = is_pdf_tagged(pdf_document)
        image_info = get_image_alts(pdf_document)
        
        full_text = ""
        for page in pdf_document:
            full_text += page.get_text() + "\n--- Page Break ---\n"
            
        pdf_document.close()
        
        contains_text = len(full_text.strip()) > 0
        
        analysis_result = {
            "page_count": page_count, "is_tagged": tagged,
            "contains_text": contains_text, "image_info": image_info,
            "extracted_text_preview": full_text[:500] + "..."
        }
        
        return analysis_result
        
    except Exception as e:
        print(f"Error during PDF analysis: {e}")
        return None
    
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