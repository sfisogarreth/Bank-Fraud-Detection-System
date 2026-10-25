import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-me')
    DATABASE = os.path.join(BASE_DIR, 'mazi.db')
    DB_PATH = DATABASE  # Alias for cross-module compatibility
    MODEL_PATH = os.getenv('MODEL_PATH', os.path.join(BASE_DIR, 'models', 'fraud_model.pkl'))
    FRAUD_THRESHOLD = int(os.getenv('FRAUD_THRESHOLD', 75))
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # True only with HTTPS


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}