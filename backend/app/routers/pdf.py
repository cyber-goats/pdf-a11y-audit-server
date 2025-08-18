from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz  # PyMuPDF

router = APIRouter()

def is_pdf_tagged(doc: fitz.Document) -> bool:
    """
    Sprawdza w sposób niezawodny, czy dokument PDF jest otagowany,
    wyszukując klucza StructTreeRoot w katalogu dokumentu.
    """
    # Pobieramy numer referencyjny (xref) głównego katalogu PDF
    catalog_xref = doc.pdf_catalog()
    
    # Za pomocą numeru sprawdzamy, czy w tym obiekcie istnieje klucz "StructTreeRoot"
    # Jego obecność jest ostatecznym dowodem na tagowanie.
    # xref_get_key zwraca ('null', 'null') jeśli klucza nie ma.
    if doc.xref_get_key(catalog_xref, "StructTreeRoot")[1] != "null":
        return True
        
    return False

@router.post("/upload/pdf/", tags=["PDF Processing"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Przyjmuje plik PDF, wyciąga z niego tekst, sprawdza czy jest tagowany 
    i zwraca podstawowe metadane.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    try:
        file_bytes = await file.read()
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        
        page_count = pdf_document.page_count
        is_tagged = is_pdf_tagged(pdf_document)
        
        full_text = ""
        
        for page_num in range(page_count):
            page = pdf_document.load_page(page_num)
            full_text += page.get_text() + "\n--- Page Break ---\n"
            
        pdf_document.close()
        
        contains_text = len(full_text.strip()) > 0
        
        return {
            "filename": file.filename,
            "page_count": page_count,
            "is_tagged": is_tagged,
            "contains_text": contains_text,
            "extracted_text_preview": full_text[:500] + "..."
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not process the PDF file: {e}")