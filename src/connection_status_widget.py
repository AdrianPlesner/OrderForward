import tkinter as tk
from src.gmail_utils import *
from src.simply_mail_utils import *

MAIL_OPTIONS = ["Gmail", "simply"]

class ConnectionStatusWidget(tk.Frame):
    disconnected_label = "IKKE FORBUNDET!"
    disconnected_color = "red"
    connected_label = "FORBUNDET: "
    connected_color = "green"
    connect_bt_text = "Opret Forbindelse"
    connect_bt_color = "blue"
    disconnect_bt_text = "Afbryd Forbindelse"

    def __init__(self, master):
        super().__init__(master)
        self.connected = False
        self.creds = None
        self.service = None
        #self.frame = tk.Frame(master)
        self.mail = tk.StringVar()
        self.mail.set(MAIL_OPTIONS[0])
        self.mail_chooser = tk.OptionMenu(self, self.mail, *MAIL_OPTIONS, command=lambda x: self.update_connection())
        self.pre_label = tk.Label(self, text=" server forbindelse: ")
        self.status_label = tk.Label(self)
        self.connect_button = tk.Button(self, text=self.connect_bt_text, bg=self.connect_bt_color, command=self.establish_connection)
        self.disconnect_button = tk.Button(self, text=self.disconnect_bt_text, fg='red', command=self.disconnect)

        self.update_connection()

        self.mail_chooser.grid(column=0, row=0, padx=4)
        self.pre_label.grid(column=1, row=0, padx=4)
        self.status_label.grid(column=2, row=0, padx=4)
        if not self.connected:
            self.connect_button.grid(column=3, row=0, padx=4)
        else:
            self.disconnect_button.grid(column=3, row=0, padx=4)

    def update_connection(self):
        match self.mail.get():
            case "Gmail":
                self.creds = check_credentials()
                self.connected = self.creds is not None and self.creds.valid
            case "simply":
                self.connected = False
                print("using simply")
            case _:
                print("Error unknown email type")
        self.update_status(self.connected)


    def update_status(self, status: bool):
        if status:
            self.service = get_service()
            self.status_label['text'] = self.connected_label + get_user_address(self.service)
            self.status_label['bg'] = self.connected_color
            self.connect_button.grid_forget()
            self.disconnect_button.grid(column=3, row=0, padx=4)
        else:
            self.service = None
            self.status_label['text'] = self.disconnected_label
            self.status_label['bg'] = self.disconnected_color
            self.disconnect_button.grid_forget()
            self.connect_button.grid(column=3, row=0, padx=4)

    def establish_connection(self):
        match self.mail.get():
            case "Gmail":
                self.creds = validate_credentials(self.creds)
                self.connected = self.creds is not None and self.creds.valid
            case "simply":
                connect_imap(self.get_credentials_dialog)
                pass
        self.update_status(self.connected)

    def disconnect(self):
        delete_token()
        self.creds = None
        self.connected = False
        self.update_status(False)

    def get_service(self):
        if self.service is None:
            self.establish_connection()
        return self.service

    def get_credentials_dialog(self):
        d = tk.Toplevel(self.master)
        d.geometry("256x128")
        label = tk.Label(d, text="Indtast email adresse og password for simply konto:")

        credentials_frame = tk.Frame(d)
        user_label = tk.Label(credentials_frame,text="Email:")
        #TODO: get username and password from entry field and validate
        login_btn = tk.Button(d, text="Login")

        label.pack()
        d.attributes("-topmost", True)