from celery import Celery
from celery.signals import task_success, task_failure
from services.youtube_service import download_audio
from services.google_transcription_service import delete_gcs_file, transcribe_audio_google
from google.cloud import storage
from services.analyze_text_service import analyze_text
import os
import logging
import asyncio

celery = Celery('tasks', broker='redis://localhost:6379/0')
logger = logging.getLogger(__name__)

@celery.task(bind=True)
def download_and_process(self, url, prompt):
    """Handles downloading, transcribing, and analyzing the video asynchronously."""
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Downloading video'})
        try:
            audio_path = download_audio(url)
        except Exception as e:
            raise Exception(f"Error downloading audio: {str(e)}")

        self.update_state(state='PROGRESS', meta={'status': 'Transcribing audio'})
        
        transcript, audio_chunks = asyncio.run(transcribe_audio_google(bucket, audio_path))

        self.update_state(state='PROGRESS', meta={'status': 'Analyzing transcript'})
        analysis = analyze_text(transcript, prompt)

        return {
            'status': 'Completed',
            'result': {
                'transcript': transcript,
                'analysis': analysis,
                'file_path': audio_path,
                'audio_chunks': audio_chunks  # Include chunk paths for cleanup
            }
        }

    except Exception as e:
        logger.error(f"Task failed: {str(e)}")

@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    logger.info(f"Task {sender.name} completed successfully with result: {result}")
    try:
        file_path = result['result']['file_path']
        audio_chunks = result['result'].get('audio_chunks', [])
        # Delete the original MP3 and WAV files locally
        if file_path:
            logger.info('Cleaning up local files after task success...')
            wav_file = file_path.replace('.mp3', '.wav')
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted local MP3: {file_path}")
            if os.path.exists(wav_file):
                os.remove(wav_file)
                logger.info(f"Deleted local WAV: {wav_file}")

        # Delete chunk files locally
        for chunk in audio_chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
                logger.info(f"Deleted local chunk: {chunk}")


    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **other_kwargs):
    logger.error(f"Task {sender.name} failed with exception: {exception}")
    try:
        file_path = kwargs.get('file_path')
        audio_chunks = kwargs.get('audio_chunks', [])

        # Clean up locally
        if file_path:
            logger.info('Cleaning up local files after task failure...')
            wav_file = file_path.replace('.mp3', '.wav')
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted local MP3: {file_path}")
            if os.path.exists(wav_file):
                os.remove(wav_file)
                logger.info(f"Deleted local WAV: {wav_file}")

        # Delete chunk files locally
        for chunk in audio_chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
                logger.info(f"Deleted local chunk: {chunk}")


    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
