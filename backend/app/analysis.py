# backend/app/analysis.py

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
    Główna klasa orkiestrująca proces analizy dostępności pliku PDF.
    """

    def __init__(self, file_bytes: bytes):
        """
        Inicjalizuje analizę, otwierając dokument PDF.

        Args:
            file_bytes: Surowe bajty pliku PDF.

        Raises:
            PasswordProtectedPDFError: Jeśli plik jest zaszyfrowany.
            CorruptPDFError: Jeśli plik jest uszkodzony lub nie ma stron.
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

        Returns:
            Słownik z podstawowymi informacjami o pliku.
        """
        logger.info(f"Uruchamianie podstawowej analizy dla PDF z {self.doc.page_count} stronami.")
        
        tagged = self._is_tagged()
        image_info = self._get_image_alts()
        
        full_text = ""
        for page in self.doc:
            full_text += page.get_text()

        contains_text = len(full_text.strip()) > 0
        
        return {
            "page_count": self.doc.page_count,
            "is_tagged": tagged,
            "contains_text": contains_text,
            "image_info": image_info,
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

    def _get_image_alts(self) -> Dict:
        """Analizuje obrazy i ich teksty alternatywne."""
        image_analysis = {
            "image_count": 0,
            "images_with_alt": 0,
            "images_without_alt": 0,
            "alt_texts": []
        }
        
        for page in self.doc:
            image_analysis["image_count"] += len(page.get_images(full=True))
        
        if not self._is_tagged():
            image_analysis["images_without_alt"] = image_analysis["image_count"]
            return image_analysis
        
        # Logika do ekstrakcji alt-textów (może być rozbudowana)
        # Na razie uproszczona, zakładamy, że jeśli jest otagowany, to alty są (do poprawy w kolejnych krokach)
        
        return image_analysis

    def close(self):
        """Zamyka dokument PDF, jeśli jest otwarty."""
        if self.doc:
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