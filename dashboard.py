import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prospectra Dashboard", layout="wide")

# ---- Mock credentials ----
USER_CREDENTIALS = {"admin": "admin123", "user": "user123"}

# ---- Session state defaults ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "KPI Recommender"
if "brd_uploaded" not in st.session_state:
    st.session_state.brd_uploaded = False
if "review_done" not in st.session_state:
    st.session_state.review_done = False

# ---- Login Page ----
if not st.session_state.logged_in:
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# ---- Main App ----
else:
    # Navbar
    nav_left, nav_right = st.columns([4, 1])
    with nav_left:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:10px;">
                <img src="https://i.ibb.co/h8rjN50/prospectra-icon.png" width="40">
                <h3 style="margin:0; color:#d00000;">Prospectra</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
        tabs = ["Dashboard", "KPI Recommender", "JIRA", "AI Insights"]
        cols = st.columns(len(tabs))
        for i, tab in enumerate(tabs):
            if cols[i].button(tab, use_container_width=True):
                st.session_state.active_tab = tab
                st.rerun()
    with nav_right:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.brd_uploaded = False
            st.session_state.review_done = False
            st.rerun()

    st.markdown("---")

    if st.session_state.active_tab == "KPI Recommender":
        st.subheader("🤖 KPI Recommender")

        # ---- Upload BRD ----
        uploaded_file = st.file_uploader(
            "📂 Upload Business Requirements Document (BRD)",
            type=["docx", "pdf", "txt"]
        )

        if uploaded_file and st.button("Process Uploaded File"):
            # Simulated extraction
            st.session_state.brd_uploaded = True
            st.session_state.review_done = False

            # Mock extracted KPIs
            st.session_state.extracted = pd.DataFrame([
                ["Employee Turnover Rate", "Percentage of employees leaving within a year.", "< 15%", "Extracted"],
                ["Employee Satisfaction Score", "Average quarterly employee survey score.", "> 8.0/10", "Extracted"],
                ["Employee Retention Rate (1 YR)", "Employees remaining after 12 months.", "> 85%", "Extracted"],
            ], columns=["KPI Name", "Description", "Target Value", "Status"])

            # Mock recommended KPIs
            st.session_state.recommended = pd.DataFrame([
                ["Employee Turnover Rate", "HR BP 1", "< 15%", "Rejected"],
                ["Employee Satisfaction Score", "HR BP 3", "> 8.0/10", "Validated"],
                ["Employee Retention Rate (1 YR)", "HR BP 3", "> 85%", "Extracted"],
                ["Involuntary Attrition", "HR BP 2", "-", "Recommended"],
                ["Absenteeism Rate", "HR BP 4", "-", "Recommended"],
                ["Time to Fill", "HR BP 1", "-", "Rejected"],
            ], columns=["KPI Name", "Owner/ SME", "Target Value", "Status"])

        # ---- Step 1: Show Preview Extracted only ----
        if st.session_state.brd_uploaded and not st.session_state.review_done:
            st.markdown("### 📊 Preview Extracted Goals & KPIs")
            st.caption("Review the automatically extracted project goals and KPIs below.")

            header_cols = st.columns([3, 5, 2, 2, 2])
            headers = ["KPI Name", "Description", "Target Value", "Status", "Actions"]
            for col, h in zip(header_cols, headers):
                col.markdown(f"**{h}**")

            for i, row in st.session_state.extracted.iterrows():
                cols = st.columns([3, 5, 2, 2, 2])
                cols[0].write(row["KPI Name"])
                cols[1].write(row["Description"])
                cols[2].write(row["Target Value"])
                cols[3].write(f"🟦 {row['Status']}")
                if cols[4].button("Review", key=f"review_{i}"):
                    st.info(f"Review clicked for {row['KPI Name']}")

            if st.button("✅ Review and Accept", use_container_width=True):
                st.session_state.review_done = True
                st.rerun()

        # ---- Step 2: After Review → Show Recommended ----
        if st.session_state.review_done:
            st.markdown("### 🔎 Extracted & Recommended KPIs")
            st.caption("Review and manage extracted and recommended KPIs.")

            header_cols = st.columns([3, 3, 2, 2, 4])
            headers = ["KPI Name", "Owner/ SME", "Target Value", "Status", "Actions"]
            for col, h in zip(header_cols, headers):
                col.markdown(f"**{h}**")

            for i, row in st.session_state.recommended.iterrows():
                cols = st.columns([3, 3, 2, 2, 4])
                cols[0].write(row["KPI Name"])
                cols[1].write(row["Owner/ SME"])
                cols[2].write(row["Target Value"])
                cols[3].write(f"🔘 {row['Status']}")
                with cols[4]:
                    c1, c2, c3 = st.columns([1, 1, 1])
                    if c1.button("Review", key=f"rec_review_{i}"):
                        st.info(f"Review clicked for {row['KPI Name']}")
                    if c2.button("Validate", key=f"rec_validate_{i}"):
                        st.success(f"Validated {row['KPI Name']}")
                    if c3.button("Reject", key=f"rec_reject_{i}"):
                        st.error(f"Rejected {row['KPI Name']}")

            st.button("🔒 Validate", use_container_width=True)
