
import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

# ------------------------------
# Load the model
# ------------------------------
model_path = r"Q:\Code\aranea_code\voice"
model = Model(model_path)

# ------------------------------
# No grammar – full transcription
# ------------------------------
recognizer = KaldiRecognizer(model, 16000)  # No grammar passed here
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print("⚠️ Audio:", status)
    q.put(bytes(indata))

# ------------------------------
# Listen and print transcriptions
# ------------------------------
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
    print("🎧 Free speech mode: say anything (Ctrl+C to stop)")
    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                print(f"📝 Heard: {text}")
