# TubeScriptAI - Video Transcription and Analysis Service

This project is a web service that allows users to upload YouTube video URLs and receive transcripts along with AI-based analysis of the video content. It integrates with Google Cloud Speech-to-Text for audio transcription and OpenAI for text analysis. The system supports user authentication and limits the free transcription minutes for each user.

---

## Features

- **User Authentication**: Users can register and login using JWT-based authentication.
- **Video Transcription**: The backend downloads the audio from a YouTube video, transcribes it using Google Cloud Speech-to-Text, and returns the transcript.
- **AI Analysis**: Transcribed text is sent for analysis using an AI model.
- **Task Management**: Transcription and analysis are handled asynchronously using Celery.
- **Free Time Limitation**: Users are granted a limited number of free minutes for transcription, which is deducted as they use the service.

---

## Setup and Installation

### 1. Make sure you have Docker and Docker Compose installed

### 2. Provide Google Cloud credentials

Download a google application credentials file from the Google Cloud Console and save it in location of choice. GCP Speech-to-Text API should be enabled.

### 3. Provide OpenAI API Key

Get an API key from OpenAI and save it.

### 4. Set Environment Variables

Create a .env file with the following environment variables:

```bash
    JWT_SECRET_KEY=your-secret-key
    OPENAI_API_KEY=your-openai-api-key
    POSTGRES_DB=database
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    PATH_TO_GOOGLE_APPLICATION_CREDENTIALS=path-to-google-credentials.json
```

### 5. Download Docker Images

- docker pull codejonesw/tubescript-ai-backend
- docker pull codejonesw/tubescript-ai-frontend
- docker pull codejonesw/tubescript-ai-worker

### 6. Run Compoose

- docker compose up

---

### Run Unit Tests

```bash
    python run_tests.py
```

---
