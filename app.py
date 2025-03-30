import streamlit as st
import openai
import fitz  # PyMuPDF
import docx

# Set OpenAI API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Utility to extract text from uploaded files
def extract_text(file):
    if file.name.endswith('.pdf'):
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text()
        return text
    elif file.name.endswith('.docx'):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return None

# App UI
st.title("📄 AI Interview Coach")

st.markdown("### ➤ Resume (Paste or Upload)")
resume_text = st.text_area("📋 Paste your resume", height=200)
resume_file = st.file_uploader("Or upload resume file (.pdf or .docx)", type=["pdf", "docx"])

st.markdown("### ➤ Job Description (Paste or Upload)")
job_text = st.text_area("📋 Paste the job description", height=200)
job_file = st.file_uploader("Or upload job description file (.pdf or .docx)", type=["pdf", "docx"], key="job")

question = st.text_input("🖊️ Enter an interview question (e.g. 'Tell me about yourself')")

if st.button("⚡ Generate Response"):
    # Use uploaded file content if present
    if resume_file:
        resume = extract_text(resume_file)
    else:
        resume = resume_text

    if job_file:
        job_desc = extract_text(job_file)
    else:
        job_desc = job_text

    if not resume or not job_desc or not question:
        st.warning("🚫 Please provide resume, job description, and an interview question.")
    else:
        try:
            prompt = f"""
You are an AI interview coach.
Resume:
{resume}

Job Description:
{job_desc}

Interview Question: {question}

Provide a great example answer.
"""

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            st.subheader("🎯 Suggested Answer")
            st.write(response.choices[0].message.content.strip())

        except openai.error.OpenAIError as e:
            st.error(f"🛑 OpenAI Error: {str(e)}")
        except Exception as e:
            st.error(f"⚠️ Unexpected Error: {str(e)}")
