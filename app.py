"""
MedScribe — doctor–patient conversation recorder
Login, audio recording, transcription, medical report, WhatsApp share.
"""

import streamlit as st
from textblob import TextBlob
from datetime import datetime
import json
import os
import tempfile
import urllib.parse

from medical_utils import summarize_text, generate_medical_report, suggest_diseases, generate_report_pdf

# Data file for persistence
DATA_FILE = "conversations.json"

# Demo credentials (change in production)
VALID_USERS = {"doctor": "doctor123", "admin": "admin123"}

# UI Settings
st.set_page_config(
    page_title="MedScribe",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Responsive layout and visual polish (matches static landing aesthetic)
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 1120px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: clamp(0.75rem, 3vw, 1.75rem) !important;
        padding-right: clamp(0.75rem, 3vw, 1.75rem) !important;
        padding-top: clamp(0.75rem, 2vw, 1.5rem) !important;
        padding-bottom: 2rem !important;
    }
    @media (max-width: 768px) {
        [data-testid="stSidebar"] { box-shadow: 8px 0 32px rgba(0,0,0,0.35); }
    }
    h1 { font-size: clamp(1.35rem, 4vw, 1.85rem) !important; letter-spacing: -0.02em; font-weight: 700 !important; }
    h2, h3 { letter-spacing: -0.01em; }
    div[data-testid="stExpander"] details {
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        background: rgba(30, 41, 59, 0.35);
    }
    .stDownloadButton > button,
    button[kind="primary"] {
        border-radius: 10px;
        font-weight: 600;
    }
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="input"] input {
        border-radius: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if "conversations" not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                st.session_state.conversations = json.load(f)
        except (json.JSONDecodeError, IOError):
            st.session_state.conversations = []
    else:
        st.session_state.conversations = []

if "report_text" not in st.session_state:
    st.session_state.report_text = ""
for k, default in (("patient_name", ""), ("patient_age", ""), ("patient_bp", "")):
    if k not in st.session_state:
        st.session_state[k] = default


# ============ LOGIN PAGE ============
if not st.session_state.logged_in:
    st.title("🏥 MedScribe")
    st.markdown("Please log in to continue.")
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="e.g. doctor")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username and password and VALID_USERS.get(username) == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password. Try: doctor / doctor123")
    st.caption("Demo: doctor / doctor123")
    st.stop()


def save_conversations():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(st.session_state.conversations, f, indent=2)
    except IOError as e:
        st.error(f"Could not save: {e}")


def add_message(speaker: str, text: str):
    if not text.strip():
        return False
    entry = {
        "id": len(st.session_state.conversations) + 1,
        "speaker": speaker,
        "text": text.strip(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.conversations.append(entry)
    save_conversations()
    return True


def transcribe_audio(audio_bytes, format="wav"):
    """Transcribe audio bytes to text using SpeechRecognition."""
    try:
        import speech_recognition as sr
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="en-US")
        except sr.UnknownValueError:
            text = ""
        except sr.RequestError:
            text = "[Transcription unavailable - check internet connection]"
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        return text
    except Exception as e:
        return f"[Transcription error: {str(e)}]"


def analyze_sentiment(text: str):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "Positive", polarity, "😊"
    elif polarity < 0:
        return "Negative", polarity, "😟"
    return "Neutral", polarity, "😐"


# Sidebar
st.sidebar.title("🏥 MedScribe")
st.sidebar.markdown(f"Logged in as **{st.session_state.username}**")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["🎙️ Record Conversation", "📝 Add Manually", "📊 Dashboard & Report", "🗑️ Clear All"]
)
st.sidebar.markdown("---")
st.sidebar.info(f"**Total messages:** {len(st.session_state.conversations)}")


# ============ RECORD CONVERSATION (Audio) ============
if page == "🎙️ Record Conversation":
    st.title("🎙️ Record conversation")
    st.markdown("Record voice from your microphone. Click the mic, speak, then stop. The recording will be transcribed.")

    # Record button using st.audio_input (Streamlit 1.48+)
    try:
        audio_data = st.audio_input("🎤 Click to start recording", key="audio_rec")
    except AttributeError:
        st.error("Audio recording requires Streamlit 1.48+. Run: pip install streamlit>=1.48")
        st.info("Use **Add Manually** to type the conversation instead.")
        audio_data = None

    if audio_data:
        st.audio(audio_data)
        if st.button("Transcribe & Add to Conversation"):
            with st.spinner("Transcribing..."):
                audio_bytes = audio_data.read()
                transcript = transcribe_audio(audio_bytes)
            if transcript:
                # Ask who spoke
                speaker = st.radio("Who was speaking?", ["Doctor", "Patient"])
                if add_message(speaker, transcript):
                    st.success("Recording added!")
                    st.write("**Transcript:**", transcript)
                    st.rerun()
            else:
                st.warning("No speech detected. Try recording again.")

    st.markdown("---")
    st.subheader("📜 Recent Conversation")
    if st.session_state.conversations:
        for msg in reversed(st.session_state.conversations[-10:]):
            icon = "👨‍⚕️" if msg["speaker"] == "Doctor" else "🩺"
            st.markdown(f"**{icon} {msg['speaker']}** ({msg['timestamp']})")
            st.markdown(f"> {msg['text']}")
    else:
        st.info("No messages yet. Record or add manually.")


# ============ ADD MANUALLY ============
elif page == "📝 Add Manually":
    st.title("📝 Add Conversation Manually")
    col1, col2 = st.columns(2)
    with col1:
        doctor_text = st.text_area("👨‍⚕️ Doctor's message", key="doc", height=100)
        if st.button("Add Doctor Message", key="add_doc"):
            if add_message("Doctor", doctor_text):
                st.success("Added!")
                st.rerun()
    with col2:
        patient_text = st.text_area("🩺 Patient's message", key="pat", height=100)
        if st.button("Add Patient Message", key="add_pat"):
            if add_message("Patient", patient_text):
                st.success("Added!")
                st.rerun()


# ============ DASHBOARD & REPORT ============
elif page == "📊 Dashboard & Report":
    st.title("📊 Dashboard & Medical Report")

    if not st.session_state.conversations:
        st.warning("No conversations yet. Record or add messages first.")
    else:
        doctor_count = sum(1 for m in st.session_state.conversations if m["speaker"] == "Doctor")
        patient_count = sum(1 for m in st.session_state.conversations if m["speaker"] == "Patient")

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Messages", len(st.session_state.conversations))
        m2.metric("Doctor", doctor_count)
        m3.metric("Patient", patient_count)

        st.markdown("---")
        st.subheader("📋 Full Conversation")
        for msg in st.session_state.conversations:
            icon = "👨‍⚕️" if msg["speaker"] == "Doctor" else "🩺"
            with st.expander(f"{icon} {msg['speaker']} — {msg['timestamp']}"):
                st.write(msg["text"])

        st.markdown("---")
        st.subheader("👤 Patient details")
        st.caption("Enter before generating; you can update anytime. Name, age, and BP appear on the report.")
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            st.text_input("Patient name", key="patient_name", placeholder="e.g. Jane Doe")
        with pc2:
            st.text_input("Age", key="patient_age", placeholder="e.g. 42")
        with pc3:
            st.text_input("Blood pressure (BP)", key="patient_bp", placeholder="e.g. 122/78 mmHg")

        st.markdown("---")
        st.subheader("📄 Medical report")
        if st.button("Generate draft report (summary, conditions, suggestions)"):
            all_text = " ".join(m["text"] for m in st.session_state.conversations)
            suggested = suggest_diseases(all_text)
            report = generate_medical_report(
                all_text,
                suggested,
                patient_name=st.session_state.get("patient_name", ""),
                patient_age=st.session_state.get("patient_age", ""),
                patient_bp=st.session_state.get("patient_bp", ""),
            )
            st.session_state.report_text = report
            st.rerun()

        st.text_area(
            "Edit report — change text, add prescribed drugs (dose, frequency), or clinical notes",
            key="report_text",
            height=420,
            placeholder="Click 'Generate draft report' above, or type your report here…",
        )

        if st.session_state.get("report_text", "").strip():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📥 Download PDF")
                pdf_bytes = bytes(generate_report_pdf(st.session_state.report_text))
                safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in st.session_state.get("patient_name", "patient"))[:40] or "patient"
                st.download_button(
                    label="Download Medical Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"medical_report_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
            with col2:
                st.markdown("### 📱 Send to WhatsApp")
                report_encoded = urllib.parse.quote(st.session_state.report_text)
                whatsapp_url = f"https://wa.me/?text={report_encoded}"
                st.link_button("Open WhatsApp to Share Report", whatsapp_url)
            st.caption("PDF and WhatsApp use the report text in the box above (including your edits).")


# ============ CLEAR ALL ============
elif page == "🗑️ Clear All":
    st.title("🗑️ Clear All Data")
    st.warning("This will permanently delete all conversations.")
    if st.button("Clear All"):
        st.session_state.conversations = []
        st.session_state.report_text = ""
        for k in ("patient_name", "patient_age", "patient_bp"):
            st.session_state[k] = ""
        save_conversations()
        st.success("Cleared.")
        st.rerun()
