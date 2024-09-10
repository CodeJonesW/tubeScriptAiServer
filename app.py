import os
import logging
from flask import Flask, request, jsonify
from services.analyze_text_service import analyze_text
from services.youtube_service import download_audio
from services.google_transcription_service import transcribe_long_audio_google
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG) 

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'YouTube URL is required'}), 400

    try:
        audio_path = download_audio(url)
        return jsonify({'audio_path': audio_path}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe_google():
    audio_path = request.json.get('audio_path')
    if not audio_path:
        return jsonify({'error': 'Audio file path is required'}), 400
    
    bucket = os.getenv('GCP_SPEECH_TO_TEXT_PROCESSING_BUCKET')
    if not bucket:
        return jsonify({'error': 'gcp_bucket_required'}), 500
    
    try:
        transcript = transcribe_long_audio_google(bucket, audio_path)
        return jsonify({'transcript': transcript}), 200
    
    except Exception as e:
        app.logger.info("error: " + str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def download_transcribe_analysis():
    transcript = request.json.get('transcript')
    prompt = request.json.get('prompt')

    try:
        content = analyze_text(transcript, prompt)
        app.logger.info("analysis: " + content)
        return jsonify({'analysis': content}), 200
    
    except Exception as e:
        app.logger.info("error: " + str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

