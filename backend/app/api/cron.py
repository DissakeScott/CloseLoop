import os
from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks
from sqlalchemy.orm import Session
# IMPORT IMPORTANT : Ajoute SessionLocal pour que la tâche de fond ait sa propre connexion DB
from app.models.database import User, get_db, SessionLocal
from app.core.security import decrypt_token
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.services.gmail_service import build_gmail_service, get_followup_opportunities, send_summary_email

router = APIRouter()

CRON_SECRET = os.getenv("CRON_SECRET")

def process_all_users_background():
    """
    C'est cette fonction qui fait le travail lourd.
    Elle tourne en arrière-plan sans aucune limite de temps !
    """
    # 1. On crée une session DB isolée pour l'arrière-plan
    db = SessionLocal()
    total_opportunities = 0
    
    try:
        users = db.query(User).all()
        
        for user in users:
            if not user.access_token:
                continue
                
            try:
                access_token = decrypt_token(user.access_token)
                refresh_token = decrypt_token(user.refresh_token) if user.refresh_token else None
                
                service = build_gmail_service(
                    access_token, refresh_token, 
                    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
                )
                
                opportunities = get_followup_opportunities(service, days_threshold=3)
                  
                if opportunities:
                    print(f"🔔 {len(opportunities)} opportunités trouvées pour {user.email}")
                    total_opportunities += len(opportunities)
                    send_summary_email(service, user.email, len(opportunities))
            
            except Exception as e:
                print(f"Erreur lors du scan pour {user.email}: {e}")
                
        print(f"✅ Scan global terminé. {total_opportunities} opportunités trouvées.")
        
    finally:
        # 2. Très important : fermer la session DB à la fin du processus
        db.close()


@router.post("/trigger-scans")
def trigger_background_scans(
    background_tasks: BackgroundTasks, 
    authorization: str = Header(None)
):
    """Route appelée toutes les 6h par le service externe (cron-job.org)."""
    
    expected_token = f"Bearer {CRON_SECRET}"
    if authorization != expected_token:
        raise HTTPException(status_code=401, detail="Accès non autorisé au Cron.")
    
    # 3. Au lieu de faire le scan ici, on le délègue à l'arrière-plan
    background_tasks.add_task(process_all_users_background)
            
    # 4. On répond à cron-job.org IMMÉDIATEMENT (en 0.1 seconde)
    return {
        "status": "success", 
        "message": "Le scan a été lancé en arrière-plan et traitera tous les utilisateurs."
    }