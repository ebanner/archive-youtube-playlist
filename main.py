import os
import pickle

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from google.auth.transport.requests import Request


WATCH_NEXT_PLAYLIST = 'PLkd5S9lUKlOAHYE97mzLKaAIdjhHaXWXS'
ARCHIVE_PLAYLIST = 'PLkd5S9lUKlOArJsazeSVyZ1syXY2yxdyC'

credentials = None

if os.path.isfile('token.pickle'):
    with open('token.pickle', 'rb') as f:
        credentials = pickle.load(f)

if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json",
            scopes=[
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtubepartner",
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.force-ssl",
            ]
        )
        flow.run_local_server(
            authorization_prompt_message='',
            access_type='offline',
        )

        credentials = flow.credentials

        with open('token.pickle', 'wb') as f:
            pickle.dump(credentials, f)

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


if __name__ == '__main__':
    watch_next_videos = get_watch_next_videos()
    print(f'Watch next videos = {watch_next_videos}')
    for watch_next_video in watch_next_videos:
        add_to_archive(watch_next_video['video_id'])
        remove_from_watch_next(watch_next_video['playlist_item_id'])
