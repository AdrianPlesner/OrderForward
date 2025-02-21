import tkinter as tk
from gmail_utils import *

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
        self.service = None
        #self.frame = tk.Frame(master)
        self.pre_label = tk.Label(self, text="Gmail server forbindelse: ")
        self.status_label = tk.Label(self)
        self.connect_button = tk.Button(self, text=self.connect_bt_text, bg=self.connect_bt_color, command=self.establish_connection)
        self.disconnect_button = tk.Button(self, text=self.disconnect_bt_text, fg='red', command=self.disconnect)

        self.creds = check_credentials()
        self.connected = self.creds is not None and self.creds.valid
        self.update_status(self.connected)

        self.pre_label.grid(column=0, row=0, padx=4)
        self.status_label.grid(column=1, row=0, padx=4)
        if not self.connected:
            self.connect_button.grid(column=2, row=0, padx=4)
        else:
            self.disconnect_button.grid(column=2, row=0, padx=4)


    def update_status(self, status: bool):
        if status:
            self.service = get_service()
            self.status_label['text'] = self.connected_label + get_user_address(self.service)
            self.status_label['bg'] = self.connected_color
        else:
            self.service = None
            self.status_label['text'] = self.disconnected_label
            self.status_label['bg'] = self.disconnected_color

    def establish_connection(self):
        self.creds = validate_credentials(self.creds)
        self.connected = self.creds is not None and self.creds.valid
        self.update_status(self.connected)
        if self.connected:
            self.connect_button.grid_forget()
            self.disconnect_button.grid(column=2, row=0, padx=4)

    def disconnect(self):
        delete_token()
        self.creds = None
        self.connected = False
        self.update_status(False)
        self.disconnect_button.grid_forget()
        self.connect_button.grid(column=2, row=0, padx=4)

    def get_service(self):
        if self.service is None:
            self.establish_connection()
        return self.service