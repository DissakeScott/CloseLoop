import os
import stripe
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db, User

router = APIRouter()

# On charge les clés depuis l'environnement
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Ton identifiant de produit fraîchement créé !
STRIPE_PRICE_ID = "price_1TUweM35PU14lwm6JUEjcSGk"

# 💡 CORRECTION : On définit FRONTEND_URL pour éviter les crashs (par défaut localhost pour tes tests)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


class CheckoutPayload(BaseModel):
    email: str

@router.post("/create-checkout-session")
def create_checkout_session(payload: CheckoutPayload, db: Session = Depends(get_db)):
    """Crée une session de paiement Stripe pour l'utilisateur"""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
        
    try:
        # 💡 On utilise le FRONTEND_URL dynamique ici aussi
        domain_url = FRONTEND_URL
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f"{domain_url}/dashboard?payment=success",
            cancel_url=f"{domain_url}/dashboard?payment=cancelled",
        )
        
        # 💡 ATTENTION : Stripe renvoie 'url' et pas 'checkout_url' dans l'objet de base, 
        # mais on le passe sous le nom "checkout_url" pour ton front.
        return {"checkout_url": checkout_session.url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: Session = Depends(get_db)):
    """Écoute les événements envoyés par Stripe (ex: Paiement réussi)"""
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Payload invalide")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Signature invalide")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        customer_details = session.get('customer_details', {})
        customer_email = customer_details.get('email') or session.get('customer_email')
        stripe_customer_id = session.get('customer') 
        
        if customer_email and stripe_customer_id:
            user = db.query(User).filter(User.email == customer_email).first()
            if user:
                user.plan = "pro"
                user.stripe_customer_id = stripe_customer_id
                db.commit()
                print(f"💰 Succès ! Le compte {customer_email} est passé PRO.")

    return {"status": "success"}


@router.post("/customer-portal")
def create_customer_portal(email: str, db: Session = Depends(get_db)):
    """Crée un lien vers le portail de gestion de l'abonnement Stripe"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not user.stripe_customer_id:
        raise HTTPException(status_code=404, detail="Client Stripe non trouvé. Vous devez d'abord souscrire à un plan.")

    try:
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{FRONTEND_URL}/dashboard/settings",
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))