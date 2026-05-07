# backend/app/api/threads.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.services.ai_service import generate_draft
from app.services.gmail_service import build_gmail_service, get_followup_opportunities, get_thread_content, send_email_reply
from google.auth.exceptions import RefreshError
router = APIRouter()

class TokenPayload(BaseModel):
    access_token: str
    refresh_token: str

class DraftPayload(BaseModel):
    access_token: str
    refresh_token: str
    tone: str = "naturel"

class SendReplyPayload(BaseModel):
    access_token: str
    refresh_token: str
    draft_text: str


@router.post("/opportunities") # <-- J'ai renommé la route pour que ce soit plus "produit"
def fetch_opportunities(payload: TokenPayload):
    """Analyse la boîte mail et renvoie les emails à relancer"""
    try:
        service = build_gmail_service(
            payload.access_token, 
            payload.refresh_token, 
            GOOGLE_CLIENT_ID, 
            GOOGLE_CLIENT_SECRET
        )
        
        # On lance l'algorithme (avec un seuil de 3 jours par défaut)
        opportunities = get_followup_opportunities(service, days_threshold=0)
        
        return {
            "message": f"Analyse terminée : {len(opportunities)} opportunités trouvées ! 🎯", 
            "data": opportunities
        }
    except RefreshError:
        # C'EST NOUVEAU : On repère spécifiquement l'expiration Google
        raise HTTPException(status_code=401, detail="Session Google expirée. Veuillez vous reconnecter.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse : {str(e)}")
    
@router.post("/{thread_id}/draft")
def create_followup_draft(thread_id: str, payload: DraftPayload): # <-- Modifie ici
    """Génère un brouillon avec Gemini via un fil de discussion"""
    try:
        service = build_gmail_service(payload.access_token, payload.refresh_token, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        content = get_thread_content(service, thread_id)
        
        # On passe le ton à notre IA !
        ai_draft = generate_draft(content, tone=payload.tone) # <-- Modifie ici
        
        return {
            "thread_id": thread_id,
            "original_content_snippet": content[:200] + "...",
            "ai_draft": ai_draft,
            "tone_used": payload.tone
        }
    except RefreshError:
        # C'EST NOUVEAU : On repère spécifiquement l'expiration Google
        raise HTTPException(status_code=401, detail="Session Google expirée. Veuillez vous reconnecter.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{thread_id}/send")
def send_followup_reply(thread_id: str, payload: SendReplyPayload):
    """Envoie la relance définitive dans le thread Gmail"""
    try:
        service = build_gmail_service(
            payload.access_token, 
            payload.refresh_token, 
            GOOGLE_CLIENT_ID, 
            GOOGLE_CLIENT_SECRET
        )
        
        # Envoi de l'email !
        result = send_email_reply(service, thread_id, payload.draft_text)
        
        return {
            "status": "success",
            "message": "Relance envoyée avec succès ! 🚀",
            "gmail_message_id": result['id']
        }
    except RefreshError:
        # C'EST NOUVEAU : On repère spécifiquement l'expiration Google
        raise HTTPException(status_code=401, detail="Session Google expirée. Veuillez vous reconnecter.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi : {str(e)}")