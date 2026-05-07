# 🔄 CloseLoop

> **Seamless Connection. Enduring Value.**
> 
> CloseLoop est un MVP (Minimum Viable Product) de type SaaS conçu pour automatiser et optimiser les relances d'e-mails professionnels. En analysant votre boîte d'envoi Gmail, l'application détecte les e-mails restés sans réponse et génère des brouillons de relance sur mesure grâce à l'Intelligence Artificielle.

<div align="center">
  
  ![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
  ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
  ![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
  ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
  
  ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
  ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
  ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
  
  ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
  ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

</div>

---

## 🎯 Pourquoi ce projet ?

Ce projet a été développé de A à Z pour démontrer des compétences en architecture **Full-Stack**, en intégration d'**API tierces complexes** (Google Workspace), et en implémentation de fonctionnalités d'**Intelligence Artificielle générative** (LLMs). 



---

## ✨ Fonctionnalités Principales

* **🔐 Authentification Sécurisée :** Connexion via Google OAuth 2.0 (récupération de l'identité et des tokens d'accès sécurisés).
* **📡 Synchronisation Gmail :** Analyse automatique des fils de discussion (Threads) pour identifier les e-mails envoyés sans réponse depuis plusieurs jours.
* **🧠 Moteur d'IA (Google Gemini) :** Génération de brouillons de relance contextuels basés sur l'historique des échanges.
* **🎛️ Personnalisation du Ton :** Ajustement dynamique du comportement de l'IA selon 4 tons : *Naturel*, *Formel*, *Direct*, ou *Très court*.
* **🛡️ Human-in-the-loop :** Modale de relecture et d'édition manuelle avant l'envoi définitif via l'API Gmail.
* **🚀 Expérience Utilisateur (UX) :** Interface moderne, responsive, avec gestion des états de chargement (Loaders) et notifications non-bloquantes (Toasts).

---

## 🛠️ Stack Technique

### Frontend
* **Framework :** Next.js 14 / React
* **Langage :** TypeScript
* **Stylisation :** Tailwind CSS
* **Icônes :** Lucide React

### Backend
* **Framework :** FastAPI (Python)
* **IA :** API Google Generative AI (Modèles Gemini Flash)
* **Intégration :** Google API Python Client (Gmail API)

### Base de Données
* **SGBD :** PostgreSQL (hébergé via Supabase)
* **ORM :** SQLAlchemy

---

## 🚀 Installation et Lancement en local

### Prérequis
* [Node.js](https://nodejs.org/) (v18+)
* [Python](https://www.python.org/) (3.10+)
* Un projet sur la [Google Cloud Console](https://console.cloud.google.com/) avec les API Gmail et Google+ activées.
* Une clé API [Google AI Studio](https://aistudio.google.com/) (Gemini) avec facturation activée pour l'Europe.
* Une base de données PostgreSQL (ex: Supabase).

### 1. Configuration du Backend (Python)

```bash
# Se déplacer dans le dossier backend
cd backend

# Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
