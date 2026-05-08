import os
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.models.database import User, get_db
from app.services.gmail_service import build_gmail_service, get_followup_opportunities
from app.core.security import decrypt_token
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

router = APIRouter()

# On récupère le mot de passe depuis les variables d'environnement
CRON_SECRET = os.getenv("CRON_SECRET")

@router.post("/trigger-scans")
def trigger_background_scans(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Route appelée toutes les 6h par un service externe pour scanner les emails."""
    
    # 1. Vérification de la sécurité
    expected_token = f"Bearer {CRON_SECRET}"
    if authorization != expected_token:
        raise HTTPException(status_code=401, detail="Accès non autorisé au Cron.")
    
    users = db.query(User).all()
    total_opportunities = 0
    
    # 2. Parcours de tous les utilisateurs de la base de données
    for user in users:
        if not user.access_token:
            continue
            
        try:
            # On déchiffre les tokens (la sécurité de la Phase 1 paie ici !)
            access_token = decrypt_token(user.access_token)
            refresh_token = decrypt_token(user.refresh_token) if user.refresh_token else None
            
            service = build_gmail_service(
                access_token, refresh_token, 
                GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
            )
            
            # On cherche les opportunités (avec un seuil de 3 jours)
            opportunities = get_followup_opportunities(service, days_threshold=3)
            
            if opportunities:
                print(f"🔔 {len(opportunities)} opportunités trouvées pour {user.email}")
                total_opportunities += len(opportunities)
                
                # NOUVEAUTÉ À VENIR : Ici, on insèrera la ligne pour envoyer un email de notification !
                
        except Exception as e:
            print(f"Erreur lors du scan pour {user.email}: {e}")
            # Si le token d'un utilisateur a expiré, on l'ignore et on passe au suivant
            
    return {
        "status": "success", 
        "users_scanned": len(users), 
        "total_opportunities_found": total_opportunities
    }