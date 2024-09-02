import threading
import queue
from tkinter import Tk, Entry, Text, N, S, E, W, END, Button, filedialog, Label, font, messagebox
from hugchat import hugchat
from hugchat.login import Login
from bing_image_downloader import downloader
import os
from PIL import Image, ImageTk
import tkinter as tk
import fitz  # PyMuPDF
from gtts import gTTS
from langdetect import detect
import pygame
import speech_recognition as sr
import subprocess
response_queue = queue.Queue()
global last_response
last_response = ""

chat_bot_name = 'YsfGPT'
try:
    with open('Credentials.txt', "r") as file:
        lines = file.readlines()
        email = lines[0].split(": ")[1].strip()
        passwd = lines[1].split(": ")[1].strip()
except:
    email = input('Input your huggingface email: ')
    passwd = input('Input your huggingface password: ')
    with open('Credentials.txt', "w") as file:
        file.write(f"Email: {email}\n")
        file.write(f"Password: {passwd}\n")
    print(f"Credentials saved to Credentials.txt")
web_search_option = 'False'

sign = Login(email, passwd)
cookies = sign.login()
cookie_path_dir = "./cookies_snapshot"
sign.saveCookiesToDir(cookie_path_dir)
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
conv_id = chatbot.new_conversation()

def ask_hugchat(text):
    global last_response
    global cookies
    global chatbot
    chatbot.change_conversation(conv_id)
    if web_search_option == 'True':
        response = chatbot.chat(text, web_search=True)
        last_response += response
        response_queue.put(response)
        for source in response.web_search_sources:
            response_queue.put(source.link)
    else:
        response = chatbot.chat(text)
        last_response += response
        response_queue.put(response)

def websearch_button():
    global web_search_option
    if web_search_option == 'True':
        web_search_option = 'False'
    else:
        web_search_option = 'True'
def get_image(query,path='images',size='',color='',type='',layout=''):
    downloader.download(query, limit=1, output_dir=path, adult_filter_off=True, force_replace=False, timeout=60, verbose=True)
    
def copy_to_clipboard():  # Get the last response from the chat log
    global last_response
    root.clipboard_clear()  # Clear the clipboard contents
    root.clipboard_append(last_response)  # Append the response to the clipboard
    last_response = ""
    
def send_message(event=None):
    message = input_box.get()
    input_box.delete(0, END)
    chat_log.config(state='normal')
    chat_log.insert(END, '>You: ' + message + '\n')
    chat_log.insert(END, f'>{chat_bot_name}: Generating...\n')
    chat_log.config(state='disabled')
    threading.Thread(target=ask_hugchat, args=(message,)).start()
    root.after(100, update_chat_log)

def detail(event=None):
    message = f"Please make this text more detailed: {last_response}"
    input_box.delete(0, END)
    chat_log.config(state='normal')
    chat_log.insert(END, '>You: Detail please' + '\n')
    chat_log.insert(END, f'>{chat_bot_name}: Detailing...\n')
    chat_log.config(state='disabled')
    threading.Thread(target=ask_hugchat, args=(message,)).start()
    root.after(100, update_chat_log)

def native(event=None):
    txt = input_box.get()
    message = f"Please make this text sound native speakers: {txt}"
    input_box.delete(0, END)
    chat_log.config(state='normal')
    chat_log.insert(END, '>You: make it more native please' + '\n')
    chat_log.insert(END,f'>{chat_bot_name}: Making it sound native...\n')
    chat_log.config(state='disabled')
    threading.Thread(target=ask_hugchat, args=(message,)).start()
    root.after(100, update_chat_log)

def translate(event=None):
    lang = input_box.get()
    message = f"Please translate this text to {lang} language: {last_response}"
    input_box.delete(0, END)
    chat_log.config(state='normal')
    chat_log.insert(END, '>You: Translate please' + '\n')
    chat_log.insert(END, f'>{chat_bot_name}: Translating...\n')
    chat_log.config(state='disabled')
    threading.Thread(target=ask_hugchat, args=(message,)).start()
    root.after(100, update_chat_log)

def summarize(event=None):
    message = f"Please summarize this text : {last_response}"
    input_box.delete(0, END)
    chat_log.config(state='normal')
    chat_log.insert(END, '>You: Summarize please' + '\n')
    chat_log.insert(END, f'>{chat_bot_name}: Summarizing...\n')
    chat_log.config(state='disabled')
    threading.Thread(target=ask_hugchat, args=(message,)).start()
    root.after(100, update_chat_log)

def generate_image():
    query = input_box.get()
    input_box.delete(0, END)
    get_image(query=query)

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
    image_label.config(image=photo)
    image_label.image = photo
def update_chat_log():
    if not response_queue.empty():
        response = response_queue.get()
        chat_log.config(state='normal')
        chat_log.delete('end-2l', 'end-1c')  # Delete the 'Generating...' message
        chat_log.insert(END, 'ChatBot: ' + response + '\n\n\n')  # Add three newlines after the response
        chat_log.see(END)
        chat_log.config(state='disabled')
    root.after(100, update_chat_log)

def open_file():
    filename = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt'), ('PDF Files', '*.pdf'), ('Word Files', '*.docx')])
    
    if filename:
        content = ""

        if filename.lower().endswith(".txt"):
            with open(filename, 'r') as file:
                content = file.read()
        elif filename.lower().endswith(".pdf"):
            content = read_text_from_pdf(filename)
        elif filename.lower().endswith(".docx"):
            #content = read_text_from_docx(filename)
            pass
        else:
            messagebox.showinfo("Unsupported File", "Unsupported file type. Please select a .txt, .pdf, or .docx file.")
            return

        prompt = input_box.get()
        message = f"{prompt} {content}"

        input_box.delete(0, END)
        chat_log.config(state='normal')
        chat_log.insert(END, 'You: ' + message + '\n')
        chat_log.insert(END, 'ChatBot: Generating...\n')
        chat_log.config(state='disabled')

        threading.Thread(target=ask_hugchat, args=(message,)).start()
        root.after(100, update_chat_log)

def read_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as pdf_document:
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                text += page.get_text()
    except Exception as e:
        messagebox.showerror("Error", f"Error reading PDF: {str(e)}")
    return text

def grammarize():
    input_words = input_box.get()
    message = f"Offer me quick tips or explanations on English grammar rules concerning this: {input_words}"
    input_box.delete(0, END)
    chat_log.config(state='normal')
    chat_log.insert(END, '>You:  Help me Grammaticaly please!!' + '\n')
    chat_log.insert(END, f'>{chat_bot_name}: Generating grammar tips/lesson...\n')
    chat_log.config(state='disabled')
    threading.Thread(target=ask_hugchat, args=(message,)).start()
    root.after(100, update_chat_log)

def detect_language(input_text):
    try:
        language = detect(input_text)
        return language
    except Exception as e:
        print(f"Error: {e}")
        return None

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def prononciate():
    txt = input_box.get()
    language = detect_language(txt)
    input_box.delete(0, END)
    chat_log.config(state='normal')
    chat_log.insert(END, f'>You: Help me pronounce this please: {txt}' + '\n')
    chat_log.insert(END, f'>{chat_bot_name}: Generating the speech...\n')
    

    tts = gTTS(text=txt, lang=language, slow=False)

    # Saving the converted audio in a file
    tts.save("output.mp3")

    # Playing the converted audio file
    play_audio("output.mp3")
    chat_log.insert(END, f'>{chat_bot_name}: listen to the speech!\n')
    chat_log.config(state='disabled')
    root.after(100, update_chat_log)

def speech_to_text():
    def recognize_speech():
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio)
                input_box.insert(END, f'{text}')
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Error making the request: {e}")

    recognizer = sr.Recognizer()

    chat_log.config(state='normal')
    chat_log.insert(END, f'>{chat_bot_name} : Wait 2 secs then Say something...\n')
    chat_log.config(state='disabled')
    root.after(100, update_chat_log)

    # start the speech recognition in a new thread
    threading.Thread(target=recognize_speech).start()

def talk_to_ai():
    from talk_to_hugchat import main
    main(email=email, password=passwd)
    
root = Tk()
root.title(chat_bot_name)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root_width = int(screen_width * 0.8)
root_height = int(screen_height * 0.8)
root.geometry(f"{root_width}x{root_height}")

# Set the background color of the window
root.configure(bg='#333444')
button_bg_color='#444444'
# Create a font with your preferred attributes
custom_font = font.Font(family="Segoe UI", size=12, weight="bold")

# Apply the custom font to the widgets where you want to change the font
chat_log = Text(root, state='disabled', bg=button_bg_color, fg='white', font=custom_font)
input_box = Entry(root, width=root_width - root_width // 2, borderwidth=5, bg=button_bg_color, fg='white', font=custom_font)
send_button = Button(root, text="Send", command=send_message, bg=button_bg_color, fg='white', font=custom_font)
copy_button = Button(root, text="Copy", command=copy_to_clipboard, bg=button_bg_color, fg='white', font=custom_font)
native_button = Button(root, text="Native", command=native, bg=button_bg_color, fg='white', font=custom_font)
translate_button = Button(root, text="Translate", command=translate, bg=button_bg_color, fg='white', font=custom_font)
detail_button = Button(root, text="Detail", command=detail, bg=button_bg_color, fg='white', font=custom_font)
upload_button = Button(root, text="Upload", command=open_file, bg=button_bg_color, fg='white', font=custom_font)
summarize_button = Button(root, text="Summarize", command=summarize, bg=button_bg_color, fg='white', font=custom_font)
generate_image_button = Button(root, text="Generate Image", command=generate_image, bg=button_bg_color, fg='white', font=custom_font)
grammar_button = Button(root, text="Grammar", command=grammarize, bg=button_bg_color, fg='white', font=custom_font)
pronciation_button = Button(root, text="Prononciate", command=prononciate, bg=button_bg_color, fg='white', font=custom_font)
speech_to_text_button = Button(root, text="Send Voice", command=speech_to_text, bg=button_bg_color, fg='white', font=custom_font)
wbsearch_button = Button(root, text="Web_search", command=websearch_button, bg=button_bg_color, fg='white', font=custom_font)
ttai_button = Button(root, text="Talk Conversation", command=talk_to_ai, bg=button_bg_color, fg='white', font=custom_font)

# Grid placement for each widget
chat_log.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
input_box.grid(row=1, column=0, columnspan=1, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)
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

image_label = Label(root)
image_label.grid(row=3, column=1, padx=10, pady=10, sticky=N + S + E + W)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=3)


root.bind('<Return>', send_message)

update_chat_log()
root.configure(bg='black')

chat_log.config(state='normal')
chat_log.insert(END, f"Welcome! I'm {chat_bot_name}, Your personal AI assistant.\n\n")
chat_log.config(state='disabled')

root.mainloop()
