import pyttsx3
from translate import Translator
import speech_recognition as sr


def save_text_to_file(text: str, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def read_text_from_file(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def text_to_speech(text: str, rate: int = 125):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()


def translate_text(text: str, from_lang: str = 'en', to_lang: str = 'persian') -> str:
    translator = Translator(from_lang=from_lang, to_lang=to_lang)
    return translator.translate(text)


def speech_to_text() -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please Speech...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"your detected text: {text}")
        return text
    except sr.UnknownValueError:
        print( "Could not recognize spaech from audio")
        return ""
    except sr.RequestError as e:
        print(f"error in communication with servises  Google API: {e}")
        return ""


def main():
    choice = input("Choose one  (say/type): ").strip().lower()

    if choice == "say":
        user_input = speech_to_text()
        if not user_input:
            print("input not received,Stop your program")
            return
    else:
        user_input = input("Enter the text ")

    save_text_to_file(user_input, "note.txt")

    text = read_text_from_file("note.txt")
    print("main text", text)

    text_to_speech(text)

    translated = translate_text(text)
    print("translated text", translated)

    save_text_to_file(translated, "note2.txt")


if __name__ == "__main__":
    main()
