import base64
import mimetypes
import os.path
import shutil
import zipfile

from email.message import EmailMessage
from tkinter.filedialog import askdirectory
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
ORDER_DIRECTORY_PATH="C:\\Users\\adria\\Desktop\\ORDERS\\"

DEBUG = True

def main():
    files_path = askdirectory(title="Angiv mappe der inderholder filer:")
    output_path = askdirectory(title="Angiv destinations mappe")

    if DEBUG:
        print(f'Files path: {files_path}')
        print(f'Orders path: {output_path}')
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
                order_id = get_order_id(get_subject(message))
                message_text = get_body_text(message)
                ordered_items = find_items(message_text)
                package_files(order_id, ordered_items, files_path, output_path)
                mark_message_read(service, message)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


def authorize():
    try:
        creds = None
        token_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"token.json"))
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

def get_subject(message):
    headers = message['payload']['headers']
    subject_header = {}
    for h in headers:
        if h['name'] == "Subject":
            subject_header = h
    subject = subject_header['value']
    if DEBUG:
        print(f'Found subject: {subject}')
    return subject

def get_order_id(subject_string: str):
    numbers = [c for c in subject_string if c.isnumeric()]
    order_id = "".join(numbers)
    if DEBUG:
        print(f'Found order id: {order_id}' )
    return order_id

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
        print(f'Found items in order: {items}')
    return items

def mark_message_read(service, message):
    if DEBUG:
        print("Marking message read")
    request = service.users().labels().list(userId='me').execute()
    labels = request['labels']
    processed_label_id = [l for l in labels if l['name'] == "PROCESSED"][0]['id']
    json_body = {
        "addLabelIds": [processed_label_id],
        "removeLabelIds": ["UNREAD"]
    }
    service.users().messages().modify(userId='me', id=message['id'], body=json_body).execute()

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

def package_files(order_id: str, files: list, files_path, output_path):
    if DEBUG:
        print(f'Packaging files for order {order_id}')
    final_directory = os.path.join(ORDER_DIRECTORY_PATH, order_id + ".zip")
    with zipfile.ZipFile(final_directory, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            file_directory = os.path.join(FILES_DIRECTORY_PATH, file)
            if os.path.exists(file_directory):
                if DEBUG:
                    print(f'Zipping files: {file}')
                zipdir(file_directory, zip_file)
            else:
                print(f'Could not find files {file_directory}')
    if DEBUG:
        print("All files successfully compressed")


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))

if __name__ == "__main__":
  main()