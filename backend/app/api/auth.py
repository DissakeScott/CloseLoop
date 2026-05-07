import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
from googleapiclient.discovery import build 
from sqlalchemy.orm import Session 
import datetime 
from app.models.database import User, get_db 

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

router = APIRouter()

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.modify"
]

CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [GOOGLE_REDIRECT_URI],
    }
}

# === L'ASTUCE POUR LE MVP ===
# Dictionnaire en mémoire pour stocker la clé de sécurité entre l'aller et le retour
auth_state_store = {}

@router.get("/login")
def login():
    """Redirige l'utilisateur vers la page de connexion Google"""
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true"
    )
    
    # On sauvegarde le "code verifier" en mémoire avec le "state" comme identifiant
    auth_state_store[state] = getattr(flow, 'code_verifier', None)
    
    return RedirectResponse(str(authorization_url))

@router.get("/callback")
def auth_callback(state: str, code: str, db: Session = Depends(get_db)):
    """Route appelée par Google après l'acceptation"""
    try:
        flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, state=state)
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        saved_verifier = auth_state_store.get(state)
        if saved_verifier:
            flow.code_verifier = saved_verifier
            
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        if state in auth_state_store:
            del auth_state_store[state]
            
        # 1. On récupère l'adresse email de l'utilisateur via l'API Google
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        user_email = user_info.get('email')

        # 2. On calcule l'heure d'expiration exacte
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=credentials.expiry.timestamp() - datetime.datetime.utcnow().timestamp() if credentials.expiry else 3599)

        # 3. SAUVEGARDE EN BASE DE DONNÉES !
        db_user = db.query(User).filter(User.email == user_email).first()
        
        if db_user:
            # L'utilisateur existe, on met à jour son token
            db_user.access_token = credentials.token
            db_user.expires_at = expires_at
            # On ne met à jour le refresh_token QUE s'il y en a un nouveau (Google n'en donne pas à chaque fois)
            if credentials.refresh_token:
                db_user.refresh_token = credentials.refresh_token
        else:
            # Nouvel utilisateur ! On le crée.
            db_user = User(
                email=user_email,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                expires_at=expires_at
            )
            db.add(db_user)
            
        db.commit()
        
        # --- C'EST ICI QUE TOUT CHANGE ---
        # On récupère l'URL de Vercel depuis les variables Render (ou localhost par défaut)
        base_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # On construit le lien dynamique vers le dashboard
        frontend_url = f"{base_frontend_url}/dashboard?access_token={db_user.access_token}&email={db_user.email}"
        
        if db_user.refresh_token:
            frontend_url += f"&refresh_token={db_user.refresh_token}"
            
        return RedirectResponse(url=frontend_url)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur d'authentification : {str(e)}")
    
@router.get("/user_tokens")
def get_user_tokens(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return {
        "access_token": user.access_token,
        "refresh_token": user.refresh_token
    }