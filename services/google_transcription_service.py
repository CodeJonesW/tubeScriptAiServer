import os
import logging
import asyncio
from google.cloud import speech, storage
import ffmpeg
from concurrent.futures import ThreadPoolExecutor
import math

logger = logging.getLogger(__name__)

# ThreadPoolExecutor for running blocking IO operations
executor = ThreadPoolExecutor(max_workers=32)

def split_audio_into_chunks(input_audio_file, chunk_length=30):
    """Split the audio file into chunks of specified length (in seconds)."""
    probe = ffmpeg.probe(input_audio_file)
    duration = float(probe['format']['duration'])
    
    num_chunks = math.ceil(duration / chunk_length)
    
    chunk_files = []
    for i in range(num_chunks):
        start_time = i * chunk_length
        output_chunk = f"{input_audio_file.replace('.wav', '')}_chunk{i}.wav"
        (
            ffmpeg
            .input(input_audio_file, ss=start_time, t=chunk_length)
            .output(output_chunk)
            .run(overwrite_output=True)
        )
        chunk_files.append(output_chunk)

    return chunk_files

async def transcribe_audio_chunk(audio_chunk):
    """Asynchronously transcribe a single audio chunk."""
    client = speech.SpeechClient()

    # Read the audio chunk file as binary content
    with open(audio_chunk, "rb") as audio_file:
        audio_content = audio_file.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US"
    )

    # Synchronous transcription offloaded to thread pool
    response = await asyncio.get_event_loop().run_in_executor(
        executor, lambda: client.recognize(config=config, audio=audio)
    )
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + "\n"

    return transcript

async def transcribe_audio_google(audio_file, chunk_length=30):
    """Asynchronously transcribe long audio by splitting into chunks and transcribing each."""
    # Convert MP3 to WAV
    wav_file = convert_mp3_to_wav(audio_file)

    # Split the WAV file into smaller chunks
    audio_chunks = split_audio_into_chunks(wav_file, chunk_length)

    # Asynchronously transcribe each chunk
    transcript = ""
    tasks = [transcribe_audio_chunk(chunk) for chunk in audio_chunks]
    
    # Gather results asynchronously
    results = await asyncio.gather(*tasks)

    # Combine all transcriptions
    for result in results:
        transcript += result

    return transcript, audio_chunks

def convert_mp3_to_wav(mp3_file_path):
    """Convert MP3 at a given file path to WAV format."""
    try:
        if not os.path.isfile(mp3_file_path):
            raise FileNotFoundError(f"The file {mp3_file_path} does not exist.")
        
        wav_file_path = mp3_file_path.replace(".mp3", ".wav")
        
        ffmpeg.input(mp3_file_path).output(wav_file_path, ac=1, ar=16000).run(overwrite_output=True)
        
        return wav_file_path
    
    except Exception as e:
        logger.error(f"Error converting {mp3_file_path} to WAV: {str(e)}")
        raise
