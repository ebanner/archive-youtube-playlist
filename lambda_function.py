import json

import google.oauth2.credentials
import googleapiclient.discovery
from google.auth.transport.requests import Request

import boto3


WATCH_NEXT_PLAYLIST = 'PLkd5S9lUKlOAHYE97mzLKaAIdjhHaXWXS'
ARCHIVE_PLAYLIST = 'PLkd5S9lUKlOArJsazeSVyZ1syXY2yxdyC'

secrets_client = boto3.client("secretsmanager")

SECRET_NAME = 'ArchiveWatchNextYouTubePlaylist'

def get_secret(secret_key):
    response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
    result = response['SecretString']
    secrets = json.loads(result)
    return secrets[secret_key]

def update_secret(secret_key, secret_value):
    return secrets_client.update_secret(
        SecretId=SECRET_NAME,
        SecretString=json.dumps({secret_key: secret_value})
    )

credentials_json = get_secret('tokens.json')
credentials_dict = json.loads(credentials_json)

credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(credentials_dict)
if credentials.expired:
    credentials.refresh(Request()) # Refresh the access token
    update_secret('tokens.json', credentials.to_json())

youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)


def get_watch_next_videos():
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=WATCH_NEXT_PLAYLIST,
        maxResults=50,
    )
    videos = request.execute()
    videos = [{'playlist_item_id': video['id'], 'video_id': video['snippet']['resourceId']['videoId']} for video in videos['items']]
    return videos


def add_to_archive(video_id):
    print(f'Archiving {video_id}...')
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
          "snippet": {
            "playlistId": ARCHIVE_PLAYLIST,
            "position": 0,
            "resourceId": {
              "kind": "youtube#video",
              "videoId": video_id
            }
          }
        }
    )
    response = request.execute()
    return response


def remove_from_watch_next(playlist_item_id):
    print(f'Removing {playlist_item_id} from Watch next...')
    request = youtube.playlistItems().delete(
        id=playlist_item_id
    )
    response = request.execute()
    return response


def lambda_handler(event, context):
    watch_next_videos = get_watch_next_videos()
    print(f'Watch next videos = {watch_next_videos}')
    for watch_next_video in watch_next_videos:
        add_to_archive(watch_next_video['video_id'])
        remove_from_watch_next(watch_next_video['playlist_item_id'])

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
