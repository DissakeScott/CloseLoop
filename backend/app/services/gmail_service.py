# backend/app/services/gmail_service.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
import base64
from app.models.database import get_db, User, Opportunity 
from sqlalchemy.orm import Session
import concurrent.futures
from email.message import EmailMessage
from app.services.ai_service import analyze_thread_intent

def build_gmail_service(access_token: str, refresh_token: str, client_id: str, client_secret: str):
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    return build('gmail', 'v1', credentials=creds)

def sync_opportunities_to_db(user_email: str, db: Session):
    """Moteur interne : Fait travailler l'IA et sauvegarde dans Supabase"""
    # 1. On récupère les opportunités via ton ancien système (Gmail + Gemini)
    new_opportunities = get_followup_opportunities(user_email) 
    
    # 2. On nettoie les anciennes opportunités non traitées pour ce client
    db.query(Opportunity).filter(Opportunity.user_email == user_email).delete()
    
    # 3. On enregistre les nouvelles pépites trouvées par l'IA
    for opp in new_opportunities:
        db_opp = Opportunity(
            user_email=user_email,
            thread_id=opp['id'],
            subject=opp['subject'],
            last_message_preview=opp['preview'],
            category=opp['category'],
            analysis_summary=opp['summary'],
            # Attention : adapte cette ligne selon comment ton ancienne fonction renvoie la date
            last_received_date=opp.get('date') 
        )
        db.add(db_opp)
    
    db.commit()

def get_followup_opportunities(service, days_threshold=3, max_results=10):
    """
    Analyse les threads pour trouver ceux qui nécessitent une relance.
    Utilise le multithreading pour accélérer l'analyse de l'IA.
    """
    results = service.users().threads().list(userId='me', q='is:sent newer_than:30d', maxResults=max_results).execute()
    threads = results.get('threads', [])
    
    # 1. On liste d'abord toutes les opportunités SANS l'IA (C'est très rapide)
    raw_opportunities = []
    
    for t in threads:
        thread_data = service.users().threads().get(userId='me', id=t['id']).execute()
        messages = thread_data.get('messages', [])
        
        if not messages:
            continue
            
        last_message = messages[-1]
        
        if 'SENT' not in last_message.get('labelIds', []):
            continue 
            
        timestamp_ms = int(last_message['internalDate'])
        last_date = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
        time_elapsed = datetime.now(timezone.utc) - last_date
        
        if time_elapsed.days >= days_threshold:
            headers = last_message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'Sans objet')
            to_email = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Inconnu')
            snippet = t.get('snippet', '')
            
            raw_opportunities.append({
                "thread_id": t['id'],
                "subject": subject,
                "recipient": to_email,
                "last_message_date": last_date.strftime("%Y-%m-%d %H:%M"),
                "days_waiting": time_elapsed.days,
                "snippet": snippet
            })

    # 2. FONCTION TRAVAILLEUR : Ce que chaque thread va exécuter en parallèle
    def enrich_with_intent(opp):
        try:
            intent_data = analyze_thread_intent(opp['snippet'])
            opp["intent_category"] = intent_data.get("categorie", "OUBLI")
            opp["intent_reason"] = intent_data.get("raison", "Analyse non disponible")
        except Exception as e:
            opp["intent_category"] = "OUBLI"
            opp["intent_reason"] = "Erreur IA"
        return opp

    opportunities = []
    
    # 3. LE MULTITHREADING : On lance les requêtes IA toutes en même temps !
    if raw_opportunities:
        # max_workers=5 signifie qu'on interroge Gemini pour 5 mails en même temps
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            opportunities = list(executor.map(enrich_with_intent, raw_opportunities))
            
    return opportunities


def get_thread_content(service, thread_id: str) -> str:
    """Récupère et décode le texte du dernier message d'un thread"""
    thread = service.users().threads().get(userId='me', id=thread_id).execute()
    last_message = thread['messages'][-1]
    payload = last_message['payload']
    
    # Fonction récursive pour fouiller dans les parties du mail (qui est souvent "multipart")
    def extract_text(part):
        text = ""
        if part.get('mimeType') == 'text/plain':
            data = part['body'].get('data')
            if data:
                text = base64.urlsafe_b64decode(data).decode('utf-8')
        elif 'parts' in part:
            for subpart in part['parts']:
                text += extract_text(subpart)
        return text

    # Si c'est un mail simple sans 'parts'
    if 'parts' not in payload:
        data = payload['body'].get('data')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
            
    return extract_text(payload)

def send_email_reply(service, thread_id: str, draft_text: str):
    """Envoie une réponse dans le thread existant"""
    
    # 1. On récupère le dernier message pour savoir à qui répondre
    thread = service.users().threads().get(userId='me', id=thread_id).execute()
    last_message = thread['messages'][-1]
    headers = last_message['payload']['headers']
    
    # 2. On extrait les informations cruciales pour garder l'historique (le "Thread")
    # Comme c'est nous qui avons envoyé le dernier mail, le "To" reste notre destinataire
    to_email = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
    message_id = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), '')
    
    # On s'assure que le sujet commence par "Re:"
    if not subject.lower().startswith('re:'):
        subject = f"Re: {subject}"
        
    # 3. On construit l'email
    message = EmailMessage()
    message.set_content(draft_text)
    message['To'] = to_email
    message['Subject'] = subject
    
    # Ces deux lignes sont la magie qui fait que Gmail range ça dans la même conversation !
    if message_id:
        message['In-Reply-To'] = message_id
        message['References'] = message_id
        
    # 4. On encode le message pour l'API Google
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    create_message = {
        'raw': encoded_message,
        'threadId': thread_id
    }
    
    # 5. ENVOI ! 🚀
    sent_message = service.users().messages().send(userId="me", body=create_message).execute()
    return sent_message


def get_user_style_examples(service, max_results=5):
    """
    Récupère les derniers messages envoyés par l'utilisateur pour servir d'exemples de style.
    """
    
    # On cherche uniquement les messages dans "SENT" (envoyés)
    results = service.users().messages().list(userId='me', labelIds=['SENT'], maxResults=max_results).execute()
    messages = results.get('messages', [])
    
    style_examples = []
    for msg in messages:
        m = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        # On extrait le corps du texte (en ignorant les signatures et le reste si possible)
        payload = m.get('payload', {})
        parts = payload.get('parts', [])
        
        body = ""
        if not parts: # Message simple sans pièces jointes
            body = payload.get('body', {}).get('data', '')
        else:
            # On cherche la partie 'text/plain'
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body = part.get('body', {}).get('data', '')
        
        if body:
            import base64
            decoded_body = base64.urlsafe_b64decode(body).decode('utf-8')
            # Nettoyage rapide pour ne garder que le texte pur
            style_examples.append(decoded_body[:500]) # On limite à 500 caractères par exemple
            
    return style_examples


def send_summary_email(service, user_email: str, opp_count: int):
    """Envoie un email récapitulatif au format HTML Premium"""
    message = EmailMessage()
    
    # 1. Le sujet de l'email
    message['Subject'] = f"🔔 {opp_count} opportunité(s) de relance en attente"
    message['From'] = f"MailtiVoo <{user_email}>" # Ajoute un joli nom d'expéditeur
    message['To'] = user_email
    
    # 2. Le texte de secours (obligatoire pour les vieux clients mail ou les montres connectées)
    text_fallback = f"""Bonjour ! 
MailtiVoo a identifié {opp_count} opportunité(s) de relance ce matin.
Traitez-les ici : https://close-loop-liard.vercel.app/dashboard
"""
    message.set_content(text_fallback)
    
    # 3. Le beau design HTML (Le vrai rendu visuel)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="100%" max-width="600px" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); max-width: 600px;">
                        
                        <tr>
                            <td align="center" style="padding: 30px 40px; border-bottom: 1px solid #f1f5f9;">
                                <h1 style="margin: 0; color: #0f172a; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">Mailti<span style="color: #2563eb;">Voo</span></h1>
                            </td>
                        </tr>
                        
                        <tr>
                            <td style="padding: 40px;">
                                <h2 style="margin-top: 0; color: #1e293b; font-size: 20px; font-weight: 600;">Bonjour, 👋</h2>
                                <p style="color: #475569; font-size: 16px; line-height: 24px; margin-bottom: 30px;">
                                    Ton assistant virtuel a scanné ta boîte mail lors de ton inactivité. Nous avons identifié <strong style="color: #0f172a; font-weight: 700;">{opp_count} opportunité(s) de relance cruciale(s)</strong> qui n'attendent plus que ton approbation.
                                </p>
                                
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td align="center">
                                            <a href="https://close-loop-liard.vercel.app/dashboard" target="_blank" style="display: inline-block; background-color: #2563eb; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; padding: 14px 28px; border-radius: 10px; box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);">
                                                Traiter mes relances
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #475569; font-size: 14px; line-height: 24px; margin-top: 30px; text-align: center;">
                                    L'IA a déjà pré-rédigé les brouillons en clonant ton style d'écriture. Il ne te reste plus qu'à valider.
                                </p>
                            </td>
                        </tr>
                        
                        <tr>
                            <td align="center" style="background-color: #f8fafc; padding: 20px; border-top: 1px solid #f1f5f9;">
                                <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                    Généré automatiquement par l'intelligence artificielle de MailtiVoo.<br>
                                    Tu reçois cet email car le scan automatique est activé.
                                </p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # On ajoute le HTML au message
    message.add_alternative(html_content, subtype='html')
    
    # Encodage et envoi
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    
    try:
        service.users().messages().send(userId="me", body=create_message).execute()
        print(f"📧 Notification HTML envoyée avec succès à {user_email}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de la notification HTML à {user_email}: {e}")