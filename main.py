import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from celery_config import make_celery
from dotenv import load_dotenv
from tasks import download_and_process
from db.models import db, User
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from utils.get_env_variables import load_secrets

secrets = load_secrets()

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    logger.info('createing app - main.py')
    logger.info(f"secrets: {secrets['CELERY_BROKER_URL']}")
    logger.info(f"secrets: {secrets['CELERY_RESULT_BACKEND']}")

    load_dotenv()

    app.config.update(
        CELERY_BROKER_URL=secrets['CELERY_BROKER_URL'],
        CELERY_RESULT_BACKEND=secrets['CELERY_RESULT_BACKEND'],
        SQLALCHEMY_DATABASE_URI=secrets['SQLALCHEMY_DATABASE_URI'],
        SQLALCHEMY_TRACK_MODIFICATIONS=secrets['SQLALCHEMY_TRACK_MODIFICATIONS'],
        JWT_SECRET_KEY=secrets['JWT_SECRET_KEY'],
    )

    db.init_app(app) 
    jwt = JWTManager(app)

    CORS(app, resources={r"/*": {"origins": secrets['FRONTEND_URL']}})

    celery = make_celery(app) 

    with app.app_context():
        db.create_all()

    return app, celery

def register_routes(app):
    @app.route('/register', methods=['POST'])
    def register():
        username = request.json.get('username')
        password = request.json.get('password')
    
        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"message": "User already exists"}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password=hashed_password, free_minutes=10)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    
    @app.route('/login', methods=['POST'])
    def login():
        username = request.json.get('username')
        password = request.json.get('password')

        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"message": "Invalid credentials"}), 401

        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token), 200

    @app.route('/process', methods=['POST'])
    @jwt_required()
    def process_video():
        logger.info('Processing video')
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user['username']).first()
        logger.info('User found in db')

        if user.free_minutes <= 0:
            return jsonify({'error': 'You have exhausted your free transcription time. Please purchase more time.'}), 403

        url = request.json.get('url')
        prompt = request.json.get('prompt')

        if not url or not prompt:
            return jsonify({'error': 'YouTube URL and prompt are required'}), 400

        task = download_and_process.apply_async(args=[url, prompt, user.id])

        return jsonify({'task_id': task.id}), 202

    @app.route('/status/<task_id>')
    @jwt_required()
    def task_status(task_id):
        task = download_and_process.AsyncResult(task_id)
        if task is None:
            response = {
                'state': 'NOT FOUND',
                'status': 'Task not found'
            }
            return jsonify(response)
        
        logger.info(f'Task: {task}\nTask State: {task.state}\nTask Info: {task.info}')

        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Pending...'
            }

        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'result': task.info.get('result', ''),
                'status': task.info.get('status', 'Processing...'),
            }
            
        else:
            response = {
                'state': task.state,
                'status': str(task.info) 
            }

        return jsonify(response)


    @app.route('/profile', methods=['GET'])
    @jwt_required()
    def profile():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user['username']).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        return jsonify({
            'username': user.username,
            'free_minutes': user.free_minutes
        }), 200
    
    return app

app, celery = create_app()
register_routes(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
