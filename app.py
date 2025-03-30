import streamlit as st
import openai
import fitz  # PyMuPDF
import docx
from PIL import Image
import pytesseract
from streamlit_speech_recognition import speech_to_text

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Interview Coach", layout="wide")
st.markdown("""
    <style>
        .big-font {
            font-size:20px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💼 AI Interview Coach")
st.markdown("**Practice interview questions using your resume and job description. Get feedback powered by GPT-4.**")

# Sidebar Instructions
with st.sidebar:
    st.header("🛠️ How to Use")
    st.markdown("1. Upload, paste, or speak your **Resume**")
    st.markdown("2. Upload, paste, or speak the **Job Description**")
    st.markdown("3. Type or speak an **Interview Question**")
    st.markdown("4. Click **Generate**")
    st.markdown("\nBuilt with ❤️ using GPT-4 + Streamlit")

# === File and Text Handling Functions ===
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)

def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        file_type = uploaded_file.type
        if "pdf" in file_type:
            return extract_text_from_pdf(uploaded_file)
        elif "msword" in file_type or "officedocument.wordprocessingml" in file_type:
            return extract_text_from_docx(uploaded_file)
        elif "image" in file_type:
            return extract_text_from_image(uploaded_file)
        elif "text" in file_type:
            return uploaded_file.read().decode("utf-8")
        else:
            return "❌ Unsupported file type."
    return ""

# === Resume Section ===
st.subheader("📄 Resume")
col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"])
with col2:
    resume_text = st.text_area("Or paste your resume here", height=200)

st.markdown("🎙️ Or speak your resume")
resume_voice = speech_to_text()
if resume_voice:
    resume_text += "\n" + resume_voice

resume = resume_text or handle_file_upload(resume_file)

# === Job Description Section ===
st.subheader("📝 Job Description")
col3, col4 = st.columns(2)
with col3:
    jd_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"])
with col4:
    jd_text = st.text_area("Or paste the job description here", height=200)

st.markdown("🎙️ Or speak the job description")
jd_voice = speech_to_text()
if jd_voice:
    jd_text += "\n" + jd_voice

job_desc = jd_text or handle_file_upload(jd_file)

# === Interview Question ===
st.subheader("❓ Interview Question")
question = st.text_input("Type your question (e.g. 'Tell me about yourself')")

st.markdown("🎙️ Or speak your question")
question_voice = speech_to_text()
if question_voice:
    question += " " + question_voice

# === Generate Interview Questions ===
if st.button("💡 Generate Interview Questions"):
    if not (resume and job_desc):
        st.warning("Please provide both resume and job description.")
    else:
        prompt_qs = f"""
You are an expert HR specialist. Based on the following resume and job description,
generate a list of 5 relevant behavioral or technical interview questions.

Resume:
{resume}

Job Description:
{job_desc}
"""
        try:
            response_qs = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert HR interview coach."},
                    {"role": "user", "content": prompt_qs}
                ]
            )
            st.subheader("🧠 General Interview Questions")
            st.write(response_qs.choices[0].message.content.strip())
        except Exception as e:
            st.error(f"⚠️ Error generating questions: {str(e)}")

# === Generate Answer ===
if st.button("✨ Generate Response"):
    if not (resume and job_desc and question):
        st.warning("Please fill in all fields.")
    else:
        prompt = f"""
You are an AI interview coach.

Here is the candidate's resume:
{resume}

Here is the job description:
{job_desc}

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
