import streamlit as st
from openai import OpenAI

st.title("AI Serial Log Analyzer")

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

uploaded_file = st.file_uploader(
    "Upload Log",
    type=["txt","log"]
)

if uploaded_file:

    log_content = uploaded_file.read().decode("utf-8")

    st.text(log_content)

    if st.button("Analyze"):

        response = client.chat.completions.create(
            model="model="gpt-5",
            messages=[
                {
                    "role":"user",
                    "content":f"""
                    Analyze this serial log.

                    Identify:
                    1. Errors
                    2. Failure Type
                    3. Root Cause
                    4. Debug Actions

                    Log:

                    {log_content}
                    """
                }
            ]
        )

        st.write(
            response.choices[0].message.content
        )
