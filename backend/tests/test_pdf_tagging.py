import pytest
from pathlib import Path
from app.analysis import PdfAnalysis
import logging

# Konfiguracja logowania dla testów
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ścieżka do folderu z testowymi plikami PDF
SAMPLES_DIR = Path(__file__).parent / "sample_pdfs"

class TestPdfTagging:
    """Kompleksowe testy weryfikacji tagowania dokumentów PDF"""
    
    def test_tagged_pdf_detection(self):
        """
        Test 1: Weryfikacja, że otagowany PDF jest poprawnie rozpoznawany
        """
        pdf_path = SAMPLES_DIR / "tagged_with_structure.pdf"
        assert pdf_path.exists(), f"Plik testowy nie istnieje: {pdf_path}"
        
        analysis = PdfAnalysis(pdf_path.read_bytes())
        results = analysis.run_basic_analysis()
        analysis.close()
        
        # Podstawowa asercja
        assert results["is_tagged"] is True, "Otagowany PDF powinien być rozpoznany jako tagged"
        
        # Dodatkowe sprawdzenia dla otagowanego PDF
        logger.info(f"✅ Otagowany PDF rozpoznany. Szczegóły: {results.get('page_count')} stron")
    
    def test_untagged_pdf_detection(self):
        """
        Test 2: Weryfikacja, że nieotagowany PDF jest poprawnie rozpoznawany
        """
        pdf_path = SAMPLES_DIR / "untagged_simple.pdf"
        assert pdf_path.exists(), f"Plik testowy nie istnieje: {pdf_path}"
        
        analysis = PdfAnalysis(pdf_path.read_bytes())
        results = analysis.run_basic_analysis()
        analysis.close()
        
        # Podstawowa asercja
        assert results["is_tagged"] is False, "Nieotagowany PDF nie powinien być rozpoznany jako tagged"
        
        logger.info(f"✅ Nieotagowany PDF poprawnie rozpoznany")
    
    def test_partially_tagged_pdf(self):
        """
        Test 3: Weryfikacja PDF z częściowym tagowaniem
        """
        pdf_path = SAMPLES_DIR / "partially_tagged.pdf"
        if not pdf_path.exists():
            pytest.skip("Brak pliku z częściowym tagowaniem do testowania")
        
        analysis = PdfAnalysis(pdf_path.read_bytes())
        results = analysis.run_basic_analysis()
        analysis.close()
        
        # PDF z jakimkolwiek StructTreeRoot powinien być uznany za otagowany
        assert results["is_tagged"] is True, "PDF z częściowym tagowaniem powinien być oznaczony jako tagged"
        
        # Możemy sprawdzić dodatkowe metryki
        logger.info(f"⚠️ PDF z częściowym tagowaniem - uznany za tagged")
    
    def test_corrupted_structure_tree(self):
        """
        Test 4: Weryfikacja obsługi uszkodzonego drzewa struktury
        """
        pdf_path = SAMPLES_DIR / "corrupted_structure.pdf"
        if not pdf_path.exists():
            pytest.skip("Brak pliku z uszkodzoną strukturą do testowania")
        
        analysis = PdfAnalysis(pdf_path.read_bytes())
        results = analysis.run_basic_analysis()
        analysis.close()
        
        # Nawet z uszkodzonym drzewem, funkcja powinna zwrócić False bez crashu
        assert isinstance(results["is_tagged"], bool), "Funkcja powinna zwrócić bool nawet dla uszkodzonego PDF"
        logger.info(f"✅ Obsługa uszkodzonej struktury: is_tagged = {results['is_tagged']}")
    
    def test_tagged_pdf_with_artifacts(self):
        """
        Test 5: Weryfikacja PDF z tagami i artefaktami (np. nagłówki/stopki)
        """
        pdf_path = SAMPLES_DIR / "tagged_with_artifacts.pdf"
        if not pdf_path.exists():
            pytest.skip("Brak pliku z artefaktami do testowania")
        
        analysis = PdfAnalysis(pdf_path.read_bytes())
        results = analysis.run_basic_analysis()
        analysis.close()
        
        assert results["is_tagged"] is True
        # Artefakty nie powinny wpływać na wykrywanie tagowania
        logger.info("✅ PDF z artefaktami poprawnie rozpoznany jako tagged")
    
    def test_performance_large_tagged_pdf(self):
        """
        Test 6: Wydajność dla dużego otagowanego PDF
        """
        pdf_path = SAMPLES_DIR / "large_tagged.pdf"
        if not pdf_path.exists():
            pytest.skip("Brak dużego pliku PDF do testowania wydajności")
        
        import time
        
        start_time = time.time()
        analysis = PdfAnalysis(pdf_path.read_bytes())
        results = analysis.run_basic_analysis()
        analysis.close()
        elapsed = time.time() - start_time
        
        assert results["is_tagged"] is True
        assert elapsed < 5.0, f"Analiza trwała zbyt długo: {elapsed:.2f}s"
        
        logger.info(f"⚡ Wydajność: Analiza dużego PDF ({results['page_count']} stron) w {elapsed:.2f}s")
    
    def test_tagging_consistency(self):
        """
        Test 7: Sprawdzenie spójności wyników dla tego samego pliku
        """
        pdf_path = SAMPLES_DIR / "tagged_with_structure.pdf"
        assert pdf_path.exists()
        
        file_bytes = pdf_path.read_bytes()
        
        # Sprawdź 3 razy ten sam plik
        results = []
        for i in range(3):
            analysis = PdfAnalysis(file_bytes)
            result = analysis.run_basic_analysis()
            analysis.close()
            results.append(result["is_tagged"])
        
        # Wszystkie wyniki powinny być identyczne
        assert all(r == results[0] for r in results), "Niespójne wyniki dla tego samego pliku!"
        logger.info("✅ Spójność: Wielokrotna analiza daje ten sam wynik")
    
    def test_tagging_info_in_report(self):
        """
        Test 8: Weryfikacja, że informacja o tagowaniu jest w pełnym raporcie
        """
        pdf_path = SAMPLES_DIR / "tagged_with_structure.pdf"
        assert pdf_path.exists()
        
        analysis = PdfAnalysis(pdf_path.read_bytes())
        results = analysis.run_basic_analysis()
        analysis.close()
        
        # Sprawdź czy is_tagged jest w wynikach
        assert "is_tagged" in results, "Brak pola 'is_tagged' w wynikach"
        assert isinstance(results["is_tagged"], bool), "is_tagged powinno być typu bool"
        
        # Sprawdź czy wpływa na inne metryki
        if not results["is_tagged"]:
            logger.warning("⚠️ Nieotagowany PDF - może wpłynąć na dostępność")
        else:
            logger.info("✅ PDF otagowany - dobra podstawa dla dostępności")

# Funkcja pomocnicza do generowania plików testowych
def create_test_pdfs():
    """
    Pomocnicza funkcja do utworzenia przykładowych plików testowych
    (uruchom tylko raz do przygotowania plików)
    """
    import fitz  # PyMuPDF
    
    samples_dir = Path(__file__).parent / "sample_pdfs"
    samples_dir.mkdir(exist_ok=True)
    
    # 1. Prosty nieotagowany PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is an untagged PDF document.")
    doc.save(samples_dir / "untagged_simple.pdf")
    doc.close()
    
    logger.info("✅ Utworzono pliki testowe w folderze sample_pdfs/")

if __name__ == "__main__":
    # Możesz uruchomić to bezpośrednio do debugowania
    test = TestPdfTagging()
    test.test_tagged_pdf_detection()
    test.test_untagged_pdf_detection()