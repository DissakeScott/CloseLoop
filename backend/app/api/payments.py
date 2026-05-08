import os
import stripe
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db, User
from fastapi import Request, Header

router = APIRouter()

# On charge la clé secrète depuis le .env
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Ton identifiant de produit fraîchement créé !
STRIPE_PRICE_ID = "price_1TUweM35PU14lwm6JUEjcSGk"

class CheckoutPayload(BaseModel):
    email: str

@router.post("/create-checkout-session")
def create_checkout_session(payload: CheckoutPayload, db: Session = Depends(get_db)):
    """Crée une session de paiement Stripe pour l'utilisateur"""
    
    # 1. On vérifie que l'utilisateur existe
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
        
    try:
        # L'URL où Stripe va renvoyer l'utilisateur après le paiement (ou l'annulation)
        # Pour le moment on met le localhost pour tes tests, on changera pour Vercel plus tard !
        domain_url = "http://localhost:3000" 
        
        # 2. Création de la session Stripe
        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email, # Pré-remplit l'email sur la page de paiement !
            payment_method_types=['card'],
            line_items=[
                {
                    'price': STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            mode='subscription', # C'est un abonnement
            success_url=f"{domain_url}/dashboard?payment=success", # S'il paie, on le félicite
            cancel_url=f"{domain_url}/dashboard?payment=cancelled", # S'il annule, retour case départ
        )
        
        # On renvoie l'URL de la page de paiement générée
        return {"checkout_url": checkout_session.url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NOUVELLE VARIABLE : La clé secrète du Webhook (on l'ajoutera dans le .env plus tard)
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: Session = Depends(get_db)):
    """Écoute les événements envoyés par Stripe (ex: Paiement réussi)"""
    
    # 1. On lit le corps de la requête envoyée par Stripe
    payload = await request.body()
    
    try:
        # 2. On vérifie que c'est bien Stripe qui parle (Sécurité)
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Payload invalide")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Signature invalide")

    # 3. Si le paiement est un succès !
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email')
        
        if customer_email:
            # On cherche l'utilisateur dans notre base de données
            user = db.query(User).filter(User.email == customer_email).first()
            if user:
                # MAGIE : On le passe en plan PRO !
                user.plan = "pro"
                db.commit()
                print(f"💰 Succès ! Le compte {customer_email} est passé PRO.")

    return {"status": "success"}