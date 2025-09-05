from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import uuid
import traceback

import speech_recognition as sr
from translate import Translator
from pydub import AudioSegment

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR , exist_ok= True)
os.makedirs(OUTPUT_DIR   , exist_ok =True)

def convert_to_wav( input_path: str, output_path :  str):
    audio =  AudioSegment.from_file(input_path)
    audio  =  audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    audio.export(output_path,  format="wav")

def speech_to_text_from_file( file_path : str) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path)   as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="en-US")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return ""

def translate_text(text: str, from_lang: str = "en" ,  to_lang: str = "persian") -> str:
    translator = Translator(from_lang=  from_lang, to_lang= to_lang)
    return translator.translate(text)

@app.post("/translate-speech/")
async def translate_speech(
    audio_file: UploadFile =  File(...)
):
    try:
        file_ext = audio_file.filename.split('.')[-1]
        temp_input_path = os.path.join(UPLOAD_DIR,  f"{uuid.uuid4()}.{file_ext}")
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file,  buffer)

        temp_wav_path =  os.path.join (UPLOAD_DIR, f"{uuid.uuid4()}.wav")
        convert_to_wav(temp_input_path, temp_wav_path)
        os.remove(temp_input_path)

        recognized_text  = speech_to_text_from_file( temp_wav_path)
        os.remove(temp_wav_path)
        #اگه تشخیص نتونه بده
        if not recognized_text:
            return JSONResponse(status_code=400, content={"error": "Could not recognize spaech from audio."})

        translated_text = translate_text(recognized_text)

        txt_filename = f"{uuid.uuid4()}.txt"
        txt_path = os.path.join(OUTPUT_DIR, txt_filename)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Original text:\n")
            f.write (recognized_text + "\n\n")
            f.write("Translated text:\n")
            f.write (translated_text)

        return {"text_file":   txt_filename}

    except Exception as e:
        return JSONResponse(status_code=500  , content={"error": str(e),  "trace": traceback.format_exc()})

@app.get("/download-text /{ filename}")
async def download_text(filename: str):
    file_path = os.path.join(OUTPUT_DIR,  filename)
    if os.path.exists(file_path ):
        return FileResponse( file_path,  media_type="text/plain", filename=filename)
    return JSONResponse(status_code=404, content={"error": "File not found."})
