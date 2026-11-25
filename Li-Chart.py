# Li-Chart : Render and Edit your csv data as a GUI object!
# Fully Open-Source by MACsepehri
# Organization Credit : Li-Team
# Visit project on github : https://github.com/LithiumTeam/Li-Chart

import tkinter as tk
from tkinter import filedialog, messagebox
import assets.render as render
import assets.theme as theme

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Li-Chart : Render Chart')
        self.geometry('800x500')
        self.resizable(False, False)
        theme.apply(self)

        # open files
        self.open_button = tk.Button(self, text='Open File', command=self.open_file)
        theme.button_style(self.open_button)
        self.open_button.place(relx=0.03,rely=0.03)

        # text widgit initalization
        label = tk.Label(self, text='Powered by Pandas | By Li-Team')
        theme.apply(label)
        label.place(relx=0.03,rely=0.9)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title='Select a file',
            filetypes=[
                ('CSV Files', '*.csv'),
                ('All Files', '*.*')
            ]
        )

        r = render.Render(file_path)
        r.run()

    def run(self):
        self.mainloop()


app = App()
app.run()
