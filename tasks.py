import os
import logging
import asyncio
from celery.signals import task_success, task_failure
from services.youtube_service import download_audio, get_audio_duration
from services.google_transcription_service import transcribe_audio_google
from services.analyze_text_service import analyze_text
from db.models import User, db
from celery import shared_task
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def app_context():
    from main import app
    with app.app_context():
        yield

@shared_task(bind=True)
def download_and_process(self, url, prompt, user_id):
    logger.info('Starting task ---- download_and_process')
    audio_path = None
    audio_chunks = []
    try:
        with app_context():
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")

            self.update_state(state='PROGRESS', meta={'status': 'Downloading video'})
            audio_path = download_audio(url)

            self.update_state(state='PROGRESS', meta={'status': 'Transcribing audio'})
            transcript, audio_chunks = asyncio.run(transcribe_audio_google(audio_path))

            transcription_time_used = get_audio_duration(audio_path) / 60
            user.free_minutes = max(0, user.free_minutes - int(transcription_time_used))
            db.session.commit()

            self.update_state(state='PROGRESS', meta={'status': 'Analyzing transcript'})
            analysis = analyze_text(transcript, prompt)

            result = {
                'status': 'Completed',
                'result': {
                    'transcript': transcript,
                    'analysis': analysis,
                    'free_minutes_left': user.free_minutes,
                }
            }
            return result
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        self.update_state(state='FAILURE', meta={'status': str(e)})
        raise
    finally:
        cleanup_files(audio_path, audio_chunks)

def cleanup_files(audio_path, audio_chunks):
    try:
        if audio_path:
            wav_file = audio_path.replace('.mp3', '.wav')
            for file in [audio_path, wav_file]:
                if os.path.exists(file):
                    os.remove(file)
                    logger.info(f"Deleted local file: {file}")

        for chunk in audio_chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
                logger.info(f"Deleted local chunk: {chunk}")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    logger.info(f"Task {sender.name} completed successfully with result: {result}")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    logger.error(f"Task {sender.name} failed with exception: {exception}")
