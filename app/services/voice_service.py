import whisper
from gtts import gTTS

# Load Whisper model
model = whisper.load_model("medium")


def speech_to_text(audio_path: str):
    try:
        result = model.transcribe(
            audio_path,
            language="en",
            fp16=False,
            temperature=0.0,
            condition_on_previous_text=False  # 🔥 improves stability
        )

        text = result.get("text", "").strip()

        if text:
            text = text[0].upper() + text[1:]

        return text if text else "ASR Error: Empty transcription"

    except Exception as e:
        return f"ASR Error: {str(e)}"


def text_to_speech(text: str, output_path="response.mp3"):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(output_path)
        return output_path
    except Exception as e:
        return f"TTS Error: {str(e)}"