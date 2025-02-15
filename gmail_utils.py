import base64
import os
import tempfile
from email.message import EmailMessage

from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://mail.google.com/"]

def send_message(service, error: Exception):
    email = EmailMessage()
    email.set_content("Testy test")

    email['To'] = "adrian.plesner@gmail.com"
    email['Subject'] = "OrderForward error report"

    email.set_content(f'{error}')


    encoded_email = base64.urlsafe_b64encode(email.as_bytes()).decode()
    json_message = {"message": {"raw": encoded_email}}
    try:
        draft = service.users().drafts().create(userId='me', body=json_message).execute()
        service.users().drafts().send(userId='me', body=draft).execute()
        print('Email sent successfully')
    except HttpError as error:
        print(f"An error occurred: {error}")


def authorize():
    try:
        creds = None
        token_path = os.path.join(tempfile.gettempdir(),"OrderForwardToken.json")
        credentials_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"credentials.json"))
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        return creds
    except Exception as e:
        print(e)
        raise e

def get_service():
    creds = authorize()
    service = build("gmail", "v1", credentials=creds)
    return service

def get_subject(message, debug=False):
    headers = message['payload']['headers']
    subject_header = {}
    for h in headers:
        if h['name'] == "Subject":
            subject_header = h
    subject = subject_header['value']
    if debug:
        print(f'Found subject: {subject}')
    return subject


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
            raise error


def mark_message_read(service, message, debug=False):
    if debug:
        print("Marking message read")
    request = service.users().labels().list(userId='me').execute()
    labels = request['labels']
    processed_label_id = [l for l in labels if l['name'] == "PROCESSED"][0]['id']
    json_body = {
        "addLabelIds": [processed_label_id],
        "removeLabelIds": ["UNREAD"]
    }
    service.users().messages().modify(userId='me', id=message['id'], body=json_body).execute()

# def get_file(file_id: str):
#     file_path = FILES_DIRECTORY_PATH + ZIPS_DIRECTORY + file_id
#     extension = ".zip"
#     exists = os.path.exists(file_path + extension)
#     if not exists:
#         directory_path = FILES_DIRECTORY_PATH + file_id
#         shutil.make_archive(file_path, 'zip', directory_path)
#     return file_path + extension

# def attach_file(message, file):
#     if DEBUG:
#         print(f'Attaching file: {file}')
#     type_subtype, _ = mimetypes.guess_type(file)
#     maintype, subtype = type_subtype.split("/")
#     with open(file, "rb") as fp:
#         attachment_data = fp.read()
#     message.add_attachment(attachment_data, maintype, subtype, filename="testfile.zip")