from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import pdf, rules


app = FastAPI()

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