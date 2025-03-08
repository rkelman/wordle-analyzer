import os
from youtube_transcript_api import YouTubeTranscriptApi
import json
from urllib.parse import urlparse, parse_qs
import requests
import isodate  # For parsing ISO 8601 duration format
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
            return {
                'success': False,
                'error': 'Video not found or API error'
            }
        
        video_data = data['items'][0]
        duration_iso = video_data['contentDetails']['duration']  # ISO 8601 format like 'PT4M13S'
        
        # Convert ISO 8601 duration to seconds
        duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())
        
        # Format duration in a readable format (HH:MM:SS)
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"
        
        return {
            'success': True,
            'video_id': video_id,
            'title': video_data['snippet']['title'],
            'channel': video_data['snippet']['channelTitle'],
            'duration_iso': duration_iso,
            'duration_seconds': duration_seconds,
            'duration_formatted': duration_formatted
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_video_data(video_id_or_url, languages=['en']):
    """
    Fetch both transcript and metadata for a YouTube video.
    
    Args:
        video_id_or_url: YouTube video ID or URL
        languages: List of language codes to try fetching (default: ['en'])
        
    Returns:
        Dictionary with transcript text, metadata, and video information
    """
    # Extract video ID if URL was provided
    video_id = get_video_id(video_id_or_url)
    
    # Get video metadata (including duration)
    metadata = get_video_metadata(video_id)
    
    # Get transcript
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get transcript in one of the specified languages
        transcript_data = None
        language_found = None
        
        for lang in languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                transcript_data = transcript.fetch()
                language_found = transcript.language
                break
            except Exception:
                continue
                
        # If all specified languages failed, try to get any available transcript
        if not transcript_data:
            try:
                transcript = transcript_list.find_transcript([])  # Get default transcript
                transcript_data = transcript.fetch()
                language_found = transcript.language
            except Exception as e:
                return {
                    'success': False,
                    'video_id': video_id,
                    'metadata': metadata if metadata['success'] else {'error': metadata['error']},
                    'transcript': {
                        'success': False,
                        'error': 'No transcript found for specified languages'
                    }
                }
        
        # Format the transcript
        full_text = ' '.join([item['text'] for item in transcript_data])
        
        return {
            'success': True,
            'video_id': video_id,
            'metadata': metadata,
            'transcript': {
                'success': True,
                'language': language_found,
                'text': full_text,
                'data': transcript_data  # Detailed data with timestamps
            }
        }
            
    except Exception as e:
        return {
            'success': False,
            'video_id': video_id,
            'metadata': metadata if metadata['success'] else {'error': metadata['error']},
            'transcript': {
                'success': False,
                'error': str(e)
            }
        }

# Example usage
if __name__ == "__main__":
    # Example URL or video ID
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Get complete video data (transcript and metadata including duration)
    result = get_video_data(youtube_url, languages=['en', 'en-US', 'en-GB'])
    
    if result['success']:
        # Print video information
        meta = result['metadata']
        print(f"Title: {meta['title']}")
        print(f"Channel: {meta['channel']}")
        print(f"Duration: {meta['duration_formatted']} ({meta['duration_seconds']} seconds)")
        
        # Print transcript info
        trans = result['transcript']
        print(f"\nTranscript language: {trans['language']}")
        print(f"Transcript preview: {trans['text'][:300]}...")
        
        # Save to file (optional)
        with open("video_data.json", "w") as f:
            json.dump(result, f, indent=2)
        print("\nFull data saved to video_data.json")
    else:
        print("Error occurred:")
        if not result['metadata']['success']:
            print(f"  Metadata error: {result['metadata']['error']}")
        if not result['transcript']['success']:
            print(f"  Transcript error: {result['transcript']['error']}")