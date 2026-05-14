# 🔄 MailtiVoo

> **Seamless Connection. Enduring Value.**
> 
> MailtiVoo is a fully functional SaaS application designed to help professionals manage their email follow-ups effortlessly. By leveraging the Gmail API and Generative AI, MailtiVoo scans your inbox for unanswered emails and automatically generates highly contextual draft responses.

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

# 🚀 MailtiVoo - AI-Powered Email Follow-Up SaaS

![MailtiVoo Banner](https://via.placeholder.com/1200x400?text=MailtiVoo+-+Never+Miss+a+Follow-Up)


## ✨ Key Features

* **Smart Inbox Scanning:** Securely integrates with the Gmail API via OAuth2 to detect emails that require a follow-up.
* **AI-Generated Drafts:** Utilizes Large Language Models (LLMs) to understand context and generate polite, personalized follow-up drafts directly in your Gmail account.
* **User-Centric Dashboard:** A clean, responsive, and intuitive interface to manage email scans and review generated drafts.
* **Secure Subscription Model:** Fully integrated with Stripe for secure and seamless payment processing and subscription management.
* **Automated Workflows:** Background cron jobs to maintain service availability and trigger periodic inbox checks.

## 🛠️ Tech Stack

### Frontend
* **Framework:** Next.js 14 (React)
* **Styling:** Tailwind CSS
* **Icons:** Lucide React
* **Hosting:** Vercel

### Backend
* **Framework:** FastAPI (Python)
* **Authentication:** Google OAuth2
* **Integrations:** Google Cloud Platform (Gmail API `readonly` & `compose`), Stripe API
* **Hosting:** Render

## 🚀 Getting Started (Local Development)

### Prerequisites
* Node.js & npm
* Python 3.9+
* Google Cloud Console account (for OAuth credentials)
* Stripe Developer account

### 1. Clone the repository
```bash
git clone [https://github.com/your-username/mailtivoo.git](https://github.com/your-username/mailtivoo.git)
cd mailtivoo### Base de Données
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
