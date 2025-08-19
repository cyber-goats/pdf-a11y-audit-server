from fastapi import FastAPI
from app.routers import pdf  # Używamy importu absolutnego

app = FastAPI()

app.include_router(pdf.router)

@app.get("/")
def read_root():
    return {"Hello": "From Final Version"}