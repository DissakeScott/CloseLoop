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
        domain_url = "https://close-loop-liard.vercel.app"
        
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
        
        # Extraction propre de l'email (Stripe stocke souvent ça dans customer_details)
        customer_details = session.get('customer_details', {})
        customer_email = customer_details.get('email') or session.get('customer_email')
        
        # 💡 L'ÉLÉMENT CRUCIAL : On récupère l'identifiant "cus_..." du client
        stripe_customer_id = session.get('customer') 
        
        if customer_email and stripe_customer_id:
            # On cherche l'utilisateur dans notre base de données
            user = db.query(User).filter(User.email == customer_email).first()
            
            if user:
                # MAGIE 1 : On le passe en plan PRO !
                user.plan = "pro"
                
                # MAGIE 2 : On sauvegarde l'identifiant Stripe pour activer le portail client !
                user.stripe_customer_id = stripe_customer_id
                
                db.commit()
                print(f"💰 Succès ! Le compte {customer_email} est passé PRO.")
                print(f"🔗 Identifiant Stripe sauvegardé : {stripe_customer_id}")

    # On répond toujours 200 à Stripe pour lui dire qu'on a bien reçu le message
    return {"status": "success"}


@router.post("/customer-portal")
def create_customer_portal(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not user.stripe_customer_id:
        raise HTTPException(status_code=404, detail="Client Stripe non trouvé. Vous devez d'abord souscrire à un plan.")

    try:
        # On crée une session pour le portail d'auto-gestion
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{FRONTEND_URL}/dashboard/settings",
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))