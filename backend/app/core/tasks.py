import os
from celery import Celery
from celery.schedules import crontab
from app.models.database import SessionLocal, User
from app.services.gmail_service import build_gmail_service, get_followup_opportunities
from app.core.security import decrypt_token
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

# Configuration de Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("tasks", broker=redis_url)

@celery_app.task
def scan_all_users_emails():
    """
    Tâche de fond qui parcourt tous les utilisateurs en base de données
    et vérifie s'ils ont des relances à faire.
    """
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            # On déchiffre les tokens pour accéder à Gmail
            access_token = decrypt_token(user.access_token)
            refresh_token = decrypt_token(user.refresh_token) if user.refresh_token else None
            
            service = build_gmail_service(
                access_token, refresh_token, 
                GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
            )
            
            # On lance l'analyse (seuil de 3 jours par exemple)
            opportunities = get_followup_opportunities(service, days_threshold=3)
            
            if len(opportunities) > 0:
                print(f"🔔 {len(opportunities)} opportunités trouvées pour {user.email}")
                # Ici, on déclenchera l'envoi du mail récapitulatif (Point suivant)
                
    finally:
        db.close()

# Configuration du planning (Toutes les 6 heures)
celery_app.conf.beat_schedule = {
    'scan-emails-every-6-hours': {
        'task': 'app.core.tasks.scan_all_users_emails',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}