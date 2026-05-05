import streamlit as st
import os
from agents.root_agent import TriageAgent

# Initialize agent
agent = TriageAgent()

st.set_page_config(page_title="AI Patient Triage", layout="centered")

st.title("🩺 AI Patient Triage System")
st.write("Speak or upload your symptoms. The AI will guide you.")

# Upload audio
audio_file = st.file_uploader("Upload your voice (WAV format)", type=["wav"])

if audio_file is not None:
    temp_path = "temp.wav"

    # Save file temporarily
    with open(temp_path, "wb") as f:
        f.write(audio_file.read())

    st.audio(temp_path)

    if st.button("Analyze"):

        # 🔁 Call Root Agent
        output = agent.process_audio(temp_path)

        # ❌ Handle invalid input
        if "error" in output:
            st.subheader("📝 Transcribed Text")
            st.write(output.get("transcription", ""))

            st.error(output["error"])
            st.stop()

        # ✅ Show transcription
        st.subheader("📝 Transcribed Text")
        st.write(output["transcription"])

        triage = output["triage"]

        # 🤖 AI Response
        st.subheader("🤖 AI Response")
        st.write(triage["response"])

        # 📊 Classification
        st.subheader("📊 Classification")
        st.write(f"Category: {triage['category']}")
        st.write(f"Severity: {triage['severity']}")

        # 📧 Email (if severe)
        if "email_status" in output:
            st.subheader("📧 Doctor Notification")
            st.write(output["email_status"])

        # 🔊 Audio response
        st.subheader("🔊 Voice Response")
        st.audio(output["audio_output"])

        # 🧹 Optional cleanup (good practice)
        if os.path.exists(temp_path):
            os.remove(temp_path)