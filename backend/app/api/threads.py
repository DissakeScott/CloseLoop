from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from sqlalchemy.orm import Session
# NOUVEAU : Import de Opportunity
from app.models.database import get_db, User, Opportunity 
from datetime import datetime
from email.utils import parsedate_to_datetime

from app.services.ai_service import generate_followup_draft
from app.services.gmail_service import (
    build_gmail_service, 
    get_followup_opportunities, 
    get_thread_content, 
    send_email_reply,
    get_user_style_examples
)
from google.auth.exceptions import RefreshError

router = APIRouter()

# --- PAYLOADS ---

class TokenPayload(BaseModel):
    access_token: str
    refresh_token: str

class SyncPayload(BaseModel):
    email: str
    access_token: str
    refresh_token: str

class DraftPayload(BaseModel):
    access_token: str
    refresh_token: str

class SendReplyPayload(BaseModel):
    access_token: str
    refresh_token: str
    draft_text: str
    email : str


# --- MOTEUR DE SYNCHRONISATION (La tâche de fond) ---
def sync_opportunities_to_db(email: str, access_token: str, refresh_token: str, db: Session):
    """Moteur interne : Fait travailler l'IA avec les tokens et sauvegarde dans Supabase"""
    service = build_gmail_service(access_token, refresh_token, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    
    # 1. On récupère les opportunités via Gmail + Gemini
    new_opportunities = get_followup_opportunities(service, days_threshold=0)
    
    # 2. On vide les anciennes opportunités non traitées pour ce client
    db.query(Opportunity).filter(Opportunity.user_email == email).delete()
    
    # 3. On enregistre les nouvelles pépites trouvées par l'IA
    for opp in new_opportunities:
        # 💡 AJOUTE CE PRINT POUR VOIR DANS TON TERMINAL CE QUI MANQUE
      #  print(f"🧐 DEBUG OPPORTUNITÉ : {opp}") 
        
        # 💡 On essaie plusieurs noms de variables classiques au cas où l'IA a changé le nom
        date_str = opp.get('date') or opp.get('last_message_date') or opp.get('internalDate')
        # --- CALCUL AUTOMATIQUE DU NOMBRE DE JOURS ---
        days_val = 0
        if date_str:
            try:
                # Essai 1 : Format standard ISO (ex: 2026-05-12T10:00:00Z)
                last_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                delta = datetime.now(last_date.tzinfo) - last_date
                days_val = max(0, delta.days) # max(0) évite d'afficher -1 jour
            except ValueError:
                try:
                    # Essai 2 : Format classique des headers d'e-mail (ex: Tue, 12 May 2026 ...)
                    last_date = parsedate_to_datetime(date_str)
                    delta = datetime.now(last_date.tzinfo) - last_date
                    days_val = max(0, delta.days)
                except Exception:
                    # Si aucun format ne marche, on met 0 par défaut
                    days_val = 0
        # -----------------------------------------------

        db_opp = Opportunity(
            user_email=email,
            thread_id=opp.get('thread_id') or opp.get('id', 'inconnu'),
            subject=opp.get('subject', 'Sans objet'),
            last_message_preview=opp.get('snippet') or opp.get('preview', ''),
            category=opp.get('intent_category') or opp.get('category', 'ATTENTE'),
            analysis_summary=opp.get('intent_reason') or opp.get('summary', ''),
            last_received_date=date_str,
            days_waiting=days_val  # 💡 Ajout du nombre de jours calculé ici !
        )
        db.add(db_opp)
    
    db.commit()

# --- ROUTES DE L'API ---

@router.get("/opportunities")
def fetch_dashboard_opportunities(email: str, db: Session = Depends(get_db)):
    """Affiche le Dashboard instantanément en lisant Supabase (0.1 seconde)"""
    try:
        opportunities = db.query(Opportunity).filter(
            Opportunity.user_email == email,
            Opportunity.is_processed == False
        ).all()
        
        # On garde la même structure de réponse pour ne pas casser le frontend
        return {
            "message": "Données récupérées instantanément ⚡", 
            "data": opportunities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-opportunities")
def force_sync_opportunities(payload: SyncPayload, db: Session = Depends(get_db)):
    """Route pour forcer l'IA à analyser les emails et remplir la base de données"""
    try:
        sync_opportunities_to_db(payload.email, payload.access_token, payload.refresh_token, db)
        return {"message": "Synchronisation terminée avec succès ! Base de données à jour."}
    except RefreshError:
        raise HTTPException(status_code=401, detail="Session Google expirée. Veuillez vous reconnecter.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de synchronisation : {str(e)}")


@router.post("/{thread_id}/draft")
def create_followup_draft(thread_id: str, payload: DraftPayload):
    """Génère un brouillon avec Gemini via un fil de discussion (Avec Clonage de Style)"""
    try:
        service = build_gmail_service(payload.access_token, payload.refresh_token, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        content = get_thread_content(service, thread_id)
        style_examples = get_user_style_examples(service, max_results=3)
        ai_draft = generate_followup_draft(content, user_style_examples=style_examples)
        
        return {
            "thread_id": thread_id,
            "original_content_snippet": content[:200] + "...",
            "ai_draft": ai_draft,
            "style_cloned": True if style_examples else False 
        }
    except RefreshError:
        raise HTTPException(status_code=401, detail="Session Google expirée. Veuillez vous reconnecter.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{thread_id}/send")
def send_followup_reply(thread_id: str, payload: SendReplyPayload, db: Session = Depends(get_db)):
    """Envoie la relance ET gère les quotas / ROI"""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
        
    if user.plan == "free" and user.used_quota >= 5:
        raise HTTPException(status_code=402, detail="QUOTA_REACHED")
        
    try:
        service = build_gmail_service(payload.access_token, payload.refresh_token, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        result = send_email_reply(service, thread_id, payload.draft_text)
        
        user.used_quota += 1
        user.revenue_recovered += 500.0 
        
        # NOUVEAU : On marque l'opportunité comme traitée pour qu'elle disparaisse du Dashboard
        opp = db.query(Opportunity).filter(Opportunity.thread_id == thread_id).first()
        if opp:
            opp.is_processed = True
            
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