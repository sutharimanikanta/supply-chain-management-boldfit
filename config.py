import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///boldfit_supply_chain.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "boldfit-secret-key-2024"

    # LLM Configuration - Groq Only
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
