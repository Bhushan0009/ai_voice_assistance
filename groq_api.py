import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq
import pyttsx3
import os

# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Initialize TTS engine
engine = pyttsx3.init()

# Initialize recognizer
recognizer = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio)
            print("You said:", query)
            return query
        except sr.UnknownValueError:
            print("Sorry, I could not understand.")
            return None
        except sr.RequestError:
            print("API unavailable.")
            return None

def ask_groq(prompt):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192"
    )
    return response.choices[0].message.content.strip()

def main():
    speak("Hi!, I'm your AI Voice Assistant. Say something to start.")
    while True:
        user_input = listen()
        if user_input:
            if user_input.lower() in ["exit", "quit", "stop"]:
                print("Goodbye!")
                speak("Goodbye!")
                break
            reply = ask_groq(user_input)
            print("Assistant:", reply)
            speak(reply)

if __name__ == "__main__":
    main()
