from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz  # PyMuPDF

router = APIRouter()

@router.post("/upload/pdf/", tags=["PDF Processing"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Przyjmuje plik PDF, odczytuje go w pamięci i zwraca liczbę stron.
    """
    # Sprawdzamy, czy przesłany plik to na pewno PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    try:
        # Odczytujemy zawartość pliku do pamięci RAM
        file_bytes = await file.read()
        
        # Otwieramy dokument PDF bezpośrednio z odczytanych bajtów
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        
        # Pobieramy liczbę stron
        page_count = pdf_document.page_count
        
        # Zamykamy dokument
        pdf_document.close()
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "page_count": page_count
        }
    except Exception as e:
        # Obsługa błędu, jeśli plik jest uszkodzony lub nie jest poprawnym PDF
        raise HTTPException(status_code=422, detail=f"Could not process the PDF file: {e}")