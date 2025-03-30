import streamlit as st
import openai
from openai.error import AuthenticationError

# Set OpenAI API key securely from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Title
st.title("🧠 AI Interview Coach")

# Description
st.write("Practice interview questions using your resume and a job description. Get instant feedback powered by GPT-4.")

# Input fields
resume = st.text_area("📄 Paste your resume", height=200)
job_desc = st.text_area("📝 Paste the job description", height=200)
question = st.text_input("🎤 Enter an interview question (e.g. 'Tell me about yourself')")

if st.button("💬 Generate Response"):
    if not (resume and job_desc and question):
        st.warning("Please fill in all fields.")
    else:
        prompt = f"""
You are an AI interview coach.
Resume: {resume}
Job Description: {job_desc}
Interview Question: {question}
Respond as if you're the candidate. Use a confident, concise tone aligned with the job and resume.
"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful AI interview coach."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content
            st.subheader("🎯 Suggested Answer")
            st.write(answer)

        except AuthenticationError:
            st.error("⚠️ Invalid OpenAI API Key. Please check your Streamlit secrets.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
