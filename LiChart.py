# Li-Chart : Render and Edit your csv data as a GUI object!
# Fully Open-Source by MACsepehri
# Organization Credit : Li-Team
# Visit project on github : https://github.com/LithiumTeam/Li-Chart

import tkinter as tk
from tkinter import filedialog, messagebox
import assets.render as render
import shutil
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Li-Chart : Render Chart')
        self.geometry('800x500')
        self.resizable(False, False)

        # upload/open files
        self.upload_button = tk.Button(self, text='Upload File', command=self.upload_file)
        self.upload_button.place(relx=0.05,rely=0.05)

        self.open_button = tk.Button(self, text='Open File', command=self.open_file)
        self.open_button.place(relx=0.05,rely=0.15)

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title='Select a file',
            filetypes=[
                ('CSV Files', '*.csv'),
                ('Excel Files', '*.xlsx'),
                ('All Files', '*.*')
            ]
        )

        if not file_path:
            return

        os.makedirs('assets/data', exist_ok=True)

        filename = os.path.basename(file_path)
        destination = os.path.join('assets/data', filename)

        if os.path.exists(destination):
            overwrite = messagebox.askyesno(
                'File Already Exists',
                f'The file "{filename}" already exists.\nDo you want to replace it?'
            )

            if not overwrite:
                return

            os.remove(destination)

        shutil.copy2(file_path, destination)

        render.run(destination)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title='Select a file',
            filetypes=[
                ('CSV Files', '*.csv'),
                ('Excel Files', '*.xlsx'),
                ('All Files', '*.*')
            ]
        )

        render.run(file_path)

    def run(self):
        self.mainloop()


app = App()
app.run()
