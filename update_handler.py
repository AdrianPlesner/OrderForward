import os
import tkinter as tk
import urllib.request

import requests

CURRENT_VERSION = "1.2"
GITHUB_RELEASE_URL = "https://api.github.com/repos/AdrianPlesner/OrderForward/releases/latest"

class UpdateHandler(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.latest_tag = None
        self.get_latest_version_number()
        self.label = tk.Label(self, text=f'latest tag: {self.latest_tag}')
        self.label.pack()

    def get_latest_version_number(self):
        r = requests.get(GITHUB_RELEASE_URL)
        if r.status_code == 200:
            self.latest_tag = r.json()['tag_name']

    def exists_newer_tag(self):
        return float(self.latest_tag) > float(CURRENT_VERSION)

    def install_update(self):
        exe_dir = os.path.join(os.getcwd(),"OrderForward.exe")
        r = requests.get(GITHUB_RELEASE_URL)
        if r.status_code == 200:
            file_url = r.json()['assets'][0]['browser_download_url']
            os.replace()
            urllib.request.urlretrieve(file_url, exe_dir)
            self.master.destroy()

    def open_dialog(self):
        d = tk.Toplevel(self.master)
        d.geometry("256x128")
        label = tk.Label(d, text=f"Der findes en nyere version af OrderForward!\nNuværende version: {CURRENT_VERSION} Nyeste version: {self.latest_tag}")
        buttons_frame = tk.Frame(d)
        update_button = tk.Button(buttons_frame, text="Opdater nu!", command=self.install_update)
        ignore_button = tk.Button(buttons_frame, text="Ikke nu", command=d.destroy)
        update_button.grid(row=0, column=0, padx=4)
        ignore_button.grid(row=0, column=1, padx=4)

        label.pack()
        buttons_frame.pack()
        d.attributes("-topmost", True)


