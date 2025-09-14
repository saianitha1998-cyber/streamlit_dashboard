import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prospectra Dashboard", layout="wide")

# ---- Mock credentials ----
USER_CREDENTIALS = {
    "admin": "admin123",
    "user": "user123"
}

# ---- Session state ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Dashboard"

# ---- Login Page ----
if not st.session_state.logged_in:
    st.title("🔐 Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome {username}! Redirecting to dashboard...")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

else:
    # ---- NAVBAR ----
    tabs = ["Dashboard", "KPI Recommender", "JIRA", "AI Insights", "Logout"]

    # create horizontal buttons
    cols = st.columns(len(tabs))
    for i, tab in enumerate(tabs):
        if cols[i].button(tab, use_container_width=True):
            st.session_state.active_tab = tab
            if tab == "Logout":
                st.session_state.logged_in = False
                st.session_state.username = ""
            st.rerun()

    st.markdown("---")

    # ---- Pages ----
    if st.session_state.active_tab == "Dashboard":
        st.subheader("📊 Main Dashboard")
        st.info("This is a placeholder for the **Dashboard** page.")

    elif st.session_state.active_tab == "KPI Recommender":
        st.subheader("🤖 KPI Recommender")

        uploaded_file = st.file_uploader("📂 Upload BRD (PDF, DOC, DOCX, TXT)", type=["pdf", "doc", "docx", "txt"])
        if uploaded_file:
            st.success("✅ File uploaded successfully!")
            if st.button("Process Uploaded File"):
                st.info("🔄 Processing file... (mock example)")

        # ---- Preview Extracted KPIs ----
        st.subheader("📊 Preview Extracted Goals & KPIs")
        data_extracted = [
            ["Employee Turnover Rate", "Percentage leaving within a year.", "< 15%", "Extracted"],
            ["Employee Satisfaction Score", "Average quarterly survey score.", "> 8.0/10", "Extracted"],
            ["Employee Retention Rate (1 YR)", "Employees staying after 12 months.", "> 85%", "Extracted"]
        ]
        df_extracted = pd.DataFrame(data_extracted, columns=["KPI Name", "Description", "Target Value", "Status"])
        st.table(df_extracted)

        st.button("✅ Review and Accept")

        # ---- Recommended KPIs ----
        st.subheader("🔎 Extracted & Recommended KPIs")
        data_recommended = [
            ["Employee Turnover Rate", "HR BP 1", "< 15%", "Rejected"],
            ["Employee Satisfaction Score", "HR BP 3", "> 8.0/10", "Validated"],
            ["Employee Retention Rate (1 YR)", "HR BP 3", "> 85%", "Extracted"],
            ["Involuntary Attrition", "HR BP 2", "-", "Recommended"],
            ["Absenteeism Rate", "HR BP 4", "-", "Recommended"],
            ["Time to Fill", "HR BP 1", "-", "Rejected"]
        ]
        df_recommended = pd.DataFrame(data_recommended, columns=["KPI Name", "Owner/ SME", "Target Value", "Status"])
        st.table(df_recommended)

        st.button("🔒 Validate")

    elif st.session_state.active_tab == "JIRA":
        st.subheader("📌 JIRA Integration & Task Management")
        st.info("This is a placeholder for JIRA-related dashboards and tasks.")

    elif st.session_state.active_tab == "AI Insights":
        st.subheader("📈 AI Insights & Reporting")
        st.info("This is a placeholder for AI-driven insights & reports.")
