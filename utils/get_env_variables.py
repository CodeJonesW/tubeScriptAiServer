import os
from google.cloud import secretmanager

def get_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.getenv('PROJECT_ID')}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def load_secrets():
    if os.getenv('FLASK_ENV') == 'production':
        CELERY_BROKER_URL = get_secret('CELERY_BROKER_URL')
        CELERY_RESULT_BACKEND = get_secret('CELERY_RESULT_BACKEND')
        SQLALCHEMY_DATABASE_URI = get_secret('SQLALCHEMY_DATABASE_URI')
        JWT_SECRET_KEY = get_secret('JWT_SECRET_KEY')
        SQLALCHEMY_TRACK_MODIFICATIONS=False
        OPEN_AI_API_KEY = get_secret('OPEN_AI_API_KEY')
        FRONTEND_URL = get_secret('FRONTEND_URL')
        

    else:
        CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
        CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///users.db')
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
        OPEN_AI_API_KEY = os.getenv('OPENAI_API_KEY')
        FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    return {
        "CELERY_BROKER_URL": CELERY_BROKER_URL,
        "CELERY_RESULT_BACKEND": CELERY_RESULT_BACKEND,
        "SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_URI,
        "JWT_SECRET_KEY": JWT_SECRET_KEY,
        "SQLALCHEMY_TRACK_MODIFICATIONS": SQLALCHEMY_TRACK_MODIFICATIONS,
        "OPEN_AI_API_KEY": OPEN_AI_API_KEY,
        "FRONTEND_URL": FRONTEND_URL
    }
