import base64
import mimetypes
import os.path
import shutil

from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://mail.google.com/"]

RECIPIENT_ADDRESS = "nicklashinge@gmail.com"
SENDER_ADDRESS = "orderforward87@gmail.com"

FILES_DIRECTORY_PATH="C:\\Users\\adria\\Desktop\\SALE FILES\\"
ZIPS_DIRECTORY = "ZIPS\\"

DEBUG = True

REMOVE_UNREAD_JSON_BODY = {
  "addLabelIds": ["PROCESSED"],
  "removeLabelIds": ["UNREAD"]
}

def main():

    creds = authorize()
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        ensure_processed_exists(service)
        results = service.users().messages().list(userId="me", maxResults=25, q="is:unread").execute()
        messages = results.get("messages")

        length = 0

        if messages is None:
            print('No new messages')
        else:
            length = len(messages)
            print(f'Number of unread messages: {length}')

        if length > 0:
            for messageObject in messages:
                message = service.users().messages().get(userId='me', id=messageObject.get('id')).execute()
                messageText = get_body_text(message)
                orderedItems = find_items(messageText)
                send_message(service, orderedItems)
                mark_message_read(service, message)

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
    return base64.b64decode(message['payload']['parts'][0]['body']['data']).decode()

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
            items.append('#' + item)
    if DEBUG:
        print(items)
    return items

def mark_message_read(service, message):
    service.users().messages().modify(userId='me', id=message['id'], body=REMOVE_UNREAD_JSON_BODY).execute()

def ensure_processed_exists(service):
    request = service.users().labels().list(userId='me').execute()
    labels = request['labels']
    isPresent = False
    for l in labels:
        isPresent |= l['name'] == "PROCESSED"
    if not isPresent:
        print("PROCESSED not fund")
        json_body ={
            "id": "PROCCESSED",
            "name": "PROCESSED",
            "messageListVisibility": 'show',
            "labelListVisibility": 'labelShow'}
        try:
            service.users().labels().create(userId='me', body=json_body).execute()
            print("PROCESSED label created")
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

def send_message(service, items: list):
    email = EmailMessage()
    email.set_content("Testy test")

    email['To'] = RECIPIENT_ADDRESS
    email['From'] = SENDER_ADDRESS
    email['Subject'] = "test subject"

    for item in items:
        file_path = get_file(item)
        attach_file(email, file_path)

    encoded_email = base64.urlsafe_b64encode(email.as_bytes()).decode()
    json_message = {"message": {"raw": encoded_email}}
    try:
        draft = service.users().drafts().create(userId='me', body=json_message).execute()
        service.users().drafts().send(userId='me', body=draft).execute()
        print('Email sent successfully')
    except HttpError as error:
        print(f"An error occurred: {error}")

def get_file(file_id: str):
    file_path = FILES_DIRECTORY_PATH + ZIPS_DIRECTORY + file_id
    extension = ".zip"
    exists = os.path.exists(file_path + extension)
    if not exists:
        directory_path = FILES_DIRECTORY_PATH + file_id
        shutil.make_archive(file_path, 'zip', directory_path)
    return file_path + extension

def attach_file(message, file):
    if DEBUG:
        print(f'Attaching file: {file}')
    type_subtype, _ = mimetypes.guess_type(file)
    maintype, subtype = type_subtype.split("/")
    with open(file, "rb") as fp:
        attachment_data = fp.read()
    message.add_attachment(attachment_data, maintype, subtype, filename="testfile.zip")

if __name__ == "__main__":
  main()