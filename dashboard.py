import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prospectra - KPI Recommender", layout="wide")

# ---- CUSTOM STYLES ----
st.markdown(
    """
    <style>
        .nav-container {
            display: flex;
            justify-content: left;
            gap: 30px;
            background-color: #f9f9f9;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        .nav-item {
            font-size: 16px;
            font-weight: 600;
            color: #444;
            text-decoration: none;
            cursor: pointer;
        }
        .nav-item:hover {
            color: #8B0000;
        }
        .title {font-size:28px; font-weight:600; color:#8B0000;}
        .status-tag {
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }
        .Extracted {background-color: #5DADE2;}
        .Validated {background-color: #28B463;}
        .Rejected {background-color: #E74C3C;}
        .Recommended {background-color: #17A589;}
    </style>
    """,
    unsafe_allow_html=True
)

# ---- NAVIGATION ----
if "page" not in st.session_state:
    st.session_state.page = "KPI Recommender"  # default page

nav_items = ["Dashboard", "KPI Recommender", "JIRA Integration & Task Management", "AI Insights & Reporting"]

st.markdown('<div class="nav-container">' + "".join(
    [f"<span class='nav-item' onclick='window.parent.postMessage({{\"page\": \"{item}\"}}, \"*\")'>{item}</span>" for item in nav_items]
) + "</div>", unsafe_allow_html=True)

# ---- HANDLE NAVIGATION ----
page = st.session_state.page

# ---- PAGE CONTENT ----
if page == "Dashboard":
    st.subheader("📊 Welcome to the Main Dashboard")
    st.info("This is a placeholder for the **Dashboard** page.")

elif page == "KPI Recommender":
    st.subheader("🤖 KPI Recommender")

    # ---- FILE UPLOAD ----
    uploaded_file = st.file_uploader("📂 Upload BRD (PDF, DOC, DOCX, TXT)", type=["pdf", "doc", "docx", "txt"])
    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        if st.button("Process Uploaded File"):
            st.info("🔄 Processing file... (mock example)")

    # ---- EXTRACTED KPIs ----
    st.subheader("📊 Preview Extracted Goals & KPIs")

    data_extracted = [
        ["Employee Turnover Rate", "Percentage leaving within a year.", "< 15%", "Extracted"],
        ["Employee Satisfaction Score", "Average quarterly survey score.", "> 8.0/10", "Extracted"],
        ["Employee Retention Rate (1 YR)", "Employees staying after 12 months.", "> 85%", "Extracted"]
    ]
    df_extracted = pd.DataFrame(data_extracted, columns=["KPI Name", "Description", "Target Value", "Status"])

    def render_status(status):
        return f"<span class='status-tag {status}'>{status}</span>"

    df_extracted["Status"] = df_extracted["Status"].apply(lambda x: render_status(x))
    st.write(df_extracted.to_html(escape=False, index=False), unsafe_allow_html=True)

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
    df_recommended["Status"] = df_recommended["Status"].apply(lambda x: render_status(x))
    st.write(df_recommended.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.button("🔒 Validate")

elif page == "JIRA Integration & Task Management":
    st.subheader("📌 JIRA Integration & Task Management")
    st.info("This is a placeholder for JIRA-related dashboards and tasks.")

elif page == "AI Insights & Reporting":
    st.subheader("📈 AI Insights & Reporting")
    st.info("This is a placeholder for AI-driven insights & reports.")
