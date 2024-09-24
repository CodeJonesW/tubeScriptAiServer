import yt_dlp as youtube_dl
import ffmpeg
import os
import logging

logger = logging.getLogger(__name__)

def download_audio(youtube_url):
    output_dir = "../tmp/downloads"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            logger.info(f"yt-dlp info_dict: {info_dict}")
            video_id = info_dict.get("id", None)
            audio_file = os.path.join(output_dir, f"{video_id}.mp3")
            logger.info(f"Audio file: {audio_file}")

        if not os.path.exists(audio_file):
            raise FileNotFoundError("Audio file could not be created")

        return audio_file
    except Exception as e:
        logger.error(f"Error downloading audio: {str(e)}")
        raise Exception(str(e))

def get_audio_duration(audio_file):
    probe = ffmpeg.probe(audio_file)
    audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    return float(audio_stream['duration'])
