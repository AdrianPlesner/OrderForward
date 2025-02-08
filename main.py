import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def main():

    creds = authorize()
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", maxResults=25, q="is:unread").execute()
        messages = results.get("messages")

        length = len(messages)

        print(f'Number of unread messages: {length}')

        if length > 0:
            for messageObject in messages:
                message = service.users().messages().get(userId='me', id=messageObject.get('id')).execute()
                messageText = get_body_text(message)
                orderedItems = find_items(messageText)



    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


def authorize():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_subject(message):
    return message['payload']['headers'][21]['value']

def get_body_text(message):
    return base64.b64decode(message['payload']['parts'][0]['body']['data']).decode("ascii")

def debug_message(message):
    print('---------------')
    print(get_subject(message))
    print(get_body_text(message))
    print('----------------\n')

def find_items(text: str):
    items = []
    substrings = text.split('#')
    for s in substrings[1:]:
        i = 0
        while i < len(s) and s[i].isnumeric():
            i += 1
        item = s[:i]
        if len(item) > 0:
            items.append(item)
    return items

def mark_message_read(service, message):
    json_body = '{"removeLabelIds":["unread"]}'
    service.users().messages().modify(userId='me', id=message['id'], body=json_body).execute()

if __name__ == "__main__":
  main()