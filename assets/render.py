from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from openai import OpenAI
import tkinter as tk
import pandas as pd
import threading
import json
import re
import io, shutil
import subprocess
import sys

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
            label="Use Pandas Functions",
            command=self.open_pandas_code_editor
        )
        self.menu.add_command(
            label="AI Settings",
            command=self.open_ai_settings
        )

        self.menu.add_command(
            label="Fill blank data",
            command=self.fill_blank_data
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
            self.model_name = data["model.name"]

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



    def open_pandas_code_editor(self):
        def run():
            user_code = code_input.get('1.0', tk.END).strip()
            if not user_code:
                return

            # Wrap user code so `data` is preloaded
            wrapped = (
                "import pandas as pd\n"
                f"data = pd.read_csv({self.file_path!r})\n"
                "import io, sys\n"
                "buf = io.StringIO()\n"
                "_stdout = sys.stdout\n"
                "sys.stdout = buf\n"
                "try:\n"
                f"    {user_code.replace(chr(10), chr(10) + '    ')}\n"
                "finally:\n"
                "    sys.stdout = _stdout\n"
                "print(buf.getvalue())\n"
            )

            result = subprocess.run(
                [sys.executable, "-c", wrapped],
                capture_output=True,
                text=True
            )
            out = result.stdout or ""
            if result.stderr:
                out += "\n--- stderr ---\n" + result.stderr

            result_input.configure(state="normal")
            result_input.delete("1.0", tk.END)
            result_input.insert(tk.END, out)
            result_input.configure(state="disabled")

        win = tk.Tk()
        win.geometry('400x300')
        win.title('Pandas Code Editor')

        code_input = ScrolledText(win,height=15)
        code_input.place(relx=0.0,rely=0.0,width=200)
        code_input.insert(tk.END, "# your data has been saved in 'data' variable.")

        result_input = ScrolledText(win,height=15, state="disabled")
        result_input.place(relx=0.5,rely=0.0,width=200)

        run_button = tk.Button(win, text="Run", width=47, height=2, command=run,)
        run_button.place(relx=0.0,rely=0.86)

        win.mainloop()

    def open_ai_settings(self):
        def save():
            new_data = json_scrolled_text.get("1.0", tk.END)
            new_data = json.loads(new_data)
            json.dump(new_data,open('./assets/data.json','w'), indent=4)

            with open('./assets/data.json', 'r') as file:
                data = json.load(file)

            self.ai_base_url = data["env.base.api.url"]
            self.ai_api_key = data["env.api.key"]
            self.model_name = data["model.name"]

            self.client = OpenAI(
                api_key=self.ai_api_key,
                base_url=self.ai_base_url
            )

        win = tk.Tk()
        win.geometry('500x300')
        win.title('Ai settings')

        json_data = open('./assets/data.json','r').read()
        json_scrolled_text = ScrolledText(win,height=15)
        json_scrolled_text.insert(tk.END, json_data)
        json_scrolled_text.place(relx=0.0,rely=0.0,width=500)

        save_button = tk.Button(win, text="Save", width=60, height=2, command=save)
        save_button.place(relx=0.0,rely=0.86)

        win.mainloop()



    def fill_blank_data(self):
        try:
            # Read the latest CSV from ScrolledText
            csv_text = self.scrolledText.get('1.0', tk.END)

            self.data = pd.read_csv(io.StringIO(csv_text))

            # Fill missing values
            for column in self.data.columns:
                if pd.api.types.is_numeric_dtype(self.data[column]):
                    median = self.data[column].median()

                    self.data[column] = self.data[column].fillna(
                        median if pd.notna(median) else 0
                    )
                else:
                    self.data[column] = self.data[column].fillna('Empty')

            # Update ScrolledText
            self.scrolledText.delete('1.0', tk.END)
            self.scrolledText.insert(
                tk.END,
                self.data.to_csv(index=False)
            )

            # Save CSV
            self.data.to_csv(self.file_path, index=False)

        except Exception as e:
            messagebox.showerror('Error', str(e))




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
            csv_context = self.data.to_csv(index=False)

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
                model=self.model_name,
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

    def validate_ai_csv(self, new_csv_text, original_df):
        try:
            new_df = pd.read_csv(io.StringIO(new_csv_text))
        except Exception as e:
            messagebox.showerror('Invalid CSV', f'Cannot read ai answer:\n\n{e}')
            return None

        if len(new_df) == 0:
            messagebox.showerror('Empty CSV', 'AI result is empty')
            return None

        return new_df

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

        if edit_confirmation:
            new_df = self.validate_ai_csv(edit_confirmation, self.data)
            if new_df is None:
                self.ai_busy = False
                self.ai_ask_button.config(state=tk.NORMAL)
                return

            try:
                shutil.copy2(self.file_path, self.file_path + '.bak')
            except Exception as e:
                messagebox.showerror('Backup Failed', str(e))
                return

            try:
                new_df.to_csv(self.file_path, index=False)
            except Exception as e:
                messagebox.showerror('Save Error', f'Data did not save:\n\n{e}')
                return

            self.data = new_df

            self.scrolledText.delete('1.0', tk.END)
            self.scrolledText.insert(tk.END, new_df.to_csv(index=False))

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

        tk.Label(self, text="Chatbot : use ai to fix your data easily", font=('Arial',14)).place(relx=0.62, rely=0.01)

        self.mainloop()
