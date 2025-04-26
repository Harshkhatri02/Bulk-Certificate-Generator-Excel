import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.getenv('PERMANENT_SESSION_LIFETIME', 1800)))
    SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'False').lower() == 'true'
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    # Add any production-specific settings here

# Select configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 