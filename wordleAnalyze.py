import os
import json
import requests
from urllib.parse import urlparse, parse_qs
import isodate  # For parsing ISO 8601 duration format
import yt_dlp
from waSecrets import *

# You'll need a simple API key for metadata like duration
API_KEY = ytAPIKey  # Replace with your YouTube API key

def get_video_id(youtube_url):
    """Extract the video ID from a YouTube URL."""
    parsed_url = urlparse(youtube_url)
    
    # Handle different URL formats
    if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed_url.path[1:]
    if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif '/v/' in parsed_url.path:
            return parsed_url.path.split('/v/')[1]
        elif 'embed' in parsed_url.path:
            return parsed_url.path.split('/embed/')[1]
    
    return youtube_url

def get_video_metadata(video_id):
    """
    Get video metadata including duration using the YouTube API.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Dictionary with video metadata or error
    """
    try:
        # Use the YouTube Data API to get video details
        url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=contentDetails,snippet&key={API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if 'items' not in data or not data['items']:
            return {'success': False, 'error': 'Video not found or API error'}
        
        video_data = data['items'][0]
        duration_iso = video_data['contentDetails']['duration']  # ISO 8601 format
        
        # Convert ISO 8601 duration to seconds
        duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())

        #convert duration seconds to hh:mm:ss
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"      
        
        return {
            'success': True,
            'video_id': video_id,
            'title': video_data['snippet']['title'],
            'channel': video_data['snippet']['channelTitle'],
            'duration': duration_formatted
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

import yt_dlp

def download_youtube_video(url, output_path="downloads"):
    """Downloads a YouTube video using yt-dlp."""
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Get best quality video & audio
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Save with video title
        'merge_output_format': 'mp4',  # Ensure MP4 format
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Main Program
if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=Rz-ESn7_F0k"
    video_id = get_video_id(youtube_url)
    metadata = get_video_metadata(video_id)
    print(json.dumps(metadata, indent=4))

    #video_url = input("Enter YouTube video URL: ")
    download_youtube_video(youtube_url)
    print("Download complete!")