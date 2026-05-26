import streamlit as st
import hashlib
import tempfile
import time

from agents.root_agent import TriageAgent
from utils.storage import save_recording, save_response

# -------------------------------
# 🚀 Initialize
# -------------------------------
agent = TriageAgent()

st.set_page_config(page_title="AI Patient Triage", layout="centered")

# -------------------------------
# 🎨 Header
# -------------------------------
st.markdown(
    """
    <h1 style='text-align: center;'>🩺 AI Patient Triage System</h1>
    <p style='text-align: center;'>Speak or upload your symptoms. The AI will guide you.</p>
    """,
    unsafe_allow_html=True
)

st.warning("⚠️ Speak clearly in a quiet environment for best results.")

st.divider()

# -------------------------------
# 🎧 Audio Helpers
# -------------------------------
def write_temp_audio(audio_file, suffix=".wav"):
    audio_file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_file.read())
        return tmp.name


def analyze_audio(audio_path, status_text):
    progress = st.progress(0)
    status = st.empty()

    for i in range(100):
        time.sleep(0.01)
        progress.progress(i + 1)
        status.text(status_text)

    output = agent.process_audio(audio_path)

    status.empty()
    progress.empty()

    return output


# -------------------------------
# 🧠 Output Handler
# -------------------------------
def handle_output(output, idx=None):
    st.divider()

    if "error" in output:
        st.subheader("📝 Transcribed Text")
        st.write(output.get("transcription", ""))

        st.error(
            "⚠️ Could not clearly understand your speech.\n\n"
            "👉 Please speak clearly.\n"
            "👉 Mention symptoms like fever, cough, pain."
        )
        return

    st.success("✅ Analysis Complete")

    st.subheader("📝 Transcribed Text")
    st.write(output["transcription"])

    triage = output["triage"]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Category", triage.get("category"))
    with col2:
        st.metric("Severity", triage.get("severity"))

    st.subheader("🤖 AI Response")
    st.write(triage.get("response"))

    if triage.get("summary"):
        st.subheader("📄 Case Summary")
        st.json(triage["summary"])

    if "email_status" in output:
        st.success(f"📧 {output['email_status']}")

    st.subheader("🔊 Voice Response")
    st.audio(output.get("audio_output"))

    # Save response only for live recordings
    if idx:
        save_response(output, idx)

# -------------------------------
# 🎤 Live Recording
# -------------------------------
st.subheader("🎤 Live Recording")

if hasattr(st, "audio_input"):
    live_audio = st.audio_input("Record symptoms from your microphone")

    if live_audio is not None:
        live_bytes = live_audio.getvalue()
        live_hash = hashlib.sha256(live_bytes).hexdigest()

        if st.session_state.get("live_audio_hash") != live_hash:
            st.session_state["live_audio_hash"] = live_hash
            st.session_state.pop("live_audio", None)
            st.session_state.pop("live_idx", None)

        st.audio(live_bytes, format="audio/wav")

        if st.button("🔍 Analyze Live Recording", use_container_width=True):
            temp_audio = write_temp_audio(live_audio)
            saved_path, idx = save_recording(temp_audio)

            st.session_state["live_audio"] = saved_path
            st.session_state["live_idx"] = idx

            output = analyze_audio(saved_path, "Analyzing live recording...")
            handle_output(output, idx)

        if "live_audio" in st.session_state:
            st.caption(f"Saved as recording_{st.session_state['live_idx']}.wav")
else:
    st.info("Live recording requires Streamlit 1.40 or newer. Please upload audio.")

st.divider()

# -------------------------------
# 📁 Upload Audio
# -------------------------------
st.subheader("📁 Upload Audio")

uploaded_file = st.file_uploader("Upload WAV file", type=["wav"])

if uploaded_file is not None:
    temp_audio = write_temp_audio(uploaded_file)

    st.audio(temp_audio)

    st.session_state["upload_audio"] = temp_audio

if "upload_audio" in st.session_state:
    if st.button("🔍 Analyze Uploaded Audio", use_container_width=True):
        output = analyze_audio(
            st.session_state["upload_audio"],
            "Processing uploaded audio..."
        )
        handle_output(output)
