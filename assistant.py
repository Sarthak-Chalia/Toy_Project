import os
import json
import speech_recognition as sr
import pyttsx3
from langchain_together import ChatTogether
from langchain.schema import HumanMessage, SystemMessage
import time
import pvporcupine
import sounddevice as sd
import numpy as np
import struct
from uuid import uuid4

# Configuration
os.environ["OPENAI_API_KEY"] = "4d10c2b5824d38cca324cb9f5a6464fa55b0379f1e8fb31d1275e4a74cc063fc"
MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
TEMPERATURE = 0.7
WAKE_WORD = "porcupine" 
USER_DB = 'users.json'  
CHAT_HISTORY_DB = 'chat_history.json'
MAX_HISTORY_LENGTH = 10  # Number of messages to keep in context

# Initialize text-to-speech engine
def init_tts():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[0].id)
    return engine

def initialize_model():
    return ChatTogether(model=MODEL, temperature=TEMPERATURE)

def get_response(llm, messages):
    return llm.invoke(messages).content

def listen_for_activation():
    """Listens for the wake word using Porcupine (offline)."""
    print("\n🔇 System is sleeping. Say 'porcupine' to activate...")
    
    porcupine = pvporcupine.create(
        access_key="gL3VkwAs+E3SAzJPUHhN/k7R2NRS5lNzDazkojDzgb2ovI/6XFghIQ==",
        keywords=["porcupine"]  
    )
    
    try:
        with sd.RawInputStream(
            samplerate=porcupine.sample_rate,
            blocksize=porcupine.frame_length,
            dtype='int16',
            channels=1
        ) as stream:
            while True:
                audio_frame, _ = stream.read(porcupine.frame_length)
                audio_frame = struct.unpack_from("h" * porcupine.frame_length, audio_frame)
                if porcupine.process(audio_frame) >= 0:
                    print("\n🎤 Wake word detected!")
                    return True
    finally:
        porcupine.delete()

def get_voice_input(recognizer, prompt=None):
    if prompt:
        speak_response(prompt)
    with sr.Microphone() as mic:
        try:
            recognizer.adjust_for_ambient_noise(mic, duration=0.5)
            audio = recognizer.listen(mic, timeout=9, phrase_time_limit=27)
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            speak_response("Couldn't understand audio")
            return ""
        except sr.RequestError as e:
            speak_response(f"Speech service error: {e}")
            return ""
        except sr.WaitTimeoutError:
            speak_response("No voice detected")
            return ""

def speak_response(text):
    print(f"System: {text}\n")
    engine.say(text)
    engine.runAndWait()

def load_users():
    """Load user data from JSON file"""
    if os.path.exists(USER_DB):
        with open(USER_DB, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save user data to JSON file"""
    with open(USER_DB, 'w') as f:
        json.dump(users, f, indent=2)

def load_chat_history():
    """Load chat history from JSON file"""
    if os.path.exists(CHAT_HISTORY_DB):
        with open(CHAT_HISTORY_DB, 'r') as f:
            return json.load(f)
    return {}

def save_chat_history(history):
    """Save chat history to JSON file"""
    with open(CHAT_HISTORY_DB, 'w') as f:
        json.dump(history, f, indent=2)

def update_chat_history(user_id, role, content):
    """Update chat history for a specific user"""
    history = load_chat_history()
    
    if user_id not in history:
        history[user_id] = []
    
    # Add new message
    history[user_id].append({
        "role": role,
        "content": content,
        "timestamp": time.time()
    })
    
    # Keep only the most recent messages
    if len(history[user_id]) > MAX_HISTORY_LENGTH:
        history[user_id] = history[user_id][-MAX_HISTORY_LENGTH:]
    
    save_chat_history(history)
    return history[user_id]

def prepare_messages(user_id, new_input):
    """Prepare the conversation history with the new input"""
    history = load_chat_history()
    user_history = history.get(user_id, [])
    
    messages = []
    
    # Add system message if it's a new conversation
    if len(user_history) == 0:
        messages.append(SystemMessage(content="You are a helpful AI assistant."))
    
    # Add previous conversation history
    for msg in user_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(SystemMessage(content=msg["content"]))
    
    # Add the new user input
    messages.append(HumanMessage(content=new_input))
    
    return messages

def case_insensitive_compare(input_str, stored_str):
    """Compare strings case-insensitively"""
    return input_str.lower() == stored_str.lower()

def get_existing_user(users, username):
    """Find existing user with case-insensitive match"""
    for stored_user in users:
        if case_insensitive_compare(username, stored_user):
            return stored_user
    return None

def authenticate_user(recognizer):
    """Voice-based authentication system"""
    users = load_users()
    
    while True:
        # Get username via voice
        username = get_voice_input(recognizer, "Please say your username")
        
        if not username:
            speak_response("Username cannot be empty. Please try again.")
            continue
        
        stored_username = get_existing_user(users, username)
        
        if stored_username:
            # Existing user - handle password attempts
            attempts = 3
            while attempts > 0:
                password = get_voice_input(recognizer, f"Welcome {stored_username}. Please say your password")
                
                if case_insensitive_compare(password, users[stored_username]):
                    speak_response(f"Authentication successful! Welcome back, {stored_username}!")
                    return stored_username
                else:
                    attempts -= 1
                    if attempts > 0:
                        speak_response(f"Incorrect password. {attempts} attempt(s) remaining.")
                    else:
                        speak_response("Too many failed attempts. Please start over.")
                        break
        else:
            # New user - create account
            speak_response("New user detected. Let's create your account.")
            
            while True:
                password = get_voice_input(recognizer, "Please say your new password")
                
                if not password:
                    speak_response("Password cannot be empty. Please try again.")
                    continue
                
                confirm = get_voice_input(recognizer, "Please confirm your password")
                
                if password == confirm:
                    # Store with the original casing they entered
                    users[username] = password
                    save_users(users)
                    speak_response(f"Account created successfully! Welcome, {username}!")
                    return username
                else:
                    speak_response("Passwords don't match. Please try again.")

def main():
    global engine
    llm = initialize_model()
    engine = init_tts()
    recognizer = sr.Recognizer()
    
    print("\n" + "="*40)
    print(" Voice-Activated Authentication Chatbot ".center(40, '~'))
    print("="*40)
    print(f"\nSystem is in sleep mode. Say '{WAKE_WORD}' to activate.\n")
    
    try:
        while True:
            # Wait for wake word (offline)
            if listen_for_activation():
                # Authenticate user first
                username = authenticate_user(recognizer)
                
                if username:
                    # Get voice input (online)
                    user_input = get_voice_input(recognizer, "Authentication successful! How can I help you?")
                    
                    if not user_input:
                        continue
                        
                    if "exit" in user_input or "quit" in user_input:
                        speak_response("Goodbye!")
                        break
                    
                    # Update chat history with user input
                    update_chat_history(username, "user", user_input)
                    
                    # Prepare messages with context
                    messages = prepare_messages(username, user_input)
                    
                    # Get and output response
                    response = get_response(llm, messages)
                    speak_response(response)
                    
                    # Update chat history with AI response
                    update_chat_history(username, "assistant", response)
                
    except KeyboardInterrupt:
        pass
    finally:
        print("\n" + "="*40)
        print(" Session ended ".center(40, '~'))
        print("="*40 + "\n")

if __name__ == "__main__":
    main()
