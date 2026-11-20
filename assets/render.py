from tkinter import messagebox
import pandas as pd

def handle_valid_content_exception(file_path):
    try:
        pd.read_csv(file_path)
        return True
    except Exception as e:
        messagebox.showerror('Error',f'Error while reading file. It might be a binary file, please check it.\nError Message:\n\n{e}')
        return False

def run(file_path):
    handle_valid_content_exception(file_path)

    raw_data = pd.read_csv(file_path)
    print(raw_data)
