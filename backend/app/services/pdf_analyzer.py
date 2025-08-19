import pymupdf as fitz

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