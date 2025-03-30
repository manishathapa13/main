import streamlit as st
import openai
from openai.error import AuthenticationError

# App Title
st.title("🧠 AI Interview Coach")
st.write("Practice interview questions using your resume and a job description. "
         "Get instant feedback powered by GPT-4.")

# Load API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Input Fields
st.subheader("📥 Input Information")
resume = st.text_area("📄 Paste your resume", height=200)
job_desc = st.text_area("📝 Paste the job description", height=200)
question = st.text_input("🎙️ Enter an interview question (e.g. 'Tell me about yourself')")

# Generate Button
if st.button("✨ Generate Response"):
    if not (resume and job_desc and question):
        st.warning("⚠️ Please fill in all fields.")
    else:
        with st.spinner("Generating response..."):
            try:
                prompt = f"""
You are an AI interview coach.

Analyze the following resume and job description, and give a strong answer to the interview question:

Resume:
{resume}

Job Description:
{job_desc}

Interview Question:
{question}
                """

                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert career coach."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )

                answer = response.choices[0].message.content
                st.subheader("🎯 Suggested Answer")
