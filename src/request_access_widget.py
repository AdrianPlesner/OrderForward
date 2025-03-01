import ssl
import tkinter as tk
import smtplib
from email.message import EmailMessage


class RequestAccessWidget(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.txt = tk.Text(self, height=1)
        self.btn = tk.Button(self, text="Anmod om adgang", command=self.request_access)


        self.txt.grid(column=0, row=0, padx=4)
        self.btn.grid(column=1, row=0, padx=4)

    def request_access(self):
        address = self.txt.get(1.0, tk.END)
        self.txt.delete(1.0, tk.END)
        print(address)
        email = EmailMessage()
        email['Subject'] = "OrderForward access request"
        email['From'] = "orderforward87@gmail.com"
        email['To'] = "adrian.plesner@gmail.com"
        email.set_content(f"{address} is requesting access to the OrderForward API")

        context = ssl.create_default_context()

        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.ehlo()
            s.starttls(context=context)
            s.login("orderforward87@gmail.com","")
            s.send(email.as_string())
