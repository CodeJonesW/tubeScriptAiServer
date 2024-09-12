import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from celery_config import make_celery
from dotenv import load_dotenv
from tasks import download_and_process

load_dotenv()
app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

celery = make_celery(app)

logging.basicConfig(level=logging.DEBUG)

@app.route('/process', methods=['POST'])
def process_video():
    url = request.json.get('url')
    prompt = request.json.get('prompt')

    if not url or not prompt:
        return jsonify({'error': 'YouTube URL and prompt are required'}), 400

    # Enqueue the task
    task = download_and_process.apply_async(args=[url, prompt])
    
    # Return the task ID immediately to the client
    return jsonify({'task_id': task.id}), 202

@app.route('/status/<task_id>')
def task_status(task_id):
    task = download_and_process.AsyncResult(task_id)
    print('Task :', task)
    print('Task State:', task.state)
    print('Task Info:', task.info)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.info.get('result', ''),
            'status': task.info.get('status', 'Processing...')
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)  # Task error details
        }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
