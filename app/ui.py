import streamlit as st
import hashlib
import tempfile
import html
import os
import sys
import time
import wave
from pathlib import Path

from agents.root_agent import TriageAgent
from utils.storage import save_recording, save_response

# -------------------------------
# 🚀 Initialize
# -------------------------------
agent = TriageAgent()
import streamlit as st

# Safe import: the app still supports upload-only mode if WebRTC is unavailable.
try:
    import av
    from streamlit_webrtc import AudioProcessorBase, WebRtcMode, webrtc_streamer

    WEBRTC_AVAILABLE = True
except Exception:
    WEBRTC_AVAILABLE = False

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from agents.root_agent import TriageAgent
from utils.storage import save_recording, save_response


SUPPORTED_AUDIO_TYPES = ["wav", "mp3", "m4a", "mp4", "mpeg", "mpga", "webm", "ogg", "flac", "aac"]


st.set_page_config(
    page_title="AI Patient Triage",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        :root {
            --surface: #ffffff;
            --muted-surface: #f6f8fb;
            --border: #d9e1ea;
            --ink: #132238;
            --muted: #5f6d7a;
            --accent: #0f766e;
            --accent-weak: #e6f5f3;
            --warn: #b45309;
            --warn-weak: #fff7ed;
            --danger: #b42318;
            --danger-weak: #fef3f2;
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            letter-spacing: 0;
        }

        .app-hero {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.35rem 1.5rem;
            background: linear-gradient(135deg, #ffffff 0%, #eef8f6 58%, #f7fbff 100%);
        }

        .app-hero h1 {
            color: var(--ink);
            font-size: clamp(2rem, 3vw, 3rem);
            line-height: 1.05;
            margin: 0 0 .55rem 0;
        }

        .app-hero p {
            color: var(--muted);
            font-size: 1rem;
            margin: 0;
            max-width: 760px;
        }

        .status-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .75rem;
            margin: 1rem 0 1.25rem 0;
        }

        .status-item,
        .result-card,
        .summary-card {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            padding: 1rem;
        }

        .status-label,
        .card-label {
            color: var(--muted);
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .04em;
            text-transform: uppercase;
            margin-bottom: .35rem;
        }

        .status-value,
        .card-value {
            color: var(--ink);
            font-size: 1.05rem;
            font-weight: 700;
            line-height: 1.25;
        }

        .result-card {
            min-height: 118px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            font-size: .76rem;
            font-weight: 800;
            line-height: 1;
            padding: .42rem .62rem;
            text-transform: uppercase;
        }

        .badge-mild {
            background: var(--accent-weak);
            color: var(--accent);
        }

        .badge-severe {
            background: var(--danger-weak);
            color: var(--danger);
        }

        .badge-neutral {
            background: #eef2f7;
            color: #334155;
        }

        .transcript-box,
        .response-box {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--muted-surface);
            color: var(--ink);
            padding: 1rem;
            line-height: 1.55;
        }

        .response-box {
            background: #f8fbfa;
            border-color: #cfe7e2;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .75rem;
        }

        .summary-card div:last-child {
            color: var(--ink);
            line-height: 1.45;
        }

        div[data-testid="stTabs"] button {
            font-weight: 700;
        }

        div[data-testid="stFileUploader"] section {
            border-radius: 8px;
        }

        @media (max-width: 760px) {
            .status-strip,
            .summary-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


if WEBRTC_AVAILABLE:

    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.frames = []

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            self.frames.append(frame)
            return frame

@st.cache_resource
def get_agent():
    return TriageAgent()


agent = get_agent()


def safe_text(value, fallback="Not available"):
    if value is None or value == "":
        return fallback
    return html.escape(str(value))


def severity_badge(severity):
    normalized = (severity or "").strip().lower()
    if normalized == "mild":
        badge_class = "badge-mild"
    elif normalized == "severe":
        badge_class = "badge-severe"
    else:
        badge_class = "badge-neutral"

    return f"<span class='badge {badge_class}'>{safe_text(severity)}</span>"


def render_status_strip():
    live_state = "Available" if WEBRTC_AVAILABLE else "Upload only"
    env_state = "Configured" if os.getenv("GROQ_API_KEY") else "Needs API key"

    st.markdown(
        f"""
        <div class="status-strip">
            <div class="status-item">
                <div class="status-label">Input</div>
                <div class="status-value">{live_state}</div>
            </div>
            <div class="status-item">
                <div class="status-label">Model access</div>
                <div class="status-value">{env_state}</div>
            </div>
            <div class="status-item">
                <div class="status-label">Escalation</div>
                <div class="status-value">Email alerts for severe cases</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress(label):
    progress = st.progress(0)
    status = st.empty()

    for value in range(100):
        time.sleep(0.01)
        progress.progress(value + 1)
        status.caption(label)

    status.empty()
    progress.empty()


def render_summary(summary):
    if not summary:
        return

    if hasattr(summary, "dict"):
        summary = summary.dict()

    fields = [
        ("Symptoms", summary.get("symptoms")),
        ("Duration", summary.get("duration")),
        ("Severity reason", summary.get("severity_reason")),
        ("Recommendation", summary.get("recommendation")),
    ]

    cards = "".join(
        f"""
        <div class="summary-card">
            <div class="card-label">{safe_text(label)}</div>
            <div>{safe_text(value)}</div>
        </div>
        """
        for label, value in fields
    )

    st.markdown(f"<div class='summary-grid'>{cards}</div>", unsafe_allow_html=True)


def render_audio_response(audio_path):
    if not audio_path:
        return

    if isinstance(audio_path, str) and audio_path.startswith("TTS Error"):
        st.warning(audio_path)
        return

    if isinstance(audio_path, str) and os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.info("Voice response is not available for this result.")


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
    st.markdown("### Analysis result")

    transcription = output.get("transcription", "")

    if "error" in output:
        st.markdown(
            f"<div class='transcript-box'>{safe_text(transcription)}</div>",
            unsafe_allow_html=True,
        )
        st.error(
            "The audio could not be interpreted clearly enough for triage. "
            "Record again in a quieter place or upload a clearer WAV file."
        )
        return

    triage = output["triage"]
    category = triage.get("category")
    severity = triage.get("severity")
    response = triage.get("response")

    result_cols = st.columns([1.2, 1, 1])
    with result_cols[0]:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="card-label">Category</div>
                <div class="card-value">{safe_text(category)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with result_cols[1]:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="card-label">Severity</div>
                <div class="card-value">{severity_badge(severity)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with result_cols[2]:
        routing = "Doctor escalation" if severity == "Severe" else "Home guidance"
        st.markdown(
            f"""
            <div class="result-card">
                <div class="card-label">Routing</div>
                <div class="card-value">{routing}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Transcript")
    st.markdown(
        f"<div class='transcript-box'>{safe_text(transcription)}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Patient guidance")
    st.markdown(
        f"<div class='response-box'>{safe_text(response)}</div>",
        unsafe_allow_html=True,
    )

    if triage.get("summary"):
        st.markdown("#### Doctor summary")
        render_summary(triage["summary"])

    if "email_status" in output:
        st.success(output["email_status"])

    with st.expander("Voice response", expanded=False):
        render_audio_response(output.get("audio_output"))

    if idx:
        save_response(output, idx)


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
st.markdown(
    """
    <section class="app-hero">
        <h1>AI Patient Triage</h1>
        <p>Capture or upload a patient symptom report, then review the transcript, triage category, severity, guidance, and escalation status in one place.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

render_status_strip()

with st.sidebar:
    st.header("Session")
    st.caption("Use this tool for early triage support. Severe symptoms should be escalated to a clinician.")
    st.divider()
    st.caption("Environment")
    st.write("GROQ_API_KEY:", "Set" if os.getenv("GROQ_API_KEY") else "Missing")
    st.write("Live recording:", "Available" if WEBRTC_AVAILABLE else "Unavailable")


record_tab, upload_tab = st.tabs(["Record audio", "Upload WAV"])

with record_tab:
    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.subheader("Live recording")

        if WEBRTC_AVAILABLE:
            ctx = webrtc_streamer(
                key="audio",
                mode=WebRtcMode.SENDRECV,
                audio_processor_factory=AudioProcessor,
                media_stream_constraints={"audio": True, "video": False},
            )

            if ctx.audio_processor:
                st.caption("Recording is active while the WebRTC control is running.")

                if st.button("Save recording", use_container_width=True):
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
                    else:
                        st.warning("No audio frames were captured yet.")
        else:
            st.info("Live recording is not available in this environment. Use the upload tab.")

    with right:
        st.subheader("Current recording")

        if "live_audio" in st.session_state:
            st.audio(st.session_state["live_audio"])

            if st.button("Analyze recording", type="primary", use_container_width=True):
                render_progress("Analyzing recording...")
                output = agent.process_audio(st.session_state["live_audio"])
                handle_output(output, st.session_state["live_idx"])
        else:
            st.info("Save a recording to analyze it here.")

if uploaded_file is not None:
    temp_audio = write_temp_audio(uploaded_file)
with upload_tab:
    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.subheader("Upload audio")
        st.caption("Supported formats: WAV, MP3, M4A, MP4, MPEG, WEBM, OGG, FLAC, AAC")
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=SUPPORTED_AUDIO_TYPES,
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            suffix = Path(uploaded_file.name).suffix.lower()
            if suffix not in {f".{file_type}" for file_type in SUPPORTED_AUDIO_TYPES}:
                suffix = ".audio"

            temp_audio = f"uploaded{suffix}"

if "upload_audio" in st.session_state:
    if st.button("🔍 Analyze Uploaded Audio", use_container_width=True):
        output = analyze_audio(
            st.session_state["upload_audio"],
            "Processing uploaded audio..."
        )
        handle_output(output)
            with open(temp_audio, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.session_state["upload_audio"] = temp_audio
            st.session_state["upload_name"] = uploaded_file.name
            st.success(f"Loaded {uploaded_file.name}")

    with right:
        st.subheader("Selected file")

        if "upload_audio" in st.session_state:
            st.caption(st.session_state.get("upload_name", "uploaded.wav"))
            st.audio(st.session_state["upload_audio"])

            if st.button("Analyze uploaded audio", type="primary", use_container_width=True):
                render_progress("Processing uploaded audio...")
                output = agent.process_audio(st.session_state["upload_audio"])
                handle_output(output)
        else:
            st.info("Upload an audio file to begin.")
