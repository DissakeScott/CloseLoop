# backend/app/main.py
from fastapi import FastAPI
import sentry_sdk
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth # On importe nos routes d'auth
from app.api import threads  # <-- AJOUT : Import du nouveau routeur
from app.models.database import init_db
from app.api.cron import router as cron_router
from app.api.payments import router as payments_router

init_db()

load_dotenv()

# --- INITIALISATION DE SENTRY ---
sentry_dsn = os.getenv("SENTRY_DSN")

if sentry_dsn:
    print(f"✅ Sentry DSN trouvé ! Sentry est activé.") # Un petit print pour nous rassurer
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
else:
    print("❌ ATTENTION: Sentry DSN introuvable dans le .env !")


app = FastAPI(title="MailtiVoo API")

origins = [
    "http://localhost:3000",
    "https://mailtivoo.com",
    "https://www.mailtivoo.com",
    ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# On connecte le routeur. Les routes seront accessibles sous /auth/...
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(threads.router, prefix="/threads", tags=["Gmail Threads"])
app.include_router(cron_router, prefix="/api/admin", tags=["Admin/Cron"])
app.include_router(payments_router, prefix="/payments", tags=["Payments"])

@app.get("/")
def read_root():
    return {"message": "API Smart Follow-up opérationnelle 🚀"}

@app.get("/health")
def health_check():
    return {"status": "awake", "message": "MailtiVoo backend is running!"}
