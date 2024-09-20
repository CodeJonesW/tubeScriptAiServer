# TubeScriptAI - Video Transcription and Analysis Service

This project is a web service that allows users to upload YouTube video URLs and receive transcripts along with AI-based analysis of the video content. It integrates with Google Cloud Speech-to-Text for audio transcription and OpenAI for text analysis. The system supports user authentication and limits the free transcription minutes for each user.

## Features

- **User Authentication**: Users can register and login using JWT-based authentication.
- **Video Transcription**: The backend downloads the audio from a YouTube video, transcribes it using Google Cloud Speech-to-Text, and returns the transcript.
- **AI Analysis**: Transcribed text is sent for analysis using an AI model.
- **Task Management**: Transcription and analysis are handled asynchronously using Celery.
- **Free Time Limitation**: Users are granted a limited number of free minutes for transcription, which is deducted as they use the service.

## Setup and Installation

### 1. Install Dependencies

Ensure that you have Python 3.9+ installed. Clone the repository, then create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a .env file with the following environment variables:

```bash
    CELERY_BROKER_URL=redis://localhost:6379/0
    CELERY_RESULT_BACKEND=redis://localhost:6379/0
    JWT_SECRET_KEY=your-secret-key
    OPENAI_API_KEY=your-openai-api-key
```

### 3. Start Flask Server

The Flask server handles user authentication, requests for processing, and status polling.

```bash
    python3 main.py
```

### 4. Start Celery worker

```bash
    celery -A app.celery worker --loglevel=info
```

### Run Tests

```bash
    python run_tests.py
```
