import os
from cryptography.fernet import Fernet

# On récupère la clé secrète depuis les variables d'environnement
encryption_key = os.getenv("ENCRYPTION_KEY")

if not encryption_key:
    # Par sécurité, l'application refusera de démarrer s'il n'y a pas de clé
    raise ValueError("FATAL ERROR: ENCRYPTION_KEY manquante dans les variables d'environnement.")

# Initialisation de l'outil de chiffrement
cipher_suite = Fernet(encryption_key.encode())

def encrypt_token(token: str) -> str:
    """Chiffre un token en texte clair."""
    if not token:
        return token
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Déchiffre un token chiffré."""
    if not encrypted_token:
        return encrypted_token
    return cipher_suite.decrypt(encrypted_token.encode()).decode()