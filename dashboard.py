import streamlit as st
import pandas as pd
import docx  # for docx parsing
import pdfplumber  # for pdf parsing
import io

st.set_page_config(page_title="Prospectra Dashboard", layout="wide")

# ---- Mock credentials ----
USER_CREDENTIALS = {"admin": "admin123", "user": "user123"}

# ---- Session state ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Dashboard"
if "extracted_kpis" not in st.session_state:
    st.session_state.extracted_kpis = pd.DataFrame()
if "recommended_kpis" not in st.session_state:
    st.session_state.recommended_kpis = pd.DataFrame()


# ---- Helper: Extract text from uploaded file ----
def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif uploaded_file.name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    else:  # txt
        return uploaded_file.read().decode("utf-8", errors="ignore")


# ---- Helper: Extract KPIs from text ----
def extract_kpis_from_text(text):
    kpis = []

    if "drop-off" in text.lower():
        kpis.append(["Application Drop-off Rate", "% candidates abandoning application", "Reduce", "Extracted"])
    if "time-to-fill" in text.lower() or "time to fill" in text.lower():
        kpis.append(["Time-to-Fill", "Avg. days to close requisition", "< 30 days", "Extracted"])
    if "candidate satisfaction" in text.lower():
        kpis.append(["Candidate Satisfaction Score", "Survey rating from candidates", "> 8/10", "Extracted"])
    if "automation" in text.lower():
        kpis.append(["Automation Rate", "% workflows automated", "> 80%", "Extracted"])
    if "1000 requisitions" in text.lower():
        kpis.append(["Requisition Throughput", "No. requisitions handled per day", "1000/day", "Extracted"])
    if "uptime" in text.lower():
        kpis.append(["System Uptime", "System availability", "> 99%", "Extracted"])
    if "productivity" in text.lower():
        kpis.append(["Recruiter Productivity", "Avg. requisitions closed per recruiter", "↑ Increase", "Extracted"])
    if "integration" in text.lower():
        kpis.append(["Integration Success Rate", "% of successful integrations", "> 95%", "Extracted"])

    return pd.DataFrame(kpis, columns=["KPI Name", "Description", "Target Value", "Status"])


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
    # ---- Navbar ----
    tabs = ["Dashboard", "KPI Recommender", "JIRA", "AI Insights"]
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
        cols = st.columns(len(tabs))
        for i, tab in enumerate(tabs):
            if cols[i].button(tab, use_container_width=True):
                st.session_state.active_tab = tab
                st.rerun()
    with nav_right:
        if st.button("Logout", use_container_width=True):
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

        # ---- File Upload ----
        uploaded_file = st.file_uploader("📂 Upload BRD (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if uploaded_file and st.button("Process BRD File"):
            st.info("🔄 Extracting KPIs...")
            text = extract_text(uploaded_file)
            df_extracted = extract_kpis_from_text(text)
            st.session_state.extracted_kpis = df_extracted.copy()

            # Create Recommended KPIs table
            recommended = []
            for _, row in df_extracted.iterrows():
                recommended.append([row["KPI Name"], "Talent Acquisition / IT", row["Target Value"], "Recommended"])
            st.session_state.recommended_kpis = pd.DataFrame(
                recommended, columns=["KPI Name", "Owner/ SME", "Target Value", "Status"]
            )
            st.success("✅ KPIs extracted successfully!")

        # ---- Show Extracted KPIs ----
        if not st.session_state.extracted_kpis.empty:
            st.subheader("📊 Preview Extracted Goals & KPIs")
            st.dataframe(st.session_state.extracted_kpis, use_container_width=True)

        if not st.session_state.recommended_kpis.empty:
            st.subheader("🔎 Extracted & Recommended KPIs")
            st.dataframe(st.session_state.recommended_kpis, use_container_width=True)

    elif st.session_state.active_tab == "JIRA":
        st.subheader("📌 JIRA Integration & Task Management")
        st.info("This is a placeholder for JIRA-related dashboards and tasks.")

    elif st.session_state.active_tab == "AI Insights":
        st.subheader("📈 AI Insights & Reporting")
        st.info("This is a placeholder for AI-driven insights & reports.")
