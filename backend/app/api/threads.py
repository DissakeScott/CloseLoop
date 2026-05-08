# backend/app/api/threads.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from sqlalchemy.orm import Session
from app.models.database import get_db, User

# --- NOUVEAUX IMPORTS ---
from app.services.ai_service import generate_followup_draft
from app.services.gmail_service import (
    build_gmail_service, 
    get_followup_opportunities, 
    get_thread_content, 
    send_email_reply,
    get_user_style_examples # <-- On importe notre nouvelle fonction
)
from google.auth.exceptions import RefreshError

router = APIRouter()

class TokenPayload(BaseModel):
    access_token: str
    refresh_token: str

class DraftPayload(BaseModel):
    access_token: str
    refresh_token: str
    # Le champ "tone" a été supprimé ! 
    # L'IA n'a plus besoin qu'on lui dise "naturel" ou "formel", elle copie le vrai style.

class SendReplyPayload(BaseModel):
    access_token: str
    refresh_token: str
    draft_text: str
    email : str


@router.post("/opportunities")
def fetch_opportunities(payload: TokenPayload):
    """Analyse la boîte mail et renvoie les emails à relancer"""
    try:
        service = build_gmail_service(
            payload.access_token, 
            payload.refresh_token, 
            GOOGLE_CLIENT_ID, 
            GOOGLE_CLIENT_SECRET
        )
        
        opportunities = get_followup_opportunities(service, days_threshold=0)
        
        return {
            "message": f"Analyse terminée : {len(opportunities)} opportunités trouvées ! 🎯", 
            "data": opportunities
        }
    except RefreshError:
        raise HTTPException(status_code=401, detail="Session Google expirée. Veuillez vous reconnecter.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse : {str(e)}")
    

@router.post("/{thread_id}/draft")
def create_followup_draft(thread_id: str, payload: DraftPayload):
    """Génère un brouillon avec Gemini via un fil de discussion (Avec Clonage de Style)"""
    try:
        # 1. On se connecte à Gmail
        service = build_gmail_service(payload.access_token, payload.refresh_token, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        
        # 2. On récupère le contexte de la discussion actuelle
        content = get_thread_content(service, thread_id)
        
        # 3. NOUVEAU : On récupère l'ADN rédactionnel du freelance (ses 3 derniers messages envoyés)
        # /!\ Assure-toi que ta fonction get_user_style_examples accepte 'service' en paramètre
        style_examples = get_user_style_examples(service, max_results=3)
        
        # 4. NOUVEAU : On passe le tout à notre nouvelle IA
        ai_draft = generate_followup_draft(content, user_style_examples=style_examples)
        
        return {
            "thread_id": thread_id,
            "original_content_snippet": content[:200] + "...",
            "ai_draft": ai_draft,
            "style_cloned": True if style_examples else False # Indique au front que le clonage a marché
        }
    except RefreshError:
        raise HTTPException(status_code=401, detail="Session Google expirée. Veuillez vous reconnecter.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{thread_id}/send")
def send_followup_reply(thread_id: str, payload: SendReplyPayload, db: Session = Depends(get_db)):
    """Envoie la relance ET gère les quotas / ROI"""
    
    # 1. Vérification de l'utilisateur et de son quota
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
        
    if user.plan == "free" and user.used_quota >= 3:
        raise HTTPException(
            status_code=402, # 402 = Payment Required
            detail="QUOTA_REACHED"
        )
        
    try:
        # 2. Envoi de l'email
        service = build_gmail_service(payload.access_token, payload.refresh_token, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        result = send_email_reply(service, thread_id, payload.draft_text)
        
        # 3. Succès ! Mise à jour des statistiques (Business)
        user.used_quota += 1
        user.revenue_recovered += 500.0 # Valeur estimée d'une relance sauvée
        db.commit()
        
        return {
            "status": "success",
            "message": "Relance envoyée avec succès ! 🚀",
            "gmail_message_id": result['id']
        }
    except RefreshError:
        raise HTTPException(status_code=401, detail="Session Google expirée.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'envoi : {str(e)}")

# --- NOUVELLE ROUTE POUR LE DASHBOARD ---
@router.get("/stats/{email}")
def get_user_stats(email: str, db: Session = Depends(get_db)):
    """Renvoie les statistiques de l'utilisateur pour le Dashboard"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"plan": "free", "used_quota": 0, "revenue_recovered": 0.0}
        
    return {
        "plan": user.plan,
        "used_quota": user.used_quota,
        "revenue_recovered": user.revenue_recovered
    }