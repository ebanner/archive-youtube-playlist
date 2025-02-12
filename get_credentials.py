import google_auth_oauthlib.flow

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

if __name__ == '__main__':
    with open('tokens.json', "w") as f:
        f.write(credentials.to_json())

