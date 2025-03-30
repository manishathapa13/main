import streamlit as st
import openai

# Set OpenAI API key securely from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# UI: Title and intro
st.title("AI Interview Coach")
st.write("Practice interview questions using your resume and a job description. Get instant feedback powered by GPT-4.")

# Input fields
resume = st.text_area("📄 Paste your resume", height=200)
job_desc = st.text_area("🧾 Paste the job description", height=200)
question = st.text_input("🎤 Enter an interview question (e.g. 'Tell me about yourself')")

# When button is clicked
if st.button("💬 Generate Response"):
    if not (resume and job_desc and question):
        st.warning("Please fill in all fields.")
    else:
        # Prompt for GPT-4
        prompt = f"""
You are an AI interview coach.

Resume: {resume}

Job Description: {job_desc}

Interview Question: {question}

Generate a suggested response for the interview question tailored to the resume and job description above.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert AI interview coach."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response['choices'][0]['message']['content']
            st.subheader("🎯 Suggested Answer")
            st.write(answer)

        except openai.error.AuthenticationError:
            st.error("⚠️ Invalid OpenAI API Key. Please check your Streamlit secrets.")
        except Exception as e:
            st.error(f"🚨 An unexpected error occurred: {e}")
