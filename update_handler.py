import os
import shutil
import subprocess
import tempfile
import tkinter as tk
import urllib.request

import requests

CURRENT_VERSION = "1.1"
GITHUB_RELEASE_URL = "https://api.github.com/repos/AdrianPlesner/OrderForward/releases/latest"

class UpdateHandler(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.latest_tag = None
        self.get_latest_version_number()
        self.label = tk.Label(self, text=f'latest tag: {self.latest_tag}')
        self.label.pack()
        self.want_update = False

    def get_latest_version_number(self):
        r = requests.get(GITHUB_RELEASE_URL)
        if r.status_code == 200:
            self.latest_tag = r.json()['tag_name']

    def exists_newer_tag(self):
        return float(self.latest_tag) > float(CURRENT_VERSION)

    def install_update(self):
        tmp_dir = tempfile.gettempdir()
        update_exe = "OrderForwardUpdater.exe"
        dest_file = os.path.join(tmp_dir, update_exe)
        src_file = os.path.abspath(os.path.join(os.path.dirname(__file__), update_exe))
        shutil.copy(src_file, dest_file)


        tmp_exe_dir = os.path.join(tmp_dir,"OrderForward.exe")
        running_exe_dir = os.path.join(os.getcwd(), "OrderForward.exe")
        r = requests.get(GITHUB_RELEASE_URL)
        if r.status_code == 200:
            file_url = r.json()['assets'][0]['browser_download_url']
            print("Downloading update")
            urllib.request.urlretrieve(file_url, tmp_exe_dir)
            subprocess.Popen([dest_file, str(os.getpid()), running_exe_dir, tmp_exe_dir], shell=False)
            print("closing window")
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

