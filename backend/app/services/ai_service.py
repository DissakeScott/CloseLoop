import os
import google.generativeai as genai

# Configuration de la clé API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("⚠️ ATTENTION : La variable GEMINI_API_KEY est introuvable !")

def get_best_model():
    """Demande à Google la liste exacte des modèles autorisés et choisit le plus rapide (Flash)."""
    available_models = []
    try:
        # On demande à Google ce à quoi on a droit
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                available_models.append(m.name)
        
        print("✅ Modèles autorisés :", available_models)
        
        # 1. On cherche en priorité la toute dernière version Flash (très rapide, gros quota)
        for m in available_models:
            if "models/gemini-2.5-flash" == m: return m
            
        # 2. Plan B : le raccourci vers la dernière version Flash stable
        for m in available_models:
            if "models/gemini-flash-latest" == m: return m
            
        # 3. Plan C : l'ancienne version Flash
        for m in available_models:
            if "models/gemini-2.0-flash" == m: return m
            
        # Si aucun favori n'est là, on prend le premier de la liste
        return available_models[0]
    except Exception as e:
        print("Impossible de lister les modèles :", e)
        return "models/gemini-2.5-flash"

def generate_draft(email_content: str, tone: str = "naturel") -> str:
    """Génère un brouillon de relance avec un ton spécifique"""
    
    tone_instructions = {
        "naturel": "Le ton doit être poli, naturel, professionnel, et sans aucune pression.",
        "formel": "Le ton doit être très soutenu, extrêmement poli et utiliser le vouvoiement de rigueur.",
        "direct": "Le ton doit être direct, persuasif, orienté résultat et aller droit au but sans fioriture.",
        "court": "Le message doit être extrêmement court (1 ou 2 phrases maximum), percutant et très rapide à lire."
    }
    
    instruction = tone_instructions.get(tone, tone_instructions["naturel"])
    
    prompt = f"""
    Tu es un expert en communication professionnelle et en vente.
    Voici le dernier email que j'ai envoyé à un contact, et qui est resté sans réponse :
    
    "{email_content}"
    
    Rédige un e-mail de relance.
    {instruction}
    Ne mets pas d'objet (Subject), génère uniquement le corps du message.
    Ne mets pas de balises inutiles, juste le texte prêt à être envoyé.
    """
    
    try:
        # On récupère le modèle blindé !
        model_name = get_best_model()
        print(f"🤖 L'IA lance la génération avec : {model_name}")
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("🚨" * 10)
        print(f"ERREUR CRITIQUE GEMINI : {str(e)}")
        print("🚨" * 10)
        raise Exception(f"Erreur Gemini : {str(e)}")