from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import pdf_analyzer  # Używamy importu absolutnego
import shutil
import os
import uuid

router = APIRouter()

@router.post("/upload/pdf/", tags=["PDF Processing"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint do przyjmowania i analizowania plików PDF.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type.")

    file_bytes = await file.read()
    
    analysis_result = pdf_analyzer.analyze_pdf(file_bytes)
    
    if analysis_result is None:
        raise HTTPException(status_code=422, detail="Could not process the PDF file.")
    
    analysis_result["filename"] = file.filename
    return analysis_result

# Katalog do przechowywania plików w wolumenie Dockera
PDF_STORAGE_PATH = "/tmp/pdfs"
os.makedirs(PDF_STORAGE_PATH, exist_ok=True)


@router.post("/validate/pdf-ua", tags=["Validation"])
async def validate_pdf_ua_endpoint(file: UploadFile = File(...)):
    # ... (kod do zapisu pliku pozostaje bez zmian)
    
    unique_filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(PDF_STORAGE_PATH, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Uruchamiamy walidację, która zwraca XML
    is_compliant, report_xml = pdf_analyzer.validate_pdf_ua(unique_filename)
    # PARSUJEMY XML, ABY UZYSKAĆ LISTĘ BŁĘDÓW
    failed_rules = pdf_analyzer.parse_verapdf_report(report_xml)

    os.remove(file_path)

    # Zwracamy czyste i ustrukturyzowane dane
    return {
        "filename": file.filename,
        "is_compliant_with_pdf_ua": is_compliant,
        "failed_rules_count": len(failed_rules),
        "failed_rules": failed_rules # <-- Zamiast XML, wysyłamy listę błędów
    }