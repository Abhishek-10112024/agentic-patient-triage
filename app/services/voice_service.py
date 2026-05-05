import whisper
from gtts import gTTS
import os

# Load Whisper model (first time will download)
model = whisper.load_model("base")


def speech_to_text(audio_path: str):
    try:
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        return f"ASR Error: {str(e)}"


def text_to_speech(text: str, output_path="response.mp3"):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(output_path)
        return output_path
    except Exception as e:
        return f"TTS Error: {str(e)}"