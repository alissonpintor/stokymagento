# config.py
import os
projectPath = os.path.dirname(os.path.abspath(__name__))


class Config(object):
    """
    Common configurations
    """

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    WTF_I18n_ENABLED = True
    UPLOAD_FOLDER = os.path.join(projectPath, 'uploads')
    UPLOADS_DEFAULT_DEST = 'uploads'
    UPLOADS_DEFAULT_URL = 'http://127.0.0.1:5000/uploads'
    # UPLOADS_DEFAULT_URL = "http://192.168.104.37:5000/uploads"
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = False
    USE_RELOADER = False
    WTF_I18n_ENABLED = True


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


app_config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
    }
