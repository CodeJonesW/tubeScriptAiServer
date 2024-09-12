from celery import Celery
from services.youtube_service import download_audio
from services.google_transcription_service import transcribe_long_audio_google
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

        return {'status': 'Completed', 'result': {'transcript': transcript, 'analysis': analysis}}

    except Exception as e:
        raise self.retry(exc=e)
    
#     finally:
#         # Ensure the file is deleted from the GCP bucket after the task completes
#         try:
#             delete_gcs_file(bucket, audio_path)
#             print(f"Deleted file {audio_path} from GCP bucket")
#         except Exception as delete_error:
#             print(f"Error while deleting file {audio_path} from GCP bucket: {delete_error}")


# def delete_gcs_file(bucket_name, file_path):
#     """Deletes a file from the GCP bucket."""
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(file_path)

#     blob.delete()

#     print(f"File {file_path} deleted from bucket {bucket_name}.")

