from tkinter import Tk, N, S, E, W, END, Button
from hugchat import hugchat
from hugchat.login import Login
from tkinter import font
import tkinter as tk
from gtts import gTTS
from langdetect import detect
import pygame
import speech_recognition as sr
import io
import google.generativeai as genai

class Convo_GUI:
    def __init__(self):
        self.chat_bot_name = 'YsfGPT'
        self.setup_credentials()
        self.setup_LLMs()
        #setting up LLMs to not reinitialize them everytime
        self.setup_LLMs()
        self.root = Tk()
        self.root.title(self.chat_bot_name)

        # mic_image = tk.PhotoImage(file="assets\\listening.png")  # Change "mic_image.png" to your mic icon file
        # face_image = tk.PhotoImage(file="assets\\assistant_face.png")  # Change "face_image.png" to your face icon file
        
        self.query_LLM('I want to have a conversation with you like humans from now on , so please respond like a human and with a very short response')
        screen_width = 300
        screen_height = 300

        root_width, root_height = int(screen_width * 0.8),int(screen_height * 0.8)
        
        self.root.geometry(f"{root_width}x{root_height}")

        # Set the background color of the window
        self.root.configure(bg='#333444')
        button_bg_color='#444444'
        # Create a font with your preferred attributes
        custom_font = font.Font(family="Segoe UI", size=12, weight="bold")

        start_button = Button(self.root, text="Start Conversation", command=self.conversation, bg=button_bg_color, fg='white', font=custom_font)
        start_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)

        self.root.configure(bg='black')

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
        if LLM == 'hugchat':
            response = self.chatbot.chat(text)
            last_response += response
            return response 
        elif LLM == 'gemini':
            response = self.model.generate_content(text)
            return response.text

    def detect_language(self, input_text):
        try:
            language = detect(input_text)
            return language
        except Exception as e:
            print(f"Error: {e}")
            return None

    def play_audio(self,file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for the sound to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def text_to_speech(self,txt):
        language = self.detect_language(txt)

        tts = gTTS(text=txt, lang=language, slow=False)

        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_fp, 'mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def speech_to_text(self,num_of_reps=0):
        def recognize_speech():
            while True:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source)

                    try:
                        text = recognizer.recognize_google(audio)
                        return text
                    except sr.UnknownValueError:
                        if num_of_reps == 0:
                            self.text_to_speech("Sorry I couldn't quite catch what you said, kindly speak again.")
                        continue
                    except sr.RequestError as e:
                        print(f"Error making the request: {e}")

        recognizer = sr.Recognizer()

        # start the speech recognition in a new thread
        text = recognize_speech()
        return text

    def conversation(self):
        self.text_to_speech('Hello, How are you doing today?')
        i=0
        while True:
            txt = self.speech_to_text()
            response = self.query_LLM(text=txt)
            self.text_to_speech(response)
            i+=1

    

    

if __name__ == '__main__':
    gui = Convo_GUI()
    gui.conversation()