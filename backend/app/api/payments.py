import os
import stripe
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db, User

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID = "price_1TUweM35PU14lwm6JUEjcSGk"

# FRONTEND_URL pour rediriger proprement
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

class CheckoutPayload(BaseModel):
    email: str

@router.post("/create-checkout-session")
def create_checkout_session(payload: CheckoutPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
        
    try:
        domain_url = FRONTEND_URL
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            # 💡 SÉCURITÉ 1 : On attache l'ID unique de l'utilisateur
            client_reference_id=str(user.id), 
            payment_method_types=['card'],
            line_items=[
                {
                    'price': STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            # 💡 SÉCURITÉ 2 : On cache son email d'origine ici pour être sûr de le retrouver
            metadata={
                "original_user_email": user.email 
            },
            mode='subscription',
            success_url=f"{domain_url}/dashboard?payment=success",
            cancel_url=f"{domain_url}/dashboard?payment=cancelled",
        )
        
        # Stripe renvoie "url" (pas checkout_url)
        return {"checkout_url": checkout_session.url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: Session = Depends(get_db)):
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        print("❌ Erreur Webhook : Payload invalide")
        raise HTTPException(status_code=400, detail="Payload invalide")
    except stripe.error.SignatureVerificationError as e:
        print("❌ Erreur Webhook : Signature invalide (Vérifie ton STRIPE_WEBHOOK_SECRET)")
        raise HTTPException(status_code=400, detail="Signature invalide")

    # Dans les versions récentes du SDK Stripe, on utilise la notation pointée (event.type)
    if event.type == 'checkout.session.completed':
        session = event.data.object
        
        customer_email = None
        
        # 1. On cherche d'abord dans nos metadata avec 'getattr' au lieu de '.get()'
        metadata = getattr(session, 'metadata', None)
        if metadata:
            customer_email = getattr(metadata, 'original_user_email', None)
            
        # 2. Si pas trouvé, on cherche dans les détails du client
        if not customer_email:
            customer_details = getattr(session, 'customer_details', None)
            if customer_details:
                customer_email = getattr(customer_details, 'email', None)
                
        # 3. Dernier recours
        if not customer_email:
            customer_email = getattr(session, 'customer_email', None)
            
        stripe_customer_id = getattr(session, 'customer', None)
        
        print(f"🧐 Webhook Reçu ! Email: {customer_email} | Stripe ID: {stripe_customer_id}")
        
        if customer_email and stripe_customer_id:
            user = db.query(User).filter(User.email == customer_email).first()
            if user:
                user.plan = "pro"
                user.stripe_customer_id = stripe_customer_id
                db.commit()
                print(f"✅ BINGO ! Le compte {customer_email} est passé PRO dans Supabase.")
            else:
                print(f"⚠️ Utilisateur {customer_email} non trouvé dans Supabase !")

    return {"status": "success"}

@router.post("/customer-portal")
def create_customer_portal(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.stripe_customer_id:
        raise HTTPException(status_code=404, detail="Client Stripe non trouvé.")

    try:
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{FRONTEND_URL}/dashboard/settings",
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))