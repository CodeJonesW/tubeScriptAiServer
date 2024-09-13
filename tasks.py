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
        print('Downloaded audio file:', audio_path)

        self.update_state(state='PROGRESS', meta={'status': 'Transcribing audio'})
        bucket = os.getenv('GCP_SPEECH_TO_TEXT_PROCESSING_BUCKET')
        transcript = transcribe_long_audio_google(bucket, audio_path)
        print('Transcript:', transcript)

        self.update_state(state='PROGRESS', meta={'status': 'Analyzing transcript'})
        analysis = analyze_text(transcript, prompt)
        print('Analysis:', analysis)

        return {'status': 'Completed', 'result': {'transcript': transcript, 'analysis': analysis, 'file_path': audio_path}}

    except Exception as e:
        raise self.retry(exc=e)


# Signal to handle task success
@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    print(f"Task {sender.name} completed successfully with result: {result}")
    try:
        bucket = os.getenv('GCP_SPEECH_TO_TEXT_PROCESSING_BUCKET')
        file_path = result['result']['file_path']

        if file_path:
            print('Deleting file locally...')
            wav_file = file_path.replace('.mp3', '.wav')
            os.remove(file_path)
            os.remove(wav_file)
    
        if bucket and file_path:
            delete_gcs_file(bucket, wav_file.split('/')[-1])

    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

# Signal to handle task failure
@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **other_kwargs):
    print(f"Task {sender.name} failed with exception: {exception}")

    # # Assuming that 'url' and 'prompt' are passed in kwargs, and you can extract the file path
    # # based on the URL provided. This can vary based on your logic.
    # bucket = os.getenv('GCP_SPEECH_TO_TEXT_PROCESSING_BUCKET')
    # file_path = kwargs.get('file_path')

    # # Perform the GCS file deletion in case of failure (optional)
    # if bucket_name and file_path:
    #     delete_gcs_file(bucket_name, file_path)