from celery import Celery
from celery.signals import task_success, task_failure
from services.youtube_service import download_audio
from services.google_transcription_service import delete_gcs_file, transcribe_long_audio_google
from google.cloud import storage
from services.analyze_text_service import analyze_text
import os

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task(bind=True)
def download_and_process(self, url, prompt):
    """Handles downloading, transcribing, and analyzing the video asynchronously."""
    try:
        print('Downloading and processing video...')
        self.update_state(state='PROGRESS', meta={'status': 'Downloading video'})
        audio_path = download_audio(url)

        self.update_state(state='PROGRESS', meta={'status': 'Transcribing audio'})
        bucket = os.getenv('GCP_SPEECH_TO_TEXT_PROCESSING_BUCKET')
        transcript, audio_chunks = transcribe_long_audio_google(bucket, audio_path)

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
        raise self.retry(exc=e)


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    print(f"Task {sender.name} completed successfully with result: {result}")
    try:
        bucket = os.getenv('GCP_SPEECH_TO_TEXT_PROCESSING_BUCKET')
        file_path = result['result']['file_path']
        audio_chunks = result['result'].get('audio_chunks', [])
        # Delete the original MP3 and WAV files locally
        if file_path:
            print('Cleaning up local files after task success...')
            wav_file = file_path.replace('.mp3', '.wav')
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted local MP3: {file_path}")
            if os.path.exists(wav_file):
                os.remove(wav_file)
                print(f"Deleted local WAV: {wav_file}")

        # Delete chunk files locally
        for chunk in audio_chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
                print(f"Deleted local chunk: {chunk}")

        # Clean up GCS
        if bucket:
            for chunk in audio_chunks:
                chunk_name = chunk.split('/')[-1]
                delete_gcs_file(bucket, chunk_name)

    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **other_kwargs):
    print(f"Task {sender.name} failed with exception: {exception}")
    try:
        bucket = os.getenv('GCP_SPEECH_TO_TEXT_PROCESSING_BUCKET')
        file_path = kwargs.get('file_path')
        audio_chunks = kwargs.get('audio_chunks', [])

        # Clean up locally
        if file_path:
            print('Cleaning up local files after task failure...')
            wav_file = file_path.replace('.mp3', '.wav')
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted local MP3: {file_path}")
            if os.path.exists(wav_file):
                os.remove(wav_file)
                print(f"Deleted local WAV: {wav_file}")

        # Delete chunk files locally
        for chunk in audio_chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
                print(f"Deleted local chunk: {chunk}")

        # Clean up GCS
        if bucket:
            for chunk in audio_chunks:
                chunk_name = chunk.split('/')[-1]
                delete_gcs_file(bucket, chunk_name)

    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
