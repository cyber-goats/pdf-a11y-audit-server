class PDFAnalysisError(Exception):
    """Podstawowa klasa dla błędów analizy PDF."""
    def __init__(self, message="Błąd analizy pliku PDF", error_code="ERR_PDF_PROCESSING"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class CorruptPDFError(PDFAnalysisError):
    """Błąd dla uszkodzonych plików PDF."""
    def __init__(self, message="Plik PDF jest uszkodzony lub ma nieprawidłową strukturę."):
        super().__init__(message, "ERR_CORRUPT_FILE")

class PasswordProtectedPDFError(PDFAnalysisError):
    """Błąd dla plików PDF zabezpieczonych hasłem."""
    def __init__(self, message="Plik PDF jest zabezpieczony hasłem i nie można go przetworzyć."):
        super().__init__(message, "ERR_PASSWORD_PROTECTED")