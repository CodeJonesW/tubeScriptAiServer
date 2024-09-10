import yt_dlp as youtube_dl
import ffmpeg
import os

def download_audio(youtube_url):
    # Directory where audio will be stored
    output_dir = "downloads/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # need to add a check in the case the url input has something like a youtube playlist in it.
    # this could cause an unexpectedly large amount of files to download

    # youtube-dl options to download audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        video_id = info_dict.get("id", None)
        audio_file = os.path.join(output_dir, f"{video_id}.mp3")

    if not os.path.exists(audio_file):
        raise FileNotFoundError("Audio file could not be created")

    return audio_file
