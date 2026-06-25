import streamlit as st
import google.generativeai as genai
from datetime import datetime

st.title("AI Serial Log Analyzer")

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("models/gemini-2.5-flash")

uploaded_file = st.file_uploader(
    "Upload Log",
    type=["txt", "log"]
)

if uploaded_file:

    log_content = uploaded_file.read().decode("utf-8")

    st.subheader("Uploaded Log")
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

        result = response.text

        st.subheader("Analysis Result")
        st.write(result)

        # Save to history
        st.session_state.history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file": uploaded_file.name,
            "result": result
        })

# Sidebar History
st.sidebar.title("Analysis History")

if st.session_state.history:

    for i, item in enumerate(
        reversed(st.session_state.history),
        start=1
    ):
        with st.sidebar.expander(
            f"{i}. {item['file']}"
        ):
            st.write(f"Time: {item['time']}")
            st.write(item["result"])

else:
    st.sidebar.write("No history available.")
