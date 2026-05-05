from services.voice_service import speech_to_text, text_to_speech
from services.llm_service import analyze_patient
from services.email_service import send_email
from utils.validation import is_valid_input


class TriageAgent:

    def process_audio(self, audio_path: str):
        result = {}

        # Step 1: Speech-to-Text
        text = speech_to_text(audio_path)
        result["transcription"] = text

        # Step 2: Validate input
        if not is_valid_input(text):
            result["error"] = "⚠️ Could not clearly understand your speech. Please try again."
            return result

        # Step 3: LLM + Guardrails
        llm_output = analyze_patient(text)
        result["triage"] = llm_output

        # Step 4: Email if severe
        if llm_output["severity"] == "Severe" and llm_output.get("summary"):
            email_status = send_email(llm_output["summary"])
            result["email_status"] = email_status

        # Step 5: Text-to-Speech
        audio_output = text_to_speech(llm_output["response"])
        result["audio_output"] = audio_output

        return result