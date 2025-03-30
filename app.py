import streamlit as st
import openai

# Set OpenAI API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Title
st.title("🧠 AI Interview Coach")
st.write("Practice interview questions using your resume and a job description. Get instant feedback powered by GPT-4.")

# Upload Resume
resume_file = st.file_uploader("📄 Upload your resume", type=["pdf", "docx", "txt"])
resume = ""
if resume_file is not None:
    resume = resume_file.read().decode("utf-8", errors="ignore")

# Upload Job Description
job_file = st.file_uploader("📋 Upload the job description", type=["pdf", "docx", "txt"])
job_desc = ""
if job_file is not None:
    job_desc = job_file.read().decode("utf-8", errors="ignore")

# Question input
question = st.text_input("🖊️ Enter an interview question (e.g. 'Tell me about yourself')")

# Button
if st.button("✨ Generate Response"):
    if not resume or not job_desc or not question:
        st.warning("Please upload both files and enter a question.")
    else:
        try:
            prompt = f"""
            You are an AI interview coach.
            Candidate's Resume: {resume}
            Job Description: {job_desc}
            Interview Question: {question}
            Provide an ideal answer and briefly explain why it's strong.
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            st.subheader("🎯 Suggested Answer")
            st.write(response.choices[0].message.content.strip())

        except openai.OpenAIError as e:
            st.error(f"❗ OpenAI Error: {str(e)}")
        except Exception as e:
            st.error(f"⚠️ Unexpected Error: {str(e)}")
