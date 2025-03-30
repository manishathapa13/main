import streamlit as st
import openai

st.set_page_config(page_title="AI Interview Coach", layout="centered")

# 💬 Title
st.title("🧠 AI Interview Coach")
st.write("Practice interview questions using your resume and a job description. Get instant feedback powered by GPT-3.5.")

# 🚫 Don't expose your key publicly
openai.api_key = "sk-REPLACE_WITH_YOURS"

# 📝 Input fields
resume = st.text_area("📄 Paste your resume", height=200)
job_desc = st.text_area("📝 Paste the job description", height=200)
question = st.text_input("🎤 Enter an interview question (e.g. 'Tell me about yourself')")

if st.button("🧠 Generate Response"):
    if not (resume and job_desc and question):
        st.warning("Please fill in all fields.")
    else:
        prompt = f"""
You are an AI interview coach.
Resume: {resume}
Job Description: {job_desc}
Interview Question: {question}

Generate a strong, relevant interview response.
Then provide coaching feedback on clarity, tone, and suggestions for improvement.
"""

        with st.spinner("Generating response..."):
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content
            st.success("✅ Response Generated")
            st.markdown(answer)
