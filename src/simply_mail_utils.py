import imaplib
import ssl

IMAP_SERVER = "mail.simply.com"
IMAP_PORT = 143

def connect_imap(get_credentials_callback):
    imap_server = imaplib.IMAP4(IMAP_SERVER, port=IMAP_PORT)
    context = ssl.create_default_context()
    imap_server.starttls(context)
    user, password = get_credentials_callback()
    imap_server.login(user, password)
