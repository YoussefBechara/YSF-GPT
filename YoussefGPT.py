import threading
import queue
from tkinter import Tk, Entry, Text, N, S, E, W, END, Button, filedialog, Label, font, messagebox
from hugchat import hugchat
from hugchat.login import Login
from bing_image_downloader import downloader
import os
from PIL import Image, ImageTk
import tkinter as tk
#import fitz  # PyMuPDF
from gtts import gTTS
from langdetect import detect
from pydub import AudioSegment
from pydub.playback import play
import io
import speech_recognition as sr
import google.generativeai as genai
import pygame

class YSF_GPT_GUI:
    def __init__(self):
        self.response_queue = queue.Queue()
        global last_response
        last_response = ""

        self.chat_bot_name = 'YsfGPT'
        
        
        web_search_option = 'False'
        
        self.setup_credentials()
        #setting up LLMs to not reinitialize them everytime
        self.setup_LLMs()
        
        self.root = Tk()
        self.root.title(self.chat_bot_name)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        root_width = int(screen_width * 0.8)
        root_height = int(screen_height * 0.8)
        self.root.geometry(f"{root_width}x{root_height}")

        # Set the background color of the window
        self.root.configure(bg='#333444')
        button_bg_color='#444444'
        # Create a font with your preferred attributes
        custom_font = font.Font(family="Segoe UI", size=12, weight="bold")

        # Apply the custom font to the widgets where you want to change the font
        self.chat_log = Text(self.root, state='disabled', bg=button_bg_color, fg='white', font=custom_font)
        self.input_box = Entry(self.root, width=root_width - root_width // 2, borderwidth=5, bg=button_bg_color, fg='white', font=custom_font)
        send_button = Button(self.root, text="Send", command=self.send_message, bg=button_bg_color, fg='white', font=custom_font)
        copy_button = Button(self.root, text="Copy", command=self.copy_to_clipboard, bg=button_bg_color, fg='white', font=custom_font)
        native_button = Button(self.root, text="Native", command=self.native, bg=button_bg_color, fg='white', font=custom_font)
        translate_button = Button(self.root, text="Translate", command=self.translate, bg=button_bg_color, fg='white', font=custom_font)
        detail_button = Button(self.root, text="Detail", command=self.detail, bg=button_bg_color, fg='white', font=custom_font)
        upload_button = Button(self.root, text="Upload", command=self.open_file, bg=button_bg_color, fg='white', font=custom_font)
        summarize_button = Button(self.root, text="Summarize", command=self.summarize, bg=button_bg_color, fg='white', font=custom_font)
        generate_image_button = Button(self.root, text="Generate Image", command=self.generate_image, bg=button_bg_color, fg='white', font=custom_font)
        grammar_button = Button(self.root, text="Grammar", command=self.grammarize, bg=button_bg_color, fg='white', font=custom_font)
        pronciation_button = Button(self.root, text="Prononciate", command=self.prononciate, bg=button_bg_color, fg='white', font=custom_font)
        speech_to_text_button = Button(self.root, text="Send Voice", command=self.speech_to_text, bg=button_bg_color, fg='white', font=custom_font)
        wbsearch_button = Button(self.root, text="Web_search", command=self.websearch_button, bg=button_bg_color, fg='white', font=custom_font)
        ttai_button = Button(self.root, text="Talk Conversation", command=self.talk_to_ai, bg=button_bg_color, fg='white', font=custom_font)

        # Grid placement for each widget
        self.chat_log.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        self.input_box.grid(row=1, column=0, columnspan=1, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        send_button.grid(row=1, column=1, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        copy_button.grid(row=0, column=4, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        native_button.grid(row=1, column=4, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        translate_button.grid(row=2, column=0, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        detail_button.grid(row=2, column=1, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        upload_button.grid(row=1, column=2, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        summarize_button.grid(row=2, column=4, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        generate_image_button.grid(row=3, column=0, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        grammar_button.grid(row=2, column=2, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        pronciation_button.grid(row=2, column=4, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        speech_to_text_button.grid(row=3, column=2, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        wbsearch_button.grid(row=3, column=4, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
        ttai_button.grid(row=4, column=0, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)

        image_label = Label(self.root)
        image_label.grid(row=3, column=1, padx=10, pady=10, sticky=N + S + E + W)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=3)


        self.root.bind('<Return>', self.send_message)

        self.update_chat_log()
        self.root.configure(bg='black')

        self.chat_log.config(state='normal')
        self.chat_log.insert(END, f"Welcome! I'm {self.chat_bot_name}, Your personal AI assistant.\n\n")
        self.chat_log.config(state='disabled')

        self.root.mainloop()

    def setup_credentials(self):
        try:
            with open('Credentials.txt', "r") as file:
                lines = file.readlines()
                self.hg_email = lines[0].split(": ")[1].strip()
                self.hg_passwd = lines[1].split(": ")[1].strip()
                self.gemini_api_key = lines[2].split(": ")[1].strip()
                print('Credentials loaded from Credentials.txt')
        except:
            self.hg_email = input('Input your huggingface email (optional): ')
            self.hg_passwd = input('Input your huggingface password (optional): ')
            self.gemini_api_key = input('Input your gemini api key (optional): ')
            with open('Credentials.txt', "w") as file:
                file.write(f"HuggingFace Email: {self.hg_email}\n")
                file.write(f"HuggingFace Password: {self.hg_passwd}\n")
                file.write(f"Gemini API Key: {self.gemini_api_key}\n")
            print(f"Credentials saved to Credentials.txt")

    def setup_LLMs(self):
        try:
            sign = Login(self.hg_email, self.hg_passwd)
            cookies = sign.login()
            cookie_path_dir = "./cookies_snapshot"
            sign.saveCookiesToDir(cookie_path_dir)
            self.chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
            self.conv_id = self.chatbot.new_conversation()
            self.chatbot.change_conversation(self.conv_id)
        except:
            print('Error: HuggingFace credentials not found or are incorrect. Please input your credentials in the setup_credentials() function.')
        try:
            #print(self.gemini_api_key)        
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            print('Error: Gemini API key not found or is incorrect. Please input your credentials in the setup_credentials() function.')

    def query_LLM(self, text, LLM='gemini'):
        global last_response
        global cookies
        if LLM == 'hugchat':
            if web_search_option == 'True':
                response = self.chatbot.chat(text, web_search=True)
                last_response += response
                self.response_queue.put(response)
                for source in response.web_search_sources:
                    self.response_queue.put(source.link)
            else:
                response = self.chatbot.chat(text)
                last_response += response
                self.response_queue.put(response)
        elif LLM == 'gemini':
            response = self.model.generate_content(text)
            self.response_queue.put(response.text)
    def websearch_button(self):
        global web_search_option
        if web_search_option == 'True':
            web_search_option = 'False'
        else:
            web_search_option = 'True'
            
    def get_image(self, query,path='images',size='',color='',type='',layout=''):
        downloader.download(query, limit=1, output_dir=path, adult_filter_off=True, force_replace=False, timeout=60, verbose=True)
        
    def copy_to_clipboard(self):  # Get the last response from the chat log
        global last_response
        self.root.clipboard_clear()  # Clear the clipboard contents
        self.root.clipboard_append(last_response)  # Append the response to the clipboard
        last_response = ""
        
    def send_message(self,event=None):
        message = self.input_box.get()
        self.input_box.delete(0, END)
        self.chat_log.config(state='normal')
        self.chat_log.insert(END, '>You: ' + message + '\n')
        self.chat_log.insert(END, f'>{self.chat_bot_name}: Generating...\n')
        self.chat_log.config(state='disabled')
        threading.Thread(target=self.query_LLM, args=(message,)).start()
        self.root.after(100, self.update_chat_log)

    def detail(self, event=None):
        message = f"Please make this text more detailed: {last_response}"
        self.input_box.delete(0, END)
        self.chat_log.config(state='normal')
        self.chat_log.insert(END, '>You: Detail please' + '\n')
        self.chat_log.insert(END, f'>{self.chat_bot_name}: Detailing...\n')
        self.chat_log.config(state='disabled')
        threading.Thread(target=self.query_LLM, args=(message,)).start()
        self.root.after(100, self.update_chat_log)

    def native(self,event=None):
        txt = self.input_box.get()
        message = f"Please make this text sound native speakers: {txt}"
        self.input_box.delete(0, END)
        self.chat_log.config(state='normal')
        self.chat_log.insert(END, '>You: make it more native please' + '\n')
        self.chat_log.insert(END,f'>{self.hat_bot_name}: Making it sound native...\n')
        self.chat_log.config(state='disabled')
        threading.Thread(target=self.query_LLM, args=(message,)).start()
        self.root.after(100, self.update_chat_log)

    def translate(self, event=None):
        lang = self.input_box.get()
        message = f"Please translate this text to {lang} language: {last_response}"
        self.input_box.delete(0, END)
        self.chat_log.config(state='normal')
        self.chat_log.insert(END, '>You: Translate please' + '\n')
        self.chat_log.insert(END, f'>{self.chat_bot_name}: Translating...\n')
        self.chat_log.config(state='disabled')
        threading.Thread(target=self.query_LLM, args=(message,)).start()
        self.root.after(100, self.update_chat_log)

    def summarize(self,event=None):
        message = f"Please summarize this text : {last_response}"
        self.input_box.delete(0, END)
        self.chat_log.config(state='normal')
        self.chat_log.insert(END, '>You: Summarize please' + '\n')
        self.chat_log.insert(END, f'>{self.chat_bot_name}: Summarizing...\n')
        self.chat_log.config(state='disabled')
        threading.Thread(target=self.query_LLM, args=(message,)).start()
        self.root.after(100, self.update_chat_log)

    def generate_image(self):
        query = self.input_box.get()
        self.input_box.delete(0, END)
        self.get_image(query=query)

        # Assuming the image is saved with a standard name like 'Image_1.jpg' inside the dynamically named folder
        folder_name = f'images\\{query}'  # Update this to match the actual naming convention
        image_path = os.path.join(folder_name, 'Image_1.jpg')

        try:
            image = Image.open(image_path)
        except FileNotFoundError:
            image_path = os.path.join(folder_name, 'Image_1.png')
            try:
                image = Image.open(image_path)
            except FileNotFoundError:
                image_path = os.path.join(folder_name, 'Image_1.jpeg')
        image.thumbnail((300, 300))  # Adjust the size as needed
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo
    def update_chat_log(self):
        if not self.response_queue.empty():
            response = self.response_queue.get()
            self.chat_log.config(state='normal')
            self.chat_log.delete('end-2l', 'end-1c')  # Delete the 'Generating...' message
            self.chat_log.insert(END, 'ChatBot: ' + response + '\n\n\n')  # Add three newlines after the response
            self.chat_log.see(END)
            self.chat_log.config(state='disabled')
        self.root.after(100, self.update_chat_log)

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt'), ('PDF Files', '*.pdf'), ('Word Files', '*.docx')])
        
        if filename:
            content = ""

            if filename.lower().endswith(".txt"):
                with open(filename, 'r') as file:
                    content = file.read()
            elif filename.lower().endswith(".pdf"):
                content = self.read_text_from_pdf(filename)
            elif filename.lower().endswith(".docx"):
                #content = read_text_from_docx(filename)
                pass
            else:
                messagebox.showinfo("Unsupported File", "Unsupported file type. Please select a .txt, .pdf, or .docx file.")
                return

            prompt = self.input_box.get()
            message = f"{prompt} {content}"

            self.input_box.delete(0, END)
            self.chat_log.config(state='normal')
            self.chat_log.insert(END, 'You: ' + message + '\n')
            self.chat_log.insert(END, 'ChatBot: Generating...\n')
            self.chat_log.config(state='disabled')

            threading.Thread(target=self.query_LLM, args=(message,)).start()
            self.root.after(100, self.update_chat_log)

    # def read_text_from_pdf(self,pdf_path):
    #     text = ""
    #     try:
    #         with fitz.open(pdf_path) as pdf_document:
    #             for page_number in range(pdf_document.page_count):
    #                 page = pdf_document[page_number]
    #                 text += page.get_text()
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Error reading PDF: {str(e)}")
    #     return text

    def grammarize(self,):
        input_words = self.input_box.get()
        message = f"Offer me quick tips or explanations on English grammar rules concerning this: {input_words}"
        self.input_box.delete(0, END)
        self.chat_log.config(state='normal')
        self.chat_log.insert(END, '>You:  Help me Grammaticaly please!!' + '\n')
        self.chat_log.insert(END, f'>{self.chat_bot_name}: Generating grammar tips/lesson...\n')
        self.chat_log.config(state='disabled')
        threading.Thread(target=self.query_LLM, args=(message,)).start()
        self.root.after(100, self.update_chat_log)

    def detect_language(self,input_text):
        try:
            language = detect(input_text)
            return language
        except Exception as e:
            print(f"Error: {e}")
            return None

    def prononciate(self):
        txt = self.input_box.get()
        language = self.detect_language(txt)
        self.input_box.delete(0, END)
        self.chat_log.config(state='normal')
        self.chat_log.insert(END, f'>You: Help me pronounce this please: {txt}' + '\n')
        self.chat_log.insert(END, f'>{self.chat_bot_name}: Generating the speech...\n')
        
        self.speak(txt=txt, language=language)
        self.chat_log.insert(END, f'>{self.chat_bot_name}: listen to the speech!\n')
        self.chat_log.config(state='disabled')
        self.root.after(100, self.update_chat_log)

    def speak(self,txt, language='en'):
        tts = gTTS(text=txt, lang=language, slow=False)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_fp, 'mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
    def speech_to_text(self):
        def recognize_speech():
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

                try:
                    text = recognizer.recognize_google(audio)
                    self.input_box.insert(END, f'{text}')
                except sr.UnknownValueError:
                    print("Could not understand audio.")
                except sr.RequestError as e:
                    print(f"Error making the request: {e}")

        recognizer = sr.Recognizer()

        self.chat_log.config(state='normal')
        self.chat_log.insert(END, f'>{self.chat_bot_name} : Wait 2 secs then Say something...\n')
        self.chat_log.config(state='disabled')
        self.root.after(100, self.update_chat_log)

        # start the speech recognition in a new thread
        threading.Thread(target=recognize_speech).start()

    def talk_to_ai(self):
        from Talk_to_LLM import Convo_GUI
        conv_gui = Convo_GUI()
        conv_gui.conversation()


if __name__ == '__main__':
    gui = YSF_GPT_GUI()

