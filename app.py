import streamlit as st
import openai
import fitz  # PyMuPDF
import docx
from PIL import Image
import pytesseract

# Page config
st.set_page_config(page_title="AI Interview Coach", layout="wide")

# OpenAI setup
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Custom style
st.markdown("""
    <style>
    .stApp { background-color: #f9f9f9; font-family: 'Segoe UI', sans-serif; }
    h1 { text-align: center; color: #4CAF50; }
    </style>
""", unsafe_allow_html=True)

# Sidebar instructions
with st.sidebar:
    st.title("🛠️ How to Use")
    st.markdown("""
    1. Upload your **Resume**  
    2. Upload the **Job Description**  
    3. Type an **Interview Question**  
    4. Click **Generate**
    """)
    st.markdown("---")
    st.markdown("Built with ❤️ using GPT-4 + Streamlit")

# Title
st.markdown("<h1>🌟 AI Interview Coach</h1>", unsafe_allow_html=True)
st.markdown("Practice interview questions using your resume and a job description. Get instant feedback powered by GPT-4.")
st.markdown("---")

# Function to extract text from supported file types
def extract_text(file):
    file_name = file.name.lower()
    if file_name.endswith(".pdf"):
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in pdf])
    elif file_name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file_name.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")
    elif file_name.endswith((".jpg", ".jpeg", ".png")):
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    return None

# Upload fields
col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("📄 Upload Resume", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"])
with col2:
    job_file = st.file_uploader("📋 Upload Job Description", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"])

# Question input
question = st.text_input("🖊️ Enter an interview question (e.g. 'Why should we hire you?')")

# Generate response
if st.button("✨ Generate Response"):
    if not resume_file or not job_file or not question:
        st.warning("🚫 Please upload both documents and enter a question.")
    else:
        with st.spinner("Extracting file contents..."):
            resume = extract_text(resume_file)
            job_desc = extract_text(job_file)

        if not resume or not job_desc:
            st.error("⚠️ Could not extract text from one or both files.")
        else:
            prompt = f"""
You are an AI interview coach.

Here is the candidate's resume:
{resume}

Here is the job description:
{job_desc}

Interview question:
{question}

Evaluate how well the resume and question align with the job, then suggest a professional and improved answer. Keep tone confident and concise.
"""
            try:
                with st.spinner("Thinking like a recruiter... 🤖"):
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

            except Exception as e:
                st.error(f"⚠️ Unexpected Error: {str(e)}")

# Footer
st.markdown("<hr><p style='text-align: center; color: grey;'>© 2025 AI Interview Coach | Powered by OpenAI GPT-4 & Streamlit</p>", unsafe_allow_html=True)
