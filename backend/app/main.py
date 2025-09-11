import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import pdf, rules
from supabase import create_client, Client
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
# Odczytujemy zmienne środowiskowe przekazane przez Dockera
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")

# Sprawdzamy, czy zmienne zostały załadowane
if not url or not key:
    print("⚠️  Nie znaleziono zmiennych środowiskowych SUPABASE_URL lub SUPABASE_ANON_KEY")
    print("📝  Aplikacja będzie działać bez integracji z bazą wiedzy")
    supabase_client: Client | None = None
else:
    supabase_client: Client = create_client(url, key)
    print("✅ Połączono z Supabase!")

# Udostępnij klienta globalnie (dla innych modułów)
app.state.supabase_client = supabase_client


# CORS configuration for Docker containers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Local development
        "http://frontend:3000",       # Docker container name
        "http://127.0.0.1:3000",     # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf.router)
app.include_router(rules.router)

@app.get("/")
def read_root():
    return {"Hello": "From Final Version"}