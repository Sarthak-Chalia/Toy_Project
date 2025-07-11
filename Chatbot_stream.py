import os
import speech_recognition as sr
import pyttsx3
from langchain_together import ChatTogether
from langchain.schema import HumanMessage

# Configuration
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY_HERE"
MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
TEMPERATURE = 0.7

# Initialize text-to-speech engine
def init_tts():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    # Change voice (0 = male, 1 = female)
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
    return engine

def initialize_model():
    return ChatTogether(model=MODEL, temperature=TEMPERATURE)

def get_response(llm, prompt):
    return llm.invoke([HumanMessage(content=prompt)]).content

def listen_for_activation(recognizer):
    print("\n🔇 System is sleeping. Say 'switch' to activate...")
    with sr.Microphone() as mic:
        while True:
            try:
                recognizer.adjust_for_ambient_noise(mic, duration=0.5)
                audio = recognizer.listen(mic, timeout=None, phrase_time_limit=3)
                text = recognizer.recognize_google(audio).lower()
                
                if "switch" in text:
                    print("\n🎤 Voice activated! Speak your query...")
                    return True
                
            except sr.UnknownValueError:
                continue
            except sr.WaitTimeoutError:
                continue
            except sr.RequestError as e:
                print(f"Error with speech service: {e}")
                continue

def get_voice_input(recognizer):
    with sr.Microphone() as mic:
        try:
            recognizer.adjust_for_ambient_noise(mic, duration=0.5)
            audio = recognizer.listen(mic, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Couldn't understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Speech service error: {e}")
            return ""

def speak_response(engine, text):
    print(f"Xae: {text}\n")
    engine.say(text)
    engine.runAndWait()

def main():
    llm = initialize_model()
    tts_engine = init_tts()
    recognizer = sr.Recognizer()
    
    print("\n" + "="*40)
    print(" Voice-Activated Xae Chatbot 🤖✨ ".center(40, '~'))
    print("="*40)
    print("\nSystem is in sleep mode. Say 'switch' to activate microphone.\n")
    
    try:
        while True:
            # Wait for activation word
            if listen_for_activation(recognizer):
                # Get voice input after activation
                user_input = get_voice_input(recognizer)
                
                if not user_input:
                    continue
                    
                if "switch" in user_input:
                    print("\n🔇 Returning to sleep mode...")
                    tts_engine.say("Returning to sleep mode")
                    tts_engine.runAndWait()
                    continue
                    
                if "exit" in user_input or "quit" in user_input:
                    tts_engine.say("Goodbye!")
                    tts_engine.runAndWait()
                    break
                
                # Get and output response
                response = get_response(llm, user_input)
                speak_response(tts_engine, response)
                
    except KeyboardInterrupt:
        pass
    finally:
        print("\n" + "="*40)
        print(" Session ended ".center(40, '~'))
        print("="*40 + "\n")

if __name__ == "__main__":
    main()
