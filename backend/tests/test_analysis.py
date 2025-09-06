import pytest
from pathlib import Path
from app.analysis import PdfAnalysis

# run: pytest backend/tests/ -v 

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
    
def test_alt_texts_for_tagged_pdf_with_alts():
    """
    Testuje, czy funkcja poprawnie zlicza alt-texty w otagowanym dokumencie.
    """
    pdf_path = SAMPLES_DIR / "tagged_with_alts.pdf"
    assert pdf_path.exists()
    
    analysis = PdfAnalysis(pdf_path.read_bytes())
    results = analysis.run_basic_analysis()
    analysis.close()

    image_info = results["image_info"]
    assert image_info["image_count"] == 2
    assert image_info["images_with_alt"] == 2
    assert image_info["images_without_alt"] == 0
    assert len(image_info["alt_texts"]) == 2
    assert any("Nastrojowe ujęcie filiżanki kawy" in alt for alt in image_info["alt_texts"])
    assert any("Artystyczne zdjęcie laptopa" in alt for alt in image_info["alt_texts"])

def test_alt_texts_for_tagged_pdf_without_alts():
    """
    Testuje, czy funkcja poprawnie identyfikuje brakujące alt-texty w otagowanym dokumencie.
    """
    pdf_path = SAMPLES_DIR / "tagged_no_alts.pdf"
    assert pdf_path.exists()
    
    analysis = PdfAnalysis(pdf_path.read_bytes())
    results = analysis.run_basic_analysis()
    analysis.close()

    image_info = results["image_info"]
    assert image_info["image_count"] == 2
    assert image_info["images_with_alt"] == 0
    assert image_info["images_without_alt"] == 2

def test_alt_texts_for_untagged_pdf():
    """
    Testuje, czy dla nieotagowanego PDF wszystkie obrazy są liczone jako nieposiadające alt-textu.
    """
    pdf_path = SAMPLES_DIR / "untagged_with_images.pdf"
    assert pdf_path.exists()
    
    analysis = PdfAnalysis(pdf_path.read_bytes())
    results = analysis.run_basic_analysis()
    analysis.close()

    image_info = results["image_info"]
    assert results["is_tagged"] is False
    assert image_info["image_count"] > 0
    assert image_info["images_with_alt"] == 0
    assert image_info["images_without_alt"] == image_info["image_count"]

def test_analysis_for_pdf_with_no_images():
    """
    Testuje, czy dokument bez obrazów jest poprawnie analizowany.
    """
    pdf_path = SAMPLES_DIR / "no_images.pdf"
    assert pdf_path.exists()
    
    analysis = PdfAnalysis(pdf_path.read_bytes())
    results = analysis.run_basic_analysis()
    analysis.close()
    
    image_info = results["image_info"]
    assert image_info["image_count"] == 0
    assert image_info["images_with_alt"] == 0
    assert image_info["images_without_alt"] == 0
    
def test_heading_analysis_for_correct_hierarchy():
    """
    Testuje analizę hierarchii nagłówków dla pliku z poprawną strukturą.
    """
    # Założenie: plik 'correct_headings.pdf' istnieje i ma strukturę H1 -> H2 -> H3
    pdf_path = SAMPLES_DIR / "correct_headings.pdf"
    if not pdf_path.exists():
        pytest.skip("Test pominięty: brak pliku 'correct_headings.pdf' do testowania.")
        
    analysis = PdfAnalysis(pdf_path.read_bytes())
    results = analysis.run_basic_analysis()
    analysis.close()
    
    heading_info = results["heading_info"]
    assert heading_info["has_single_h1"] is True
    assert heading_info["has_skipped_levels"] is False
    assert heading_info["h1_count"] == 1
    assert not heading_info["issues"]

def test_heading_analysis_for_multiple_h1():
    """
    Testuje analizę dla pliku z wieloma nagłówkami H1.
    """
    # Założenie: plik 'multiple_h1.pdf' istnieje
    pdf_path = SAMPLES_DIR / "multiple_h1.pdf"
    if not pdf_path.exists():
        pytest.skip("Test pominięty: brak pliku 'multiple_h1.pdf' do testowania.")

    analysis = PdfAnalysis(pdf_path.read_bytes())
    results = analysis.run_basic_analysis()
    analysis.close()

    heading_info = results["heading_info"]
    assert heading_info["has_single_h1"] is False
    assert heading_info["h1_count"] > 1
    assert any("Za dużo nagłówków H1" in issue for issue in heading_info["issues"])


def test_heading_analysis_for_skipped_level():
    """
    Testuje analizę dla pliku z pominiętym poziomem nagłówka (np. H1 -> H3).
    """
    # Założenie: plik 'skipped_level.pdf' istnieje
    pdf_path = SAMPLES_DIR / "skipped_level.pdf"
    if not pdf_path.exists():
        pytest.skip("Test pominięty: brak pliku 'skipped_level.pdf' do testowania.")

    analysis = PdfAnalysis(pdf_path.read_bytes())
    results = analysis.run_basic_analysis()
    analysis.close()

    heading_info = results["heading_info"]
    assert heading_info["has_skipped_levels"] is True
    assert any("Pominięty poziom" in issue for issue in heading_info["issues"])