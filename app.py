import streamlit as st
import openai

# Set API key securely from Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# App title and instructions
st.title("🧠 AI Interview Coach")
st.write("Practice interview questions using your resume and a job description. Get instant feedback powered by GPT-3.5.")

# 📄 Input fields
st.subheader("📥 Paste your details below:")
resume = st.text_area("📌 Paste your resume", height=200)
job_desc = st.text_area("📝 Paste the job description", height=200)
question = st.text_input("🎤 Enter an interview question (e.g. 'Tell me about yourself')")

# 🚀 Generate button
if st.button("✨ Generate Response"):
    if not (resume and job_desc and question):
        st.warning("⚠️ Please fill in all fields.")
    else:
        # Prompt formatting
        prompt = f"""
        You are an AI interview coach. Based on the resume and job description provided, craft a personalized and professional answer to the following interview question.

        Resume:
        {resume}

        Job Description:
        {job_desc}

        Interview Question:
        {question}

        Answer:
        """

        with st.spinner("Thinking... 🤖"):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an experienced career coach and recruiter."},
                        {"role": "user", "content": prompt}
                    ]
                )
                answer = response.choices[0].message.content
                st.success("✅ Here's a suggested answer:")
                st.write(answer)

            except openai.error.AuthenticationError:
                st.error("❌ Invalid OpenAI API key. Please check your Streamlit secrets.")
            except Exception as e:
                st.error(f"⚠️ An unexpected error occurred: {e}")
