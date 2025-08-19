from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import pdf_analyzer  # Używamy importu absolutnego

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