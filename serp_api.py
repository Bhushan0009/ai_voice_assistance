from transformers import pipeline
import speech_recognition as sr
from dotenv import load_dotenv
import pyttsx3
import serpapi
import time
import os

# Load environment variables
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Initialize Hugging Face summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 0.9)

# Initialize speech recognizer
recognizer = sr.Recognizer()

def speak(text):
    """Convert text to speech."""
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    """Listen for voice input and convert to text."""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=5)
        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, there was an issue with the speech recognition service.")
            return None

def search_web(query):
    """Perform a web search using SerpAPI."""
    try:
        client = serpapi.Client(api_key=SERPAPI_KEY)
        results = client.search(q=query, num=5)
        organic_results = results.get("organic_results", [])
        snippets = [result.get("snippet", "") for result in organic_results if "snippet" in result]
        print("Search snippets:", snippets)  # Debug
        return snippets
    except Exception as e:
        print(f"Search error: {e}")
        return []

def summarize_with_huggingface(query, search_results):
    """Summarize search results using Hugging Face BART model."""
    if not search_results:
        return "No results found for your query."
    
    # Combine snippets into a single text (BART has a max input length)
    input_text = " ".join(search_results)
    input_length = len(input_text.split())
    
    # Ensure input is within model limits (BART handles ~1024 tokens)
    if input_length > 1000:
        input_text = " ".join(input_text.split()[:1000])
    
    try:
        # Summarize with BART (set max/min length for concise output)
        summary = summarizer(
            input_text,
            max_length=100,  # Max summary length
            min_length=30,   # Min summary length
            do_sample=False
        )[0]["summary_text"]
        return summary
    except Exception as e:
        print(f"Summarization error: {e}")
        return "Sorry, I couldn't summarize the results."

def main():
    speak("Hello! I'm Stsarc, your AI voice assistant. Say 'search' followed by your query to begin.")
    
    while True:
        query = listen()
        if query:
            if query.startswith("search"):
                search_query = query.replace("search", "").strip()
                if search_query:
                    speak(f"Searching for {search_query}")
                    search_results = search_web(search_query)
                    summary = summarize_with_huggingface(search_query, search_results)
                    print(f"Summary: {summary}")
                    speak(summary)
                else:
                    speak("Please provide a search query.")
            elif query == "exit":
                speak("Goodbye!")
                break
            else:
                speak("Please say 'search' followed by your query, or 'exit' to quit.")
        time.sleep(1)  # Avoid rapid processing

if __name__ == "__main__":
    main()
