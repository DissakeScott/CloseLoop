# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth # On importe nos routes d'auth
from app.api import threads  # <-- AJOUT : Import du nouveau routeur
from app.models.database import init_db

init_db()

app = FastAPI(title="Smart Follow-up API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# On connecte le routeur. Les routes seront accessibles sous /auth/...
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(threads.router, prefix="/threads", tags=["Gmail Threads"])
@app.get("/")
def read_root():
    return {"message": "API Smart Follow-up opérationnelle 🚀"}