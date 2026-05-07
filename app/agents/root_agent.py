from services.voice_service import speech_to_text, text_to_speech
from services.llm_service import analyze_patient
from services.mcp_email import MCPEmailTool
from utils.validation import is_valid_input


class TriageAgent:

    def __init__(self):
        self.email_tool = MCPEmailTool()

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

        # 🚨 FIX: Handle LLM errors safely
        if not isinstance(llm_output, dict) or "error" in llm_output:
            result["error"] = "⚠️ Error analyzing symptoms. Please try again."
            return result

        result["triage"] = llm_output

        # Step 4: Email if severe (safe access)
        if llm_output.get("severity") == "Severe" and llm_output.get("summary"):
            email_status = self.email_tool.send(llm_output["summary"])
            result["email_status"] = email_status

        # Step 5: Text-to-Speech
        audio_output = text_to_speech(llm_output.get("response", ""))
        result["audio_output"] = audio_output

        return result