import streamlit as st
import google.generativeai as genai

st.title("AI Serial Log Analyzer")

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("gemini-1.5-flash")

uploaded_file = st.file_uploader(
    "Upload Log",
    type=["txt", "log"]
)

if uploaded_file:

    log_content = uploaded_file.read().decode("utf-8")

    st.text(log_content)

    if st.button("Analyze"):

        response = model.generate_content(
            f"""
            Analyze this serial log.

            Identify:
            1. Errors
            2. Failure Type
            3. Root Cause
            4. Debug Actions

            Log:

            {log_content}
            """
        )

        st.write(response.text)
