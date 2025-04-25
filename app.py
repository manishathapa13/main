import streamlit as st
import openai
import fitz  # PyMuPDF
import docx
from PIL import Image
import pytesseract
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, ClientSettings
import whisper
import numpy as np
import av
import tempfile
import os

# Config
st.set_page_config(page_title="AI Interview Coach", layout="wide")
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Styling
st.markdown("""
    <style>
    .stApp { background-color: #f9f9f9; font-family: 'Segoe UI', sans-serif; }
    h1 { text-align: center; color: #4CAF50; }
    </style>
""", unsafe_allow_html=True)

# Whisper Model
@st.cache_resource
def load_model():
    return whisper.load_model("base")

whisper_model = load_model()

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray().flatten().astype(np.float32)
        self.recorded_frames.append(pcm)
        return frame

    def get_audio_data(self):
        return np.concatenate(self.recorded_frames) if self.recorded_frames else None

# Sidebar
with st.sidebar:
    st.title("🛠️ How to Use")
    st.markdown("""
    1. Upload or paste your **Resume**  
    2. Upload or paste the **Job Description**  
    3. Type or record an **Interview Question**  
    4. Click **Generate**
    """)
    st.markdown("---")
    st.markdown("Built using GPT-4 + Streamlit")

    st.markdown("### 🎤 Record Your Question")
    ap = AudioProcessor()
    webrtc_ctx = webrtc_streamer(
        key="speech-input",
        mode="SENDRECV",
        client_settings=ClientSettings(
            media_stream_constraints={"audio": True, "video": False},
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        ),
        audio_processor_factory=lambda: ap,
        async_processing=True,
    )

    voice_transcript = ""
    if st.button("🗣️ Transcribe Audio"):
        if webrtc_ctx.state.playing:
            st.warning("Please stop recording before transcribing.")
        else:
            audio_data = ap.get_audio_data()
            if audio_data is not None:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    whisper.audio.save_audio(f.name, audio_data, sample_rate=16000)
                    result = whisper_model.transcribe(f.name)
                    voice_transcript = result["text"]
                    st.success("Transcription Complete!")
                    st.write(f"**Transcribed Text:** {voice_transcript}")
                os.remove(f.name)
            else:
                st.warning("No audio detected.")

# Title
st.markdown("<h1>🌟 AI Interview Coach</h1>", unsafe_allow_html=True)
st.markdown("Practice interview questions using your resume and a job description. Get instant feedback powered by GPT-4.")
st.markdown("---")

# Extract text function
def extract_text(file):
    name = file.name.lower()
    if name.endswith(".pdf"):
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in pdf])
    elif name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif name.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")
    elif name.endswith((".jpg", ".jpeg", ".png")):
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    return None

# Input: Resume
st.markdown("### 📄 Resume")
resume_col1, resume_col2 = st.columns([1, 1])
with resume_col1:
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"])
with resume_col2:
    resume_text = st.text_area("Or paste your resume here", height=200)

# Input: Job Description
st.markdown("### 📋 Job Description")
job_col1, job_col2 = st.columns([1, 1])
with job_col1:
    job_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"], key="job")
with job_col2:
    job_text = st.text_area("Or paste the job description here", height=200)

# Interview question
question = st.text_input("🖊️ Enter an interview question (e.g. 'Why should we hire you?')", value=voice_transcript or "")

show_common_questions = False

# Button
if st.button("✨ Generate Response"):
    resume_final = extract_text(resume_file) if resume_file else resume_text
    job_final = extract_text(job_file) if job_file else job_text

    if not resume_final or not job_final or not question:
        st.warning("🚫 Please provide resume, job description, and a question (via file or text).")
    else:
        prompt = f"""
You are an AI interview coach.

Resume:
{resume_final}

Job Description:
{job_final}

Interview Question:
{question}

Evaluate how well the resume and question align with the job, and suggest a professional, improved answer.
"""

        try:
            with st.spinner("Generating response... 🤖"):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert interview coach."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.success("✅ Response generated!")
                st.subheader("🎯 Suggested Answer")
                st.write(response.choices[0].message.content.strip())
                show_common_questions = True

        except Exception as e:
            st.error(f"⚠️ Unexpected Error: {str(e)}")

# Show common interview questions after generating a response
if show_common_questions:
    st.markdown("### 💬 Get Common Interview Questions")
    if st.button("📋 Show Common Interview Questions"):
        common_q_prompt = """
You are an expert career advisor. Provide a list of the top 10 most commonly asked job interview questions that apply to most industries and positions.
Please format your response clearly.
"""
        try:
            with st.spinner("Fetching top interview questions..."):
                response_common = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert HR advisor."},
                        {"role": "user", "content": common_q_prompt}
                    ]
                )
                st.success("✅ Here are some popular questions!")
                st.subheader("🔝 Top Interview Questions")
                st.write(response_common.choices[0].message.content.strip())
        except Exception as e:
            st.error(f"⚠️ Error fetching common questions: {str(e)}")

# Footer
st.markdown("<hr><p style='text-align: center; color: grey;'>© 2025 AI Interview Coach | Powered by OpenAI GPT-4 & Streamlit</p>", unsafe_allow_html=True)
