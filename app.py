import streamlit as st
import openai

# 🔐 Secure OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 🧠 App title and description
st.title("AI Interview Coach")
st.write("Practice interview questions using your resume and a job description. Get instant feedback powered by GPT-4.")

# 📄 Input fields
resume = st.text_area("📄 Paste your resume", height=200)
job_desc = st.text_area("🧾 Paste the job description", height=200)
question = st.text_input("🎤 Enter an interview question (e.g. 'Tell me about yourself')")

# 🚀 Generate response
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
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are an expert interview coach."},
                    {"role": "user", "content": prompt}
                ]
            )
            st.subheader("🎯 Suggested Answer")
            st.write(response.choices[0].message.content.strip())

        except openai.error.OpenAIError as e:
            st.error(f"🔐 OpenAI Error: {str(e)}")
        except Exception as e:
            st.error(f"⚠️ Unexpected Error: {str(e)}")
