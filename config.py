import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rewards-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///rewards.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    APP_NAME = 'Club Etla Rewards'
    
    POINTS_BREAKFAST = 10
    POINTS_TEA = 5
    POINTS_ALOE = 5
    POINTS_PROTEIN = 5
    
    LEVELS = {
        'BRONCE': {'min_visits': 0, 'max_visits': 19, 'discount': 0, 'icon': '🟢', 'color': '#8B8B8B'},
        'PLATA': {'min_visits': 20, 'max_visits': 49, 'discount': 5, 'icon': '🥈', 'color': '#C0C0C0'},
        'ORO': {'min_visits': 50, 'max_visits': 99, 'discount': 10, 'icon': '🥇', 'color': '#FFD700'},
        'DIAMANTE': {'min_visits': 100, 'max_visits': float('inf'), 'discount': 15, 'icon': '💎', 'color': '#B9F2FF'}
    }
    
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # ===== REFERIDOS =====
    REFERRAL_REWARD = 3  # Número de referidos válidos para premio
    REFERRAL_POINTS = 20  # Puntos por referido válido
