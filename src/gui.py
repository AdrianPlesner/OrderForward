import tkinter as tk
import os
from tkinter.filedialog import askdirectory

from src import main, gmail_utils
from src.connection_status_widget import ConnectionStatusWidget
from src.update_handler import UpdateHandler, CURRENT_VERSION

DIRECTORY_LABEL_PREFIX = "FILER PLACERING:\t"
OUTPUT_DIRECTORY_PREFIX = "ORDRE PLACRING:\t"
INGEN_MAPPE_VALGT = "Ingen mappe valgt!"

def update_directory():
    global files_directory
    new_dir = askdirectory(title="Angiv mappe der inderholder filer:")
    files_directory = new_dir
    directory_label['text'] = DIRECTORY_LABEL_PREFIX + new_dir
    main.update_files_path(new_dir)

def update_order_directory():
    global order_directory
    new_dir = askdirectory(title="Angiv destinations mappe")
    order_directory = new_dir
    order_label['text'] = OUTPUT_DIRECTORY_PREFIX + new_dir
    main.update_orders_path(new_dir)

def check_for_update(handler: UpdateHandler):
    if handler.exists_newer_tag():
        handler.open_dialog()

def run_main():
    error_label['text'] = ""
    files_valid = not (files_directory is None or not os.path.exists(files_directory))
    if not files_valid :
        error_label['text'] += "FILER PLACERING UGYLDIG!\t"
    orders_valid = not (order_directory is None or not os.path.exists(order_directory))
    if not orders_valid:
        error_label['text'] += "ORDRER PLACERING UGYLDIG!\t"

    if files_valid and orders_valid:
        service = None
        try:
            service = connection_status_widget.get_service()
            orders_processed = main.main(service, files_directory, order_directory)
            orders_processed_label['text'] = f'{orders_processed} order behandlet!'
        except Exception as e:
            error_label['text'] = "Der skete en fejl under ordre behandlingen prøv igen!"
            if service is not None:
                gmail_utils.send_message(service, e)


root = tk.Tk()
root.title(f"Order Forward v{CURRENT_VERSION}")
root.minsize(1024, 512)
root.geometry("300x300+50+50")


tk.Label(root, text="Velkommen til ordrepaknings programmet!").pack(pady=24)

update_handler = UpdateHandler(root)


connection_status_widget = ConnectionStatusWidget(root)
connection_status_widget.pack(pady=8)

#request_access_widget = RequestAccessWidget(root)
#request_access_widget.pack(pady=8)

saved_paths = main.check_for_path()
files_directory = saved_paths['files']
order_directory = saved_paths['orders']

current_files_directory = DIRECTORY_LABEL_PREFIX
current_order_directory = OUTPUT_DIRECTORY_PREFIX

if saved_paths is None:
    current_files_directory += INGEN_MAPPE_VALGT
    current_order_directory += INGEN_MAPPE_VALGT
else:
    current_files_directory += saved_paths['files']
    current_order_directory += saved_paths['orders']

files_frame = tk.Frame(root)

directory_label = tk.Label(files_frame, text=current_files_directory)
directory_label.grid(row=0, column=0)
get_directory_button = tk.Button(files_frame, text="Vælg mappe", command=update_directory)
get_directory_button.grid(row=0, column=1)
files_frame.pack(pady=8)

order_frame = tk.Frame(root)

order_label = tk.Label(order_frame, text=current_order_directory)
order_label.grid(row=0, column=0)
get_order_button = tk.Button(order_frame, text="Vælg mappe", command=update_order_directory)
get_order_button.grid(row=0, column=1)
order_frame.pack(pady=8)

run = tk.Button(root, text="Hent ordrer!", command=run_main)
run.pack()
error_label = tk.Label(root, text="", fg="red")
error_label.pack(pady=8)

orders_processed_label = tk.Label(root, text="", fg="green")
orders_processed_label.pack(pady=8)

root.after_idle(check_for_update, update_handler)
root.mainloop()


