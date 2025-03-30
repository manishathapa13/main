import streamlit as st
import openai
import os
from docx import Document
from PyPDF2 import PdfReader
from PIL import Image
import io

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Interview Coach", layout="wide")

st.markdown("""
    <style>
    .block-container {
        padding: 2rem 3rem;
    }
    .section-title {
        font-size: 24px;
        font-weight: 700;
        margin-top: 2rem;
    }
    textarea {
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI Interview Coach")

with st.sidebar:
    st.markdown("### 🛠️ How to Use")
    st.markdown("1. Upload or paste your **Resume**")
    st.markdown("2. Upload or paste the **Job Description**")
    st.markdown("3. Type an **Interview Question**")
    st.markdown("4. Click **Generate**")
    st.markdown("---")
    st.markdown("Built with ❤️ using GPT-4 + Streamlit")

# ---------- File parsing function ----------
def extract_text_from_file(uploaded_file):
    filetype = uploaded_file.type

    if filetype == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text

    elif filetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])

    elif "text" in filetype:
        return uploaded_file.read().decode("utf-8")

    elif "image" in filetype:
        return "[Image uploaded – content not readable as text]"

    else:
        return "[Unsupported file type]"

# ---------- Resume Section ----------
st.markdown("### 📄 Resume", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"])
with col2:
    resume_text = st.text_area("Or paste your resume here", height=200)

if resume_file:
    resume_text = extract_text_from_file(resume_file)

# ---------- Job Description Section ----------
st.markdown("### 📝 Job Description", unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    job_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"])
with col4:
    job_text = st.text_area("Or paste the job description here", height=200)

if job_file:
    job_text = extract_text_from_file(job_file)

# ---------- Interview Question ----------
st.markdown("### ❓ Interview Question")
question = st.text_input("Type your question (e.g. 'Tell me about yourself')")

# ---------- Generate Button ----------
if st.button("✨ Generate Response"):
    if not (resume_text and job_text and question):
        st.warning("⚠️ Please provide both resume, job description, and a question.")
    else:
        prompt = f"""
You are an AI interview coach.

Here is the candidate's resume:
{resume_text}

Here is the job description:
{job_text}

Interview question:
{question}

Evaluate how well the resume and answer align with the job description, and give actionable feedback. Then suggest an improved answer.
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert interview coach."},
                    {"role": "user", "content": prompt}
                ]
            )
            st.subheader("🎯 Suggested Answer")
            st.write(response.choices[0].message.content.strip())
        except Exception as e:
            st.error(f"⚠️ Unexpected Error: {str(e)}")
