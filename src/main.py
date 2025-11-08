import base64
import json
import os.path
import tempfile
import zipfile

from tkinter.filedialog import askdirectory
from googleapiclient.errors import HttpError
from src.gmail_utils import get_subject, ensure_processed_exists, mark_message_read, mark_message_processed

DEBUG = True

def main(service, files_path, output_path):
    if files_path == "":
        files_path = askdirectory(title="Angiv mappe der inderholder filer:")
    if output_path == "":
        output_path = askdirectory(title="Angiv destinations mappe")

    if DEBUG:
        print(f'Files path: {files_path}')
        print(f'Orders path: {output_path}')
    try:
        # Call the Gmail API
        messages_to_process = []
        max_process_count = 10
        ensure_processed_exists(service)
        results = service.users().messages().list(userId="me", maxResults=10, q="is:unread&+Eventyrprint").execute()
        next_page_token = results.get("nextPageToken")
        messages = results.get("messages")
        flag = True
        while flag and len(messages_to_process) < max_process_count and messages is not None and len(messages) > 0:
            for messageObject in messages:
                message = service.users().messages().get(userId='me', id=messageObject.get('id')).execute()
                order_id = get_order_id(get_subject(message))
                if len(order_id) > 0:
                    messages_to_process.append(message)
                else:
                    mark_message_processed(service, message, DEBUG)
            if next_page_token is None:
                flag = False
            else:
                results = service.users().messages().list(userId="me", maxResults=10, q="is:unread", pageToken=next_page_token).execute()
                next_page_token = results.get("nextPageToken")
                messages = results.get("messages")

        length = 0
        errors = 0

        if len(messages_to_process) == 0:
            print('No new messages')
        else:
            length = len(messages_to_process)
            print(f'Number of unread messages: {length}')


            for message in messages_to_process:
                order_id = get_order_id(get_subject(message))
                if len(order_id) > 0:
                    try:
                        message_text = get_body_text(message)
                        ordered_items = find_items(message_text)
                        if len(ordered_items) > 0:
                            package_files(order_id, ordered_items, files_path, output_path)
                            mark_message_read(service, message, DEBUG)
                    except HttpError as error:
                        print(f'An error orrurred while processing order {order_id}')
                        errors += 0
        return length, errors

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
        raise error

def get_order_id(subject_string: str):
    if "Din ordre nr." in subject_string:
        numbers = [c for c in subject_string if c.isnumeric()]
        order_id = "".join(numbers)
        if DEBUG:
            print(f'Found order id: {order_id}' )
        return order_id
    return ""

def get_body_text(message):
    return base64.b64decode(message['payload']['parts'][0]['body']['data']).decode()

def debug_message(message):
    print('---------------')
    print(get_subject(message, DEBUG))
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

def package_files(order_id: str, files: list, files_path, output_path):
    if DEBUG:
        print(f'Packaging files for order {order_id}')
    try:
        final_directory = os.path.join(output_path, order_id + ".zip")
        with zipfile.ZipFile(final_directory, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                file_directory = locate_file(files_path, file)
                if os.path.exists(file_directory):
                    if DEBUG:
                        print(f'Zipping files: {file}')
                    zipdir(file_directory, zip_file)
                else:
                    print(f'Could not find files {file_directory}')
        if DEBUG:
            print("All files successfully compressed")
    except Exception as e:
        print(e)
        raise e

def locate_file(files_path: str, file_name: str):
    roots = [x[0] for x in os.walk(files_path)]
    path_to_find = ""
    for path in roots:
        parts = path.split('\\')
        if parts[-1] == file_name:
            path_to_find = path
            break

    if path_to_find != "" :
        return path_to_find
    else:
        print(f'Could not locate {file_name} in {files_path}')
        raise Exception(f"File not found {file_name}")

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))

def check_for_path():
    path = os.path.join(tempfile.gettempdir(),"OrderForwardPaths.dat")
    paths = {'files': "", 'orders': ""}
    if os.path.exists(path):
        try:
            with open(path, 'r') as json_file:
                paths = json.load(json_file)
        except Exception as e:
            os.remove(path)
    return paths

def update_files_path(new_path: str):
    path = os.path.join(tempfile.gettempdir(), "OrderForwardPaths.dat")
    saved = check_for_path()
    if saved is None:
        saved = {}
    saved['files'] = new_path
    with open(path, 'w') as file:
        json.dump(saved, file)

def update_orders_path(new_path: str):
    path = os.path.join(tempfile.gettempdir(), "OrderForwardPaths.dat")
    saved = check_for_path()
    if saved is None:
        saved = {}
    saved['orders'] = new_path
    with open(path, 'w') as file:
        json.dump(saved, file)

