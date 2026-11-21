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
        root.destroy()

class Render(tk.Tk):
    def __init__(self, file_path) -> None:
        super().__init__()
        self.title('Render Engine')
        self.geometry('400x300')
        self.resizable(False,False)
        self.file_path = file_path
        self.menu_button = tk.Menubutton(self,text='Tools')
        self.menu = tk.Menu(self.menu_button)
        self.menu.add_command(label="Show Pandas Object")
        self.menu.add_command(label="Use Pandas Functions")
        self.menu.add_command(label="AI Settings")
        self.menu_button.config(menu=self.menu)

        handle_valid_content_exception(file_path,self)

        self.data = pd.read_csv(file_path)

        # init
        self.scrolledText = ScrolledText(self,width=60)
        self.save_button = tk.Button(self, text='Save', command=self.save)

    def save(self):
        with open(self.file_path,'w') as file:
            file.write(self.scrolledText.get('1.0',tk.END).rstrip('\n'))

    def run(self):
        # main buttons rendering
        self.save_button.place(relx=0.0,rely=0.0)
        self.menu_button.place(relx=0.15,rely=0.0)

        # show data
        self.scrolledText.insert(tk.END, self.data.to_csv(index=False))
        self.scrolledText.place(relx=0.0,rely=0.1)
