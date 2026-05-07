# backend/app/services/gmail_service.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
import base64
from email.message import EmailMessage

def build_gmail_service(access_token: str, refresh_token: str, client_id: str, client_secret: str):
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    return build('gmail', 'v1', credentials=creds)

def get_followup_opportunities(service, days_threshold=3, max_results=10):
    """
    Analyse les threads pour trouver ceux qui nécessitent une relance.
    """
    # On cherche les messages envoyés sur les 30 derniers jours (pour limiter la charge)
    results = service.users().threads().list(userId='me', q='is:sent newer_than:30d', maxResults=max_results).execute()
    threads = results.get('threads', [])
    
    opportunities = []
    
    for t in threads:
        # On récupère tout l'historique de la conversation
        thread_data = service.users().threads().get(userId='me', id=t['id']).execute()
        messages = thread_data.get('messages', [])
        
        if not messages:
            continue
            
        last_message = messages[-1] # Le message le plus récent est toujours à la fin
        
        # 1. Vérifier si le dernier message a été envoyé par l'utilisateur
        # L'API Gmail ajoute le label "SENT" si le message vient de nous
        if 'SENT' not in last_message.get('labelIds', []):
            continue # Le dernier message ne vient pas de nous, on ignore (le prospect a répondu)
            
        # 2. Vérifier si le délai est dépassé
        # L'API renvoie la date en millisecondes depuis 1970
        timestamp_ms = int(last_message['internalDate'])
        last_date = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
        
        # On calcule la différence avec aujourd'hui
        time_elapsed = datetime.now(timezone.utc) - last_date
        
        if time_elapsed.days >= days_threshold:
            # === C'EST UNE OPPORTUNITÉ DE RELANCE ! ===
            
            # On extrait le sujet et le destinataire pour l'affichage
            headers = last_message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'Sans objet')
            to_email = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Inconnu')
            
            opportunities.append({
                "thread_id": t['id'],
                "subject": subject,
                "recipient": to_email,
                "last_message_date": last_date.strftime("%Y-%m-%d %H:%M"),
                "days_waiting": time_elapsed.days
            })
            
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