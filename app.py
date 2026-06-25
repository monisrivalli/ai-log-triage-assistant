import streamlit as st
import google.generativeai as genai
from datetime import datetime
import sqlite3

# ==================================
# DATABASE SETUP
# ==================================

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
    category TEXT,
    failure_type TEXT,
    priority TEXT,
    result TEXT
)
""")

conn.commit()

# ==================================
# APP TITLE
# ==================================

st.title("AI Serial Log Analyzer")

# ==================================
# GEMINI CONFIGURATION
# ==================================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)

# ==================================
# FILE UPLOAD
# ==================================

uploaded_file = st.file_uploader(
    "Upload Log",
    type=["txt", "log"]
)

if uploaded_file:

    log_content = uploaded_file.read().decode(
        "utf-8",
        errors="ignore"
    )

    st.subheader("Uploaded Log")

    st.text_area(
        "Log Content",
        log_content,
        height=300
    )

    if st.button("Analyze"):

        response = model.generate_content(
            f"""
You are an expert Linux System Administrator and Post-Silicon Validation Engineer.

Analyze the following log.

Return the response EXACTLY in this format:

Category: <PCIe | USB | Memory | BIOS | Firmware | Ethernet | Storage | Power | Thermal | Security>

Failure Type: <value>

Confidence: <value>

Affected Component: <value>

Priority: <Critical | High | Medium | Low>

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

        # ==================================
        # PARSE RESPONSE
        # ==================================

        category = "Unknown"
        failure_type = "Unknown"
        confidence = "N/A"
        component = "Unknown"
        priority = "Unknown"

        for line in result.splitlines():

            line = line.strip()

            if line.startswith("Category:"):
                category = line.replace(
                    "Category:",
                    ""
                ).strip()

            elif line.startswith("Failure Type:"):
                failure_type = line.replace(
                    "Failure Type:",
                    ""
                ).strip()

            elif line.startswith("Confidence:"):
                confidence = line.replace(
                    "Confidence:",
                    ""
                ).strip()

            elif line.startswith(
                "Affected Component:"
            ):
                component = line.replace(
                    "Affected Component:",
                    ""
                ).strip()

            elif line.startswith("Priority:"):
                priority = line.replace(
                    "Priority:",
                    ""
                ).strip()

        # ==================================
        # FAILURE SUMMARY
        # ==================================

        st.subheader("Failure Summary")

        col1, col2 = st.columns(2)

        with col1:

            st.info(
                f"**Category:** {category}"
            )

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

        # ==================================
        # FULL ANALYSIS
        # ==================================

        st.subheader("Analysis Result")

        st.write(result)

        # ==================================
        # SAVE TO SQLITE
        # ==================================

        cursor.execute(
            """
            INSERT INTO history
            (
                timestamp,
                filename,
                category,
                failure_type,
                priority,
                result
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                uploaded_file.name,
                category,
                failure_type,
                priority,
                result
            )
        )

        conn.commit()

# ==================================
# SIDEBAR
# ==================================

st.sidebar.title(
    "Analysis History"
)

# Search Box
search_term = st.sidebar.text_input(
    "Search File Name"
)

# Category Filter
category_filter = st.sidebar.selectbox(
    "Filter By Category",
    [
        "All",
        "PCIe",
        "USB",
        "Memory",
        "BIOS",
        "Firmware",
        "Ethernet",
        "Storage",
        "Power",
        "Thermal",
        "Security"
    ]
)

# ==================================
# QUERY DATABASE
# ==================================

if category_filter == "All":

    if search_term:

        cursor.execute(
            """
            SELECT timestamp,
                   filename,
                   category,
                   failure_type,
                   priority,
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
                   category,
                   failure_type,
                   priority,
                   result
            FROM history
            ORDER BY id DESC
            """
        )

else:

    cursor.execute(
        """
        SELECT timestamp,
               filename,
               category,
               failure_type,
               priority,
               result
        FROM history
        WHERE category = ?
        ORDER BY id DESC
        """,
        (
            category_filter,
        )
    )

records = cursor.fetchall()

# ==================================
# DISPLAY HISTORY
# ==================================

if records:

    for record in records:

        timestamp = record[0]
        filename = record[1]
        category = record[2]
        failure_type = record[3]
        priority = record[4]
        result = record[5]

        with st.sidebar.expander(
            filename
        ):

            st.write(
                f"**Category:** {category}"
            )

            st.write(
                f"**Failure Type:** {failure_type}"
            )

            st.write(
                f"**Priority:** {priority}"
            )

            st.write(
                f"**Time:** {timestamp}"
            )

            st.write("---")

            st.write(result)

else:

    st.sidebar.write(
        "No history available."
    )
