import streamlit as st
import google.generativeai as genai
from datetime import datetime
import sqlite3

# -----------------------------
# Database Setup
# -----------------------------
conn = sqlite3.connect(
    "log_history.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    filename TEXT,
    result TEXT
)
""")

conn.commit()

# -----------------------------
# App Title
# -----------------------------
st.title("AI Serial Log Analyzer")

# -----------------------------
# Gemini Configuration
# -----------------------------
genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)

# -----------------------------
# Upload Log
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Log",
    type=["txt", "log"]
)

if uploaded_file:

    log_content = uploaded_file.read().decode(
        "utf-8"
    )

    st.subheader("Uploaded Log")

    st.text(log_content)

    if st.button("Analyze"):

        response = model.generate_content(
            f"""
You are an expert Linux System Administrator and Post-Silicon Validation Engineer.

Analyze the following log.

Return the response EXACTLY in this format:

Failure Type: <value>
Confidence: <value>
Affected Component: <value>
Priority: <value>

Errors:
- <error1>
- <error2>

Root Cause:
<root cause>

Debug Actions:
1. <action1>
2. <action2>
3. <action3>

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

            if line.startswith(
                "Failure Type:"
            ):
                failure_type = (
                    line.replace(
                        "Failure Type:",
                        ""
                    ).strip()
                )

            elif line.startswith(
                "Confidence:"
            ):
                confidence = (
                    line.replace(
                        "Confidence:",
                        ""
                    ).strip()
                )

            elif line.startswith(
                "Affected Component:"
            ):
                component = (
                    line.replace(
                        "Affected Component:",
                        ""
                    ).strip()
                )

            elif line.startswith(
                "Priority:"
            ):
                priority = (
                    line.replace(
                        "Priority:",
                        ""
                    ).strip()
                )

        # -----------------------------
        # Failure Summary Card
        # -----------------------------
        st.subheader(
            "Failure Summary"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.info(
                f"**Failure Type:** {failure_type}"
            )

            st.info(
                f"**Confidence:** {confidence}"
            )

        with col2:

            st.info(
                f"**Affected Component:** {component}"
            )

            if priority.lower() == "critical":

                st.error(
                    f"Priority: {priority}"
                )

            elif priority.lower() == "high":

                st.error(
                    f"Priority: {priority}"
                )

            elif priority.lower() == "medium":

                st.warning(
                    f"Priority: {priority}"
                )

            else:

                st.success(
                    f"Priority: {priority}"
                )

        # -----------------------------
        # Full Analysis
        # -----------------------------
        st.subheader(
            "Analysis Result"
        )

        st.write(result)

        # -----------------------------
        # Save To Database
        # -----------------------------
        cursor.execute(
            """
            INSERT INTO history
            (
                timestamp,
                filename,
                result
            )
            VALUES (?, ?, ?)
            """,
            (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                uploaded_file.name,
                result
            )
        )

        conn.commit()

# -----------------------------
# Sidebar History Search
# -----------------------------
st.sidebar.title(
    "Analysis History"
)

search_term = st.sidebar.text_input(
    "Search History"
)

if search_term:

    cursor.execute(
        """
        SELECT timestamp,
               filename,
               result
        FROM history
        WHERE filename LIKE ?
        ORDER BY id DESC
        """,
        (
            f"%{search_term}%",
        )
    )

else:

    cursor.execute(
        """
        SELECT timestamp,
               filename,
               result
        FROM history
        ORDER BY id DESC
        """
    )

records = cursor.fetchall()

# -----------------------------
# Display History
# -----------------------------
if records:

    for record in records:

        timestamp = record[0]
        filename = record[1]
        result = record[2]

        with st.sidebar.expander(
            filename
        ):

            st.write(
                f"Time: {timestamp}"
            )

            st.write(result)

else:

    st.sidebar.write(
        "No history available."
    )
