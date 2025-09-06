# backend/tests/test_analysis.py

import pytest
from pathlib import Path
from app.analysis import PdfAnalysis

# Ścieżka do folderu z testowymi plikami PDF
SAMPLES_DIR = Path(__file__).parent / "sample_pdfs"

def test_metadata_for_correct_pdf():
    """
    Testuje analizę metadanych dla pliku PDF, który ma poprawnie ustawiony tytuł i język.
    """
    pdf_path = SAMPLES_DIR / "good.pdf"
    assert pdf_path.exists(), "Upewnij się, że plik 'good.pdf' istnieje w folderze 'sample_pdfs'"
    
    file_bytes = pdf_path.read_bytes()
    analysis = PdfAnalysis(file_bytes)
    results = analysis.run_basic_analysis()
    analysis.close()

    assert results["is_title_defined"] is True
    assert "Poprawny Dokument Testowy" in results["title"] # Dostosuj do tytułu w Twoim pliku
    
    # Poniższe linie zostały zakomentowane, aby tymczasowo pominąć test języka - nie mam jak ogarnac jezyka w pliku (nie mam adobe acrobat) - TODO: poprawic to zeby moc testowac ten parametr

    # assert results["is_lang_defined"] is True
    # assert results["language"].lower() in ["pl", "pl-pl"] # Dostosuj do języka w Twoim pliku

def test_metadata_for_pdf_with_missing_data():
    """
    Testuje analizę dla pliku PDF, któremu brakuje tytułu i języka.
    """
    pdf_path = SAMPLES_DIR / "bad.pdf"
    assert pdf_path.exists(), "Upewnij się, że plik 'bad.pdf' istnieje w folderze 'sample_pdfs'"
    
    file_bytes = pdf_path.read_bytes()
    analysis = PdfAnalysis(file_bytes)
    results = analysis.run_basic_analysis()
    analysis.close()

    assert results["is_title_defined"] is False
    assert results["title"] == ""
    
    assert results["is_lang_defined"] is False
    assert results["language"] == ""

def test_metadata_for_pdf_with_whitespace_title():
    """
    Testuje, czy tytuł składający się z samych spacji jest traktowany jako niezdefiniowany.
    """
    pdf_path = SAMPLES_DIR / "empty_title.pdf"
    if not pdf_path.exists():
        pytest.skip("Test pominięty: brak pliku 'empty_title.pdf' do testowania.")

    file_bytes = pdf_path.read_bytes()
    analysis = PdfAnalysis(file_bytes)
    results = analysis.run_basic_analysis()
    analysis.close()

    assert results["is_title_defined"] is False