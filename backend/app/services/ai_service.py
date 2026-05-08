import os
from google import genai
from google.genai import types
import json

# On récupère la clé API depuis les variables d'environnement
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("FATAL ERROR: GEMINI_API_KEY manquante dans le fichier .env")

# Initialisation du nouveau client Google GenAI
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_followup_draft(thread_summary: str, user_style_examples: list[str] = None) -> str:
    """
    Génère un brouillon de relance en imitant le style de l'utilisateur (RAG).
    """
    # 1. PRÉPARATION DU RAG (Clonage de style)
    style_context = ""
    if user_style_examples and len(user_style_examples) > 0:
        style_context = (
            "\n--- STYLE D'ÉCRITURE À CLONER ---\n"
            "Voici des exemples d'emails que j'ai écrits dans le passé. "
            "Analyse mon ton (formel ou décontracté), ma façon de dire bonjour et au revoir, "
            "la longueur de mes phrases et ma ponctuation. "
            "TU DOIS RÉDIGER LA RELANCE EXACTEMENT DANS CE STYLE, comme si c'était moi qui l'avais écrite :\n\n"
        )
        for i, example in enumerate(user_style_examples):
            style_context += f"Exemple {i+1}:\n{example}\n\n"
    else:
        # Style par défaut si c'est un nouvel utilisateur sans historique
        style_context = "\nÉcris avec un ton professionnel, clair, concis et légèrement chaleureux."

    # 2. CONSTRUCTION DU PROMPT MAÎTRE
    prompt = f"""
    Tu es un assistant expert en vente et en relance client.
    Ton but est de rédiger un email de relance (warm follow-up) pour un prospect qui ne répond plus.

    --- CONTEXTE DU FIL DE DISCUSSION ---
    {thread_summary}

    {style_context}

    --- RÈGLES STRICTES ---
    1. L'email doit être prêt à être envoyé (pas de balises [Nom du prospect] si tu connais son nom).
    2. Ne sois pas agressif, la relance doit sembler naturelle (peut-être un simple oubli du prospect).
    3. Vas droit au but.
    
    Rédige uniquement le corps de l'email, sans objet.
    """

    # 3. APPEL À LA NOUVELLE API GEMINI
    try:
        # On utilise gemini-2.5-flash (le plus rapide et le plus performant pour le texte)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Erreur Gemini lors de la génération : {str(e)}")
        # En production, on enverrait aussi cette erreur à Sentry !
        return "Une erreur est survenue lors de la génération du brouillon. Veuillez réessayer."

def analyze_thread_intent(prospect_snippet: str) -> dict:
    """
    Analyse le dernier message d'un prospect pour catégoriser son intention.
    """
    prompt = f"""
    Tu es un expert en analyse commerciale. Lis ce court extrait du dernier email d'un prospect : "{prospect_snippet}"
    
    Classe ce message dans l'une de ces 3 catégories strictes :
    - OUBLI : Le prospect semblait intéressé mais n'a pas donné suite (ex: "Je regarde", "Intéressant", demande de devis...).
    - ATTENTE : Le prospect a explicitement demandé du temps (ex: "En congé", "Recontactez-moi en septembre", "Pas le temps cette semaine").
    - OBJECTION : Le prospect exprime un frein ou un refus (ex: "Trop cher", "On a pris quelqu'un d'autre", "Pas besoin").

    Réponds UNIQUEMENT par un objet JSON valide (sans aucun formatage Markdown ou texte autour) au format exact suivant :
    {{"categorie": "OUBLI", "raison": "une phrase très courte de 6 mots max expliquant pourquoi"}}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # Nettoyage de la réponse au cas où Gemini rajoute des balises ```json ... ```
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
        
    except Exception as e:
        print(f"Erreur d'analyse d'intention : {e}")
        # Valeur de repli sécurisée en cas d'erreur de l'IA
        return {"categorie": "OUBLI", "raison": "Analyse non disponible"}