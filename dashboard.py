import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prospectra - KPI Recommender", layout="wide")

# ---- TITLE ----
st.title("📊 Prospectra Dashboard")

# ---- NAVIGATION USING TABS ----
tabs = st.tabs(["Dashboard", "KPI Recommender", "JIRA Integration & Task Management", "AI Insights & Reporting"])

# ---- TAB 1: DASHBOARD ----
with tabs[0]:
    st.subheader("📊 Main Dashboard")
    st.info("This is a placeholder for the **Dashboard** page.")

# ---- TAB 2: KPI RECOMMENDER ----
with tabs[1]:
    st.subheader("🤖 KPI Recommender")

    uploaded_file = st.file_uploader("📂 Upload BRD (PDF, DOC, DOCX, TXT)", type=["pdf", "doc", "docx", "txt"])
    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        if st.button("Process Uploaded File"):
            st.info("🔄 Processing file... (mock example)")

    # ---- PREVIEW EXTRACTED GOALS & KPIs ----
    st.subheader("📊 Preview Extracted Goals & KPIs")

    data_extracted = [
        ["Employee Turnover Rate", "Percentage leaving within a year.", "< 15%", "Extracted"],
        ["Employee Satisfaction Score", "Average quarterly survey score.", "> 8.0/10", "Extracted"],
        ["Employee Retention Rate (1 YR)", "Employees staying after 12 months.", "> 85%", "Extracted"]
    ]
    df_extracted = pd.DataFrame(data_extracted, columns=["KPI Name", "Description", "Target Value", "Status"])
    st.table(df_extracted)

    st.button("✅ Review and Accept")

    # ---- RECOMMENDED KPIs ----
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

# ---- TAB 3: JIRA INTEGRATION ----
with tabs[2]:
    st.subheader("📌 JIRA Integration & Task Management")
    st.info("This is a placeholder for JIRA-related dashboards and tasks.")

# ---- TAB 4: AI INSIGHTS ----
with tabs[3]:
    st.subheader("📈 AI Insights & Reporting")
    st.info("This is a placeholder for AI-driven insights & reports.")
