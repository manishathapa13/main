import streamlit as st
import openai
import fitz  # PyMuPDF
import docx
from PIL import Image
import pytesseract

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

# Sidebar
with st.sidebar:
    st.title("🛠️ How to Use")
    st.markdown("""
    1. Upload or paste your **Resume**  
    2. Upload or paste the **Job Description**  
    3. Type an **Interview Question**  
    4. Click **Generate**
    """)
    st.markdown("---")
    st.markdown("Powered by OpenAI GPT-4 API + Streamlit")

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

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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
question = st.text_input("🖊️ Enter an interview question (e.g. 'Why should we hire you?')")

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
                ai_reply = response.choices[0].message.content.strip()

                # Append to chat history
                st.session_state.chat_history.append(("You", question))
                st.session_state.chat_history.append(("AI", ai_reply))

                st.success("✅ Response generated!")
                st.subheader("🌟 Suggested Answer")
                st.write(ai_reply)

        except Exception as e:
            st.error(f"⚠️ Unexpected Error: {str(e)}")

# Show chat history
if st.session_state.chat_history:
    st.subheader("🗂️ Conversation History")
    for speaker, message in st.session_state.chat_history:
        st.markdown(f"**{speaker}:** {message}")

    # Download chat history
    def generate_chat_download():
        lines = [f"{speaker}: {message}" for speaker, message in st.session_state.chat_history]
        return "\n\n".join(lines)

    chat_text = generate_chat_download()
    st.download_button(
        label="📅 Download Chat History",
        data=chat_text,
        file_name="interview_chat_history.txt",
        mime="text/plain"
    )

    # Clear button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()

# Footer
st.markdown("<hr><p style='text-align: center; color: grey;'>© 2025 AI Interview Coach | Powered by OpenAI GPT-4 API + Streamlit</p>", unsafe_allow_html=True)
