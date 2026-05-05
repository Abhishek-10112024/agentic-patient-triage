from agents.root_agent import TriageAgent


def run_cli():
    agent = TriageAgent()

    audio_path = input("Enter path to audio file: ")

    output = agent.process_audio(audio_path)

    print("\n--- TRIAGE OUTPUT ---\n")

    if "error" in output:
        print("Transcription:", output.get("transcription", ""))
        print("Error:", output["error"])
        return

    print("Transcription:", output["transcription"])

    triage = output["triage"]

    print("\nResponse:", triage["response"])
    print("Category:", triage["category"])
    print("Severity:", triage["severity"])

    if "email_status" in output:
        print("\nEmail Status:", output["email_status"])

    print("\nAudio File:", output["audio_output"])


if __name__ == "__main__":
    run_cli()