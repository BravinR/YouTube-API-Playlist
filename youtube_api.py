from google_auth_oauthlib import flow
from google.auth.transport.requests import Request 
from googleapiclient.discovery import build
import pickle
import os
from dotenv import load_dotenv

load_dotenv()
playlist_id = os.environ.get("playlist_id")

credentials = None
no_results = 29

if os.path.exists("token.pickle"):
  print("Loading Credentials From File...")
  with open("token.pickle", "rb") as token:
    credentials = pickle.load(token)

if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing Access Token...')
        credentials.refresh(Request())
    else:
        print('Fetching New Tokens...')
        flow = flow.InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=[
                'https://www.googleapis.com/auth/youtube'
            ]
        )

        flow.run_local_server(port=3000, prompt='consent',
                              authorization_prompt_message='')
        credentials = flow.credentials

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)

youtube = build('youtube', 'v3', credentials = credentials)

def trending_songs():
    most_popular = []
    trending = youtube.videos().list(
      part='snippet',
      chart = 'mostPopular',
      regionCode='US',
      videoCategoryId='10',
      maxResults = no_results
    ).execute()
    for x in range(no_results):
	    video_id = trending["items"][x]["id"]
	    most_popular.append(video_id)
    return most_popular

def add_video_to_playlist(videoID,playlistID):
    add_video_request=youtube.playlistItems().insert(
        part="snippet",
        body={
                'snippet': {
                  'playlistId': playlistID, 
                  'resourceId': {
                      'kind': 'youtube#video',
                      'videoId': videoID
                    }
                #'position': 0
                }
        }
    ).execute()



def creating_playlist():
    for x in range(no_results):
      most_popular = trending_songs()
      video_id = most_popular[x]
      add_video_to_playlist(video_id, playlist_id)

creating_playlist()




