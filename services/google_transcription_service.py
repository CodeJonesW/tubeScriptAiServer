import os
import logging
from google.cloud import speech, storage
import ffmpeg

logger = logging.getLogger(__name__)

# Set environment variable for Google credentials
os.getenv("GOOGLE_APPLICATION_CREDENTIALS") 

def check_file_size(file_path, max_size_mb=9.99):
    """Check if the file size exceeds the specified max size in MB."""
    file_size = os.path.getsize(file_path)  # Size in bytes
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    if file_size > max_size_bytes:
        raise Exception(f"File size exceeds {max_size_mb}MB limit. File size: {file_size / (1024 * 1024):.2f}MB")
    return True

def convert_mp3_to_wav(mp3_file_path):
    """Convert MP3 at a given file path to WAV format."""
    try:
        # Ensure the file exists
        if not os.path.isfile(mp3_file_path):
            raise FileNotFoundError(f"The file {mp3_file_path} does not exist.")
        
        # Define the output wav file path
        wav_file_path = mp3_file_path.replace(".mp3", ".wav")
        
        # Log the conversion start
        logger.info(f"Converting {mp3_file_path} to {wav_file_path}...")
        
        # Run the ffmpeg conversion
        ffmpeg.input(mp3_file_path).output(wav_file_path, ac=1, ar=16000).run(overwrite_output=True)
        
        # Log success message
        logger.info(f"Conversion successful: {mp3_file_path} -> {wav_file_path}")
        
        return wav_file_path
    
    except Exception as e:
        # Log the error if the conversion fails
        logger.error(f"Error converting {mp3_file_path} to WAV: {str(e)}")
        raise

def upload_to_gcs(bucket_name, audio_file):
    """Upload the audio file to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(os.path.basename(audio_file))
    blob.upload_from_filename(audio_file)

    gcs_uri = f"gs://{bucket_name}/{blob.name}"
    logger.info(f"Uploaded {audio_file} to {gcs_uri}")
    return gcs_uri

def transcribe_long_audio_google(bucket_name, audio_file):
    """Transcribe audio longer than 60 seconds using LongRunningRecognize."""
    # Convert MP3 to WAV for better accuracy
    wav_file = convert_mp3_to_wav(audio_file)

    # Upload audio file to Google Cloud Storage
    gcs_uri = upload_to_gcs(bucket_name, wav_file)

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # Use LINEAR16 for WAV files
        sample_rate_hertz=16000, 
        language_code="en-US"
    )

    # Use LongRunningRecognize for audio longer than 1 minute
    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=600)
    logger.info(response)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + "\n"

    return transcript
