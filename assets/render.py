from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from openai import OpenAI
import tkinter as tk
import pandas as pd
import threading
import json
import re


def handle_valid_content_exception(file_path, root):
    try:
        pd.read_csv(file_path)
        return True
    except Exception as e:
        messagebox.showerror(
            'Error',
            f'Error while reading file. It might be a binary file, please check it.\nError Message:\n\n{e}'
        )
        root.destroy()
        return False


class Render(tk.Tk):
    def __init__(self, file_path) -> None:
        super().__init__()

        self.title('Render Engine')
        self.geometry('800x300')
        self.resizable(False, False)

        self.file_path = file_path

        self.menu_button = tk.Menubutton(self, text='Tools')
        self.menu = tk.Menu(self.menu_button, tearoff=False)

        self.menu.add_command(
            label="Show Pandas Object"
        )
        self.menu.add_command(
            label="Use Pandas Functions"
        )
        self.menu.add_command(
            label="AI Settings"
        )

        self.menu_button.config(menu=self.menu)

        if not handle_valid_content_exception(file_path, self):
            return

        self.data = pd.read_csv(file_path)

        # Init
        self.scrolledText = ScrolledText(self, width=60)

        self.save_button = tk.Button(
            self,
            text='Save',
            command=self.save
        )

        self.ai_ask_input_box = tk.Entry(self)

        self.ai_ask_button = tk.Button(
            self,
            text='Ask',
            command=self.ask_ai
        )

        self.aiScrolledText = ScrolledText(
            self,
            width=36,
            wrap=tk.WORD
        )

        # AI Settings
        try:
            with open('./assets/data.json', 'r') as file:
                data = json.load(file)

            self.ai_base_url = data["env.base.api.url"]
            self.ai_api_key = data["env.api.key"]

            self.client = OpenAI(
                api_key=self.ai_api_key,
                base_url=self.ai_base_url
            )

        except Exception as e:
            messagebox.showerror(
                'AI Configuration Error',
                str(e)
            )
            self.destroy()
            return

        self.conversation = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant integrated into a CSV editor. "
                    "Help users understand, analyze, and manipulate CSV data. "
                    "Be concise and provide Python Pandas examples when useful."
                )
            }
        ]

        self.ai_busy = False

    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as file:
            file.write(
                self.scrolledText.get('1.0', tk.END).rstrip('\n')
            )

        messagebox.showinfo(
            'Saved',
            'CSV file saved successfully.'
        )

    def ask_ai(self):
        if self.ai_busy:
            messagebox.showwarning(
                'Please wait',
                'An AI request is already running.'
            )
            return

        prompt = self.ai_ask_input_box.get().strip()

        if not prompt:
            return

        self.ai_ask_input_box.delete(0, tk.END)

        self.ai_busy = True
        self.ai_ask_button.config(state=tk.DISABLED)

        self.aiScrolledText.configure(state=tk.NORMAL)

        self.aiScrolledText.insert(
            tk.END,
            f"You: {prompt}\n\nAI: Thinking...\n\n"
        )

        self.aiScrolledText.see(tk.END)
        self.aiScrolledText.configure(state=tk.DISABLED)

        threading.Thread(
            target=self.ai_request,
            args=(prompt,),
            daemon=True
        ).start()

    def ai_request(self, prompt):
        try:
            csv_context = self.data.head(30).to_csv(index=False)

            messages = self.conversation + [
                {
                    "role": "user",
                    "content": (
                        f"CSV Data:\n{csv_context}\n\n"
                        f"Question: {prompt}"
                        "If user wanted from you to edit you data, say your answer, then say :\nEDIT_CONFIRMATION='new_csv_data', Don't give user code just edit confirmation"
                    )
                }
            ]

            response = self.client.chat.completions.create(
                model="agnes-2.5-flash",
                messages=messages
            )

            answer = response.choices[0].message.content

            self.conversation.append({
                "role": "user",
                "content": prompt
            })

            self.conversation.append({
                "role": "assistant",
                "content": answer
            })

            self.after(
                0,
                lambda: self.finish_ai_request(answer)
            )

        except Exception as e:
            print(e)
            self.after(
                0,
                lambda error=str(e): self.finish_ai_request(
                    f"Error: {error}"
                )
            )

    def finish_ai_request(self, answer):

        match = re.search(
            r"EDIT_CONFIRMATION='(.*?)'",
            answer,
            re.DOTALL
        )

        edit_confirmation = ''
        text = answer

        if match:
            edit_confirmation = match.group(1)

            text = answer.replace(match.group(0), '', 1)

        # Convert literal \n into actual new lines, if necessary
        text = text.replace('\\n', '\n')

        self.aiScrolledText.configure(state=tk.NORMAL)

        # Clear everything
        self.aiScrolledText.delete("1.0", tk.END)

        # Insert new content
        self.aiScrolledText.insert(
            tk.END,
            f"AI: {text.strip()}\n\n"
        )

        self.aiScrolledText.see(tk.END)
        self.aiScrolledText.configure(state=tk.DISABLED)

        self.scrolledText.configure(state=tk.NORMAL)
        self.scrolledText.delete("1.0", tk.END)
        self.scrolledText.insert(tk.END, edit_confirmation)
        self.scrolledText.configure(state=tk.DISABLED)

        self.ai_busy = False
        self.ai_ask_button.config(state=tk.NORMAL)

    def run(self):
        # Main buttons
        self.save_button.place(
            relx=0.0,
            rely=0.0
        )

        self.menu_button.place(
            relx=0.08,
            rely=0.0
        )

        self.ai_ask_input_box.place(
            relx=0.62,
            rely=0.89,
            height=35,
            width=190
        )

        self.ai_ask_button.place(
            relx=0.86,
            rely=0.89,
            width=113,
            height=35
        )

        self.aiScrolledText.configure(
            state=tk.DISABLED
        )

        self.aiScrolledText.place(
            relx=0.62,
            rely=0.1,
            height=238
        )

        # Show CSV data
        self.scrolledText.insert(
            tk.END,
            self.data.to_csv(index=False)
        )

        self.scrolledText.place(
            relx=0.0,
            rely=0.1
        )

        self.mainloop()
