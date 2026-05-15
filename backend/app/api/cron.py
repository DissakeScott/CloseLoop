import os
from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks
from sqlalchemy.orm import Session
# IMPORT IMPORTANT : On ajoute Opportunity à la liste des imports
from app.models.database import User, Opportunity, get_db, SessionLocal
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
                    
                    # 👇 NOUVELLE PARTIE : Sauvegarde en Base de Données 👇
                    for opp in opportunities:
                        # On vérifie si l'opportunité existe déjà (basé sur le thread_id et l'email de l'utilisateur)
                        existing_opp = db.query(Opportunity).filter(
                            Opportunity.thread_id == opp.get("id"),
                            Opportunity.user_email == user.email
                        ).first()
                        
                        # Si elle n'existe pas, on l'ajoute
                        if not existing_opp:
                            new_opp = Opportunity(
                                user_email=user.email,
                                thread_id=opp.get("id"),
                                subject=opp.get("subject", "Sans objet"),
                                last_message_preview=opp.get("snippet", ""),
                                is_processed=False
                            )
                            db.add(new_opp)
                            
                    # On sauvegarde les changements pour cet utilisateur dans la base de données
                    db.commit()
                    # 👆 ------------------------------------------------ 👆

                    # On envoie l'email récapitulatif
                    send_summary_email(service, user.email, len(opportunities))
            
            except Exception as e:
                # En cas de problème avec cet utilisateur, on annule ses changements DB pour éviter de corrompre la base
                db.rollback() 
                print(f"Erreur lors du scan pour {user.email}: {e}")
                
        print(f"✅ Scan global terminé. {total_opportunities} opportunités traitées.")
        
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