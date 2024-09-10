from flask import Flask, request, jsonify
from services.youtube_service import download_audio

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)

