pip install vosk sounddevice pyttsx3

import os
import queue
import sounddevice as sd
import vosk
import pyttsx3
import json
import threading

# Vosk için model dosyası (Mac için güncellenmiş yol)
MODEL_PATH = "/Users/mertkose/Desktop/vosk-model-small-en-us-0.15"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Vosk modeli bulunamadı. Model yolunu kontrol edin.")

# Sesli yanıt için pyttsx3 motorunu başlat
engine = pyttsx3.init()
engine.setProperty('voice', 'english+m3')  # Erkek sesi seçimi

# Birden fazla sesli yanıtın çalıştırılmaması için kontrol
is_speaking = threading.Event()


def speak(text):
    def speak_thread():
        if not is_speaking.is_set():  # Eğer zaten sesli yanıt verilmemişse
            is_speaking.set()  # Sesli yanıtın başladığını işaretle
            engine.say(text)
            engine.runAndWait()  # Sesli yanıtı çalıştır
            is_speaking.clear()  # Sesli yanıt bittiğinde işareti temizle

    threading.Thread(target=speak_thread, daemon=True).start()  # Sesli yanıtı bir thread içinde çalıştır


# Vosk modelini yükle
model = vosk.Model(MODEL_PATH)
q = queue.Queue()


def callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    q.put(bytes(indata))


def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        recognizer = vosk.KaldiRecognizer(model, 16000)
        print("Jarvis dinliyor...")
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                print(f"Sen: {text}")
                if "hey jarvis" in text:
                    speak("Evet, seni dinliyorum.")
                    process_command()  # Komutları al


def process_command():
    print("Komutunuzu söyleyin...")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        recognizer = vosk.KaldiRecognizer(model, 16000)
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                command = result.get("text", "").lower()
                print(f"Komut: {command}")

                # Komutları işleme
                if "hava durumu" in command:
                    speak("Bugün hava güzel görünüyor.")
                elif "nasılsın" in command:
                    speak("Ben bir yapay zeka olduğum için hep iyiyim.")
                elif "görüşürüz" in command:
                    speak("Görüşmek üzere!")
                    break
                else:
                    speak("Bu komutu anlayamadım. Lütfen tekrar söyleyin.")


if __name__ == "__main__":
    while True:
        listen()  # "Hey Jarvis" komutunu bekler ve yalnızca bu komut alındığında aktif olur.
