from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import tkinter as tk
import pandas as pd
import sys

def handle_valid_content_exception(file_path,root):
    try:
        pd.read_csv(file_path)
        return True
    except Exception as e:
        messagebox.showerror('Error',f'Error while reading file. It might be a binary file, please check it.\nError Message:\n\n{e}')
        root.destory()

class Render(tk.Tk):
    def __init__(self, file_path) -> None:
        super().__init__()
        self.title('Render Engine')
        self.geometry('400x300')
        self.resizable(False,False)
        self.file_path = file_path

        handle_valid_content_exception(file_path,self)

    def run(self):
        raw_data = pd.read_csv(self.file_path)
        scrolledText = ScrolledText(self,width=60)
        scrolledText.insert(tk.END,raw_data)
        scrolledText.place(relx=0.0,rely=0.08)
