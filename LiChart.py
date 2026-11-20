
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Li-Chart : Render Chart')
        self.geometry('800x500')
        self.resizable(False, False)

        self.upload_button = tk.Button(
            self,
            text='Upload File',
            command=self.upload_file
        )
        self.upload_button.place(relx=0.05,rely=0.05)

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

        shutil.copy2(file_path, destination)

        messagebox.showinfo(
            'Success',
            f'File saved successfully:\n{destination}'
        )

    def run(self):
        self.mainloop()


app = App()
app.run()
