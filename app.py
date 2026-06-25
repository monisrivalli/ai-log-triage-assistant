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
You are an expert Linux System Administrator and Post-Silicon Validation Engineer.

Analyze the following log file.

Return the response EXACTLY in this format:

Failure Type: <value>
Confidence: <value>
Affected Component: <value>
Priority: <value>

Errors:
- <error 1>
- <error 2>

Root Cause:
<root cause explanation>

Debug Actions:
1. <action 1>
2. <action 2>
3. <action 3>

Log:

{log_content}
"""
        )

        result = response.text

        # -----------------------------
        # Extract Summary Fields
        # -----------------------------
        failure_type = "Unknown"
        confidence = "N/A"
        component = "Unknown"
        priority = "Unknown"

        for line in result.splitlines():

            if line.startswith("Failure Type:"):
                failure_type = line.replace(
                    "Failure Type:", ""
                ).strip()

            elif line.startswith("Confidence:"):
                confidence = line.replace(
                    "Confidence:", ""
                ).strip()

            elif line.startswith("Affected Component:"):
                component = line.replace(
                    "Affected Component:", ""
                ).strip()

            elif line.startswith("Priority:"):
                priority = line.replace(
                    "Priority:", ""
                ).strip()

        # -----------------------------
        # Failure Summary Card
        # -----------------------------
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

            elif priority.lower() == "critical":
                st.error(f"Priority: {priority}")

            else:
                st.success(f"Priority: {priority}")

        # -----------------------------
        # Full Analysis Result
        # -----------------------------
        st.subheader("Analysis Result")

        st.write(result)

        # -----------------------------
        # Save Analysis History
        # -----------------------------
        st.session_state.history.append({
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
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
            st.write(
                f"Time: {item['time']}"
            )

            st.write(
                item["result"]
            )

else:
    st.sidebar.write(
        "No history available."
    )
