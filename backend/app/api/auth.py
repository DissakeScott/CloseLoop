import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
from googleapiclient.discovery import build 
from sqlalchemy.orm import Session 
import datetime 
from app.models.database import User, OAuthState, get_db
from app.core.security import encrypt_token 

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
#auth_state_store = {}

@router.get("/login")
def login(db: Session = Depends(get_db)):
    """Redirige l'utilisateur vers la page de connexion Google"""
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true" 
    )
    
    # On sauvegarde dans Supabase
    code_verifier = getattr(flow, 'code_verifier', '')
    if code_verifier:
        db_state = OAuthState(state=state, code_verifier=code_verifier)
        db.add(db_state)
        db.commit()
    
    return RedirectResponse(str(authorization_url))

@router.get("/callback")
def auth_callback(state: str, code: str, db: Session = Depends(get_db)):
    """Route appelée par Google après l'acceptation"""
    try:
        flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, state=state)
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # LECTURE DEPUIS SUPABASE
        db_state = db.query(OAuthState).filter(OAuthState.state == state).first()
        if db_state:
            flow.code_verifier = db_state.code_verifier
            # On supprime le state de la base de données car il ne sert qu'une fois (sécurité !)
            db.delete(db_state)
            db.commit()
        else:
            raise HTTPException(status_code=400, detail="Session de connexion invalide ou expirée.")
            
        flow.fetch_token(code=code)
        credentials = flow.credentials
            
        # 1. On récupère l'adresse email de l'utilisateur via l'API Google
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        user_email = user_info.get('email')

        # 2. On calcule l'heure d'expiration exacte
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=credentials.expiry.timestamp() - datetime.datetime.utcnow().timestamp() if credentials.expiry else 3599)

        # 3. SAUVEGARDE EN BASE DE DONNÉES !
        db_user = db.query(User).filter(User.email == user_email).first()

        if db_user:
            # L'utilisateur existe, on met à jour son token (CHIFFRÉ)
            db_user.access_token = encrypt_token(credentials.token)
            db_user.expires_at = expires_at
            if credentials.refresh_token:
                db_user.refresh_token = encrypt_token(credentials.refresh_token)
        else:
            # Nouvel utilisateur ! On le crée avec des tokens CHIFFRÉS.
            db_user = User(
                email=user_email,
                access_token=encrypt_token(credentials.token),
                refresh_token=encrypt_token(credentials.refresh_token) if credentials.refresh_token else None,
                expires_at=expires_at
            )
            db.add(db_user)

        db.commit()

        base_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

        
        frontend_url = f"{base_frontend_url}/dashboard?access_token={credentials.token}&email={user_email}"

        if credentials.refresh_token:
            frontend_url += f"&refresh_token={credentials.refresh_token}"

        return RedirectResponse(url=frontend_url)
    
    except Exception as e:
        print(f"🚨 ERREUR GOOGLE OAUTH: {str(e)}") 
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

@router.get("/me")
def get_current_user_info(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
    return {
        "full_name": user.full_name,
        "email": user.email,
        "plan": user.plan,
        "used_quota": user.used_quota,
        "subscription_end": user.subscription_end, # Assure-toi que ce champ existe en BD
        "is_active": True # Logique à lier avec Stripe
    }