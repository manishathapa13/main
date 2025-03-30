import streamlit as st
import openai

# 🛠 Page config
st.set_page_config(page_title="AI Interview Coach", layout="wide")

# 🔐 Secure API setup
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 💅 Custom background & styles
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f9f9f9;
        font-family: 'Segoe UI', sans-serif;
    }
    h1 {
        text-align: center;
        color: #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 🧭 Sidebar with instructions
with st.sidebar:
    st.title("🛠️ How to Use")
    st.markdown("""
    1. Paste your **resume**
    2. Paste the **job description**
    3. Enter an **interview question**
    4. Click **✨ Generate Response**
    """)
    st.markdown("---")
    st.markdown("Built with ❤️ using GPT-4 + Streamlit")

# 🎯 Main Title
st.markdown("<h1>🌟 AI Interview Coach</h1>", unsafe_allow_html=True)
st.markdown("Practice interview questions using your resume and a job description. Get instant feedback powered by GPT-4.")
st.markdown("---")

# 🧾 Input Layout: Two Columns
col1, col2 = st.columns(2)

with col1:
    resume = st.text_area("📄 Paste your resume", height=250)

with col2:
    job_desc = st.text_area("📋 Paste the job description", height=250)

# 🎤 Question input
question = st.text_input("🖊️ Enter an interview question (e.g. 'Why should we hire you?')")

# 🚀 Generate Button
if st.button("✨ Generate Response"):
    if not resume or not job_desc or not question:
        st.warning("🚫 Please complete all inputs before generating a response.")
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
            st.error(f"⚠️ Unexpected error: {str(e)}")

# 🦶 Footer
st.markdown("<hr><p style='text-align: center; color: grey;'>© 2025 AI Interview Coach | Powered by OpenAI GPT-4 & Streamlit</p>", unsafe_allow_html=True)
