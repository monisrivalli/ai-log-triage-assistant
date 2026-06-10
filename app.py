import streamlit as st

st.title("AI Serial Log Analyzer")

uploaded_file = st.file_uploader(
    "Upload Log",
    type=["txt", "log"]
)

if uploaded_file:

    log_content = uploaded_file.read().decode("utf-8")

    st.write(log_content)
