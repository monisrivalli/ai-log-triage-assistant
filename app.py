import streamlit as st
import google.generativeai as genai
from datetime import datetime

st.title("AI Serial Log Analyzer")

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# Configure Gemini
genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("models/gemini-2.5-flash")

# Upload log file
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

            Provide the following sections:

            Failure Type:
            Confidence:
            Affected Component:
            Priority:

            Errors:
            Root Cause:
            Debug Actions:

            Log:

            {log_content}
            """
        )

        result = response.text

        # -----------------------------
        # Failure Summary Card
        # -----------------------------
        failure_type = "Unknown"
        confidence = "N/A"
        component = "Unknown"
        priority = "Unknown"

        for line in result.splitlines():

            if "Failure Type:" in line:
                failure_type = line.split(":", 1)[1].strip()

            elif "Confidence:" in line:
                confidence = line.split(":", 1)[1].strip()

            elif "Affected Component:" in line:
                component = line.split(":", 1)[1].strip()

            elif "Priority:" in line:
                priority = line.split(":", 1)[1].strip()

        st.subheader("Failure Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Failure Type:** {failure_type}")
            st.info(f"**Confidence:** {confidence}")

        with col2:
            st.info(f"**Affected Component:** {component}")

            if priority.lower() == "high":
                st.error(f"Priority: {priority}")
            elif priority.lower() == "medium":
                st.warning(f"Priority: {priority}")
            else:
                st.success(f"Priority: {priority}")

        # -----------------------------
        # Full Analysis Result
        # -----------------------------
        st.subheader("Analysis Result")
        st.write(result)

        # -----------------------------
        # Save History
        # -----------------------------
        st.session_state.history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file": uploaded_file.name,
            "result": result
        })

# -----------------------------
# Sidebar History
# -----------------------------
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
