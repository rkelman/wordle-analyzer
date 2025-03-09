#version 0.0.1 - empty shell for Python analyzing Youtube Wordle videos; when provided youtube URL

#prereq's:
    - must have loaded youtube libraries to access google's API libraries using: 
    > pip install youtube-transcript-api requests isodate
    > pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
    > pip install yt-dlp
    > pip install opencv-python numpy matplotlib


#Custom Configs: 
#   - cp waSecrets.example.py waSecrets.py
#   = update waSecrets.py with:
#       - Google (Youtube) API Client Key; ytAPIKey = ""
