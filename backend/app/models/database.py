# backend/app/models/database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import datetime

load_dotenv()

# Connexion à la base de données Supabase
DATABASE_URL = os.getenv("DATABASE_URL")
# Petite correction nécessaire pour SQLAlchemy si l'URL commence par "postgres://" au lieu de "postgresql://"
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class OAuthState(Base):
    __tablename__ = "oauth_states"

    state = Column(String, primary_key=True, index=True)
    code_verifier = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# --- MODÈLE DE NOTRE TABLE UTILISATEUR ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True) # Google ne le donne qu'à la première connexion !
    expires_at = Column(DateTime)

# Fonction pour créer les tables automatiquement
def init_db():
    Base.metadata.create_all(bind=engine)

# Fonction pour obtenir une session de base de données dans nos routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()