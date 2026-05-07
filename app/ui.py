import streamlit as st
import os
import wave
import time

# Safe import (prevents crash if WebRTC breaks)
try:
    import av
    from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
    WEBRTC_AVAILABLE = True
except:
    WEBRTC_AVAILABLE = False

from agents.root_agent import TriageAgent
from utils.storage import save_recording, save_response

# -------------------------------
# 🎤 Audio Processor
# -------------------------------
if WEBRTC_AVAILABLE:
    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.frames = []

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            self.frames.append(frame)
            return frame

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

if WEBRTC_AVAILABLE:
    ctx = webrtc_streamer(
        key="audio",
        mode=WebRtcMode.SENDRECV,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if ctx.audio_processor:
        st.caption("🔴 Recording... Click STOP in the player above when done.")

        if st.button("💾 Save Recording"):
            frames = ctx.audio_processor.frames

            if frames:
                temp_audio = "live_recording.wav"

                with wave.open(temp_audio, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(48000)

                    for frame in frames:
                        wf.writeframes(frame.to_ndarray().tobytes())

                saved_path, idx = save_recording(temp_audio)

                st.session_state["live_audio"] = saved_path
                st.session_state["live_idx"] = idx

                st.success(f"Saved as recording_{idx}.wav")
                st.audio(saved_path)

    if "live_audio" in st.session_state:
        if st.button("🔍 Analyze Recording", use_container_width=True):

            progress = st.progress(0)
            status = st.empty()

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
                status.text("Analyzing audio...")

            output = agent.process_audio(st.session_state["live_audio"])

            status.empty()
            progress.empty()

            handle_output(output, st.session_state["live_idx"])

else:
    st.info("Live recording not supported. Please upload audio.")

st.divider()

# -------------------------------
# 📁 Upload Audio
# -------------------------------
st.subheader("📁 Upload Audio")

uploaded_file = st.file_uploader("Upload WAV file", type=["wav"])

if uploaded_file is not None:
    temp_audio = "uploaded.wav"

    with open(temp_audio, "wb") as f:
        f.write(uploaded_file.read())

    st.audio(temp_audio)

    st.session_state["upload_audio"] = temp_audio

if "upload_audio" in st.session_state:
    if st.button("🔍 Analyze Uploaded Audio", use_container_width=True):

        progress = st.progress(0)
        status = st.empty()

        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)
            status.text("Processing uploaded audio...")

        output = agent.process_audio(st.session_state["upload_audio"])

        status.empty()
        progress.empty()

        handle_output(output)