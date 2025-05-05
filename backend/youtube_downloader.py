from dotenv import load_dotenv
import yt_dlp
import os
from urllib.parse import urlparse, parse_qs
import re

load_dotenv()


def download_audio(youtube_url):
    """
    Download MP3 audio from a YouTube URL using yt-dlp library.

    Args:
        youtube_url (str): The YouTube URL to download audio from

    Returns:
        str: Absolute path to the downloaded MP3 file
    """

    output_folder = "audio"
    video_id = extract_video_id(youtube_url)
    output_path = os.path.abspath(os.path.join(output_folder, video_id))

    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Configure yt-dlp options
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": output_path,
        "quiet": False,
    }

    # Download the audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
        return output_path + ".mp3"


def extract_video_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    video_id = query_params.get("v")
    if video_id:
        return video_id[0]  # because parse_qs returns a list
    return None


def extract_first_youtube_url(prompt: str) -> str | None:
    """
    Extracts the first full YouTube video URL in the standard format.
    """
    match = re.search(r"https://www\.youtube\.com/watch\?v=[\w-]+", prompt)
    return match.group(0) if match else None
