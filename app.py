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
    .highlight-input input {
        background-color: #fffbea !important;
        border: 2px solid #f1c40f !important;
        box-shadow: 0 0 10px rgba(241, 196, 15, 0.6) !important;
    }
    .highlight-button button {
        background-color: #f39c12 !important;
        color: white !important;
        font-weight: bold;
        box-shadow: 0 0 10px rgba(243, 156, 18, 0.6);
        transition: 0.3s ease;
    }
    .highlight-button button:hover {
        background-color: #e67e22 !important;
    }
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

# Interview question with highlight style

# Generate top 10 suggested questions based on resume + job description
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []

resume_final = extract_text(resume_file) if resume_file else resume_text
job_final = extract_text(job_file) if job_file else job_text

if resume_final and job_final and not st.session_state.suggested_questions:
    with st.spinner("Analyzing resume and job description for tailored questions..."):
        try:
            suggestion_prompt = f"""
You are an expert interview coach.

Given the resume and job description below, generate a list of the top 10 interview questions a candidate should prepare for. Format clearly.

Resume:
{resume_final}

Job Description:
{job_final}
"""
            suggestion_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert career advisor."},
                    {"role": "user", "content": suggestion_prompt}
                ]
            )
            st.session_state.suggested_questions = suggestion_response.choices[0].message.content.strip()
            st.success("✅ Suggested questions generated!")
            st.markdown("### 💡 Suggested Interview Questions")
            st.markdown(st.session_state.suggested_questions)
        except Exception as e:
            st.warning(f"⚠️ Could not fetch suggested questions: {str(e)}")

st.markdown("""
    <div style='background-color:#fff8dc;padding:15px;border-radius:10px;border:2px solid #f1c40f;box-shadow: 0 0 10px rgba(241,196,15,0.5);'>
        <strong>🖊️ Enter an interview question (e.g. 'Why should we hire you?')</strong>
    </div>
""", unsafe_allow_html=True)
question = st.text_input("", key="interview_q")

# Button with highlight style
if st.button("✨ Generate Response", help="Click to generate AI-powered feedback"):
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

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()

# Footer
st.markdown("<hr><p style='text-align: center; color: grey;'>© 2025 AI Interview Coach | Powered by OpenAI GPT-4 API + Streamlit</p>", unsafe_allow_html=True)
