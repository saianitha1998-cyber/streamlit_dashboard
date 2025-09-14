import streamlit as st
import pandas as pd
import io
import zipfile
import xml.etree.ElementTree as ET
import re

st.set_page_config(page_title="Prospectra Dashboard", layout="wide")

# ---- Mock credentials ----
USER_CREDENTIALS = {"admin": "admin123", "user": "user123"}

# ---- Session state defaults ----
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

# ---- Helpers ----
def color_status(val):
    color_map = {
        "Validated": "background-color: #d4edda; color: #155724; font-weight:bold;",
        "Rejected": "background-color: #f8d7da; color: #721c24; font-weight:bold;",
        "Recommended": "background-color: #cce5ff; color: #004085; font-weight:bold;",
        "Accepted": "background-color: #fff3cd; color: #856404; font-weight:bold;",
        "Extracted": "background-color: #e2e3e5; color: #383d41; font-weight:bold;"
    }
    return color_map.get(val, "")

def safe_data_editor(df, column_config=None):
    try:
        return st.data_editor(df, column_config=column_config, num_rows="dynamic", use_container_width=True)
    except Exception:
        try:
            return st.experimental_data_editor(df, column_config=column_config, num_rows="dynamic", use_container_width=True)
        except Exception:
            st.warning("Interactive editor not available in this Streamlit version — showing read-only table.")
            st.dataframe(df, use_container_width=True)
            return df

def extract_text_from_docx_bytes(content_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content_bytes)) as z:
            xml_content = z.read("word/document.xml")
        tree = ET.fromstring(xml_content)
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []
        for par in tree.findall(".//w:p", namespace):
            texts = [t.text for t in par.findall(".//w:t", namespace) if t.text]
            if texts:
                paragraphs.append("".join(texts))
        return "\n".join(paragraphs)
    except Exception:
        return ""

def extract_text_from_pdf_bytes(content_bytes: bytes) -> (str, str):
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(pages), ""
    except Exception:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(content_bytes))
            pages = [p.extract_text() or "" for p in reader.pages]
            return "\n".join(pages), ""
        except Exception:
            return "", "PDF parsing requires pdfplumber or PyPDF2. Upload DOCX/TXT instead."

def extract_text_from_uploaded_file(uploaded_file) -> (str, str):
    name = uploaded_file.name.lower()
    content = uploaded_file.read()
    if name.endswith(".docx"):
        txt = extract_text_from_docx_bytes(content)
        return (txt, "" if txt.strip() else "Unable to extract text from DOCX.")
    elif name.endswith(".pdf"):
        return extract_text_from_pdf_bytes(content)
    elif name.endswith(".txt"):
        try:
            return content.decode("utf-8", errors="ignore"), ""
        except Exception:
            return "", "Failed to decode TXT file."
    else:
        return "", "Unsupported file type. Please upload DOCX, PDF, or TXT."

def extract_kpis_from_text(text: str) -> pd.DataFrame:
    t = text.lower()
    kpis = []
    def add(name, desc, target):
        kpis.append([name, desc, target, "Extracted"])

    if "drop-off" in t or "drop offs" in t:
        add("Application Drop-off Rate", "Percentage of candidates abandoning application", "Reduce")
    if "time-to-fill" in t or "time to fill" in t:
        add("Time-to-Fill", "Average days from requisition to offer", "< 30 days")
    if "candidate satisfaction" in t or "candidate experience" in t:
        add("Candidate Satisfaction Score", "Candidate survey rating", "> 8/10")
    if "automation" in t or "automate" in t:
        add("Automation Rate", "Percentage of workflows automated", "> 80%")
    if "1000 requisitions" in t:
        add("Requisition Throughput", "No. of requisitions handled per day", "1000/day")
    if "uptime" in t or "availability" in t:
        add("System Uptime", "Service availability percentage", "> 99%")
    if "recruiter productivity" in t or "productivity" in t:
        add("Recruiter Productivity", "Avg. requisitions closed per recruiter", "Increase")
    if "integration" in t or "integrat" in t:
        add("Integration Success Rate", "Percent integrations working without manual intervention", "> 95%")

    if not kpis:
        return pd.DataFrame(columns=["KPI Name", "Description", "Target Value", "Status"])

    df = pd.DataFrame(kpis, columns=["KPI Name", "Description", "Target Value", "Status"])
    return df.drop_duplicates(subset=["KPI Name"]).reset_index(drop=True)

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
            st.rerun()

    st.markdown("---")

    # Pages
    if st.session_state.active_tab == "Dashboard":
        st.subheader("📊 Main Dashboard")
        st.info("This is a placeholder for the Dashboard page.")

    elif st.session_state.active_tab == "KPI Recommender":
        st.subheader("🤖 KPI Recommender")

        uploaded_file = st.file_uploader("📂 Upload BRD (DOCX, PDF, TXT)", type=["docx", "pdf", "txt"])

        if uploaded_file and st.button("Process BRD File"):
            with st.spinner("Extracting KPIs..."):
                text, err = extract_text_from_uploaded_file(uploaded_file)
            if err:
                st.error(err)
            else:
                st.session_state.extracted_kpis = extract_kpis_from_text(text)
                recommended = []
                for _, row in st.session_state.extracted_kpis.iterrows():
                    recommended.append([row["KPI Name"], "Talent Acquisition / IT", row["Target Value"], "Recommended"])
                st.session_state.recommended_kpis = pd.DataFrame(
                    recommended, columns=["KPI Name", "Owner/ SME", "Target Value", "Status"]
                )
                st.success("✅ KPIs extracted successfully!")

        # ---- Always show Extracted KPIs ----
        st.subheader("📊 Preview Extracted Goals & KPIs")
        if st.session_state.extracted_kpis.empty:
            st.info("No KPIs yet. Showing a sample row.")
            st.session_state.extracted_kpis = pd.DataFrame(
                [["Application Drop-off Rate", "Percentage of candidates abandoning application", "Reduce", "Extracted"]],
                columns=["KPI Name", "Description", "Target Value", "Status"]
            )

        try:
            col_cfg = {
                "Status": st.column_config.SelectboxColumn(
                    "Status", options=["Extracted", "Accepted", "Rejected", "Validated"]
                )
            }
        except Exception:
            col_cfg = None

        edited_extracted = safe_data_editor(st.session_state.extracted_kpis, column_config=col_cfg)
        if st.button("✅ Review and Accept Extracted KPIs"):
            st.session_state.extracted_kpis = edited_extracted.copy()
            st.success("Extracted KPIs updated!")

        st.dataframe(st.session_state.extracted_kpis.style.applymap(color_status, subset=["Status"]), use_container_width=True)

        # ---- Always show Recommended KPIs ----
        st.subheader("🔎 Extracted & Recommended KPIs")
        if st.session_state.recommended_kpis.empty:
            st.info("No recommended KPIs yet. Showing a sample row.")
            st.session_state.recommended_kpis = pd.DataFrame(
                [["Application Drop-off Rate", "Talent Acquisition / IT", "Reduce", "Recommended"]],
                columns=["KPI Name", "Owner/ SME", "Target Value", "Status"]
            )

        try:
            col_cfg_rec = {
                "Status": st.column_config.SelectboxColumn(
                    "Status", options=["Extracted", "Accepted", "Rejected", "Validated", "Recommended"]
                )
            }
        except Exception:
            col_cfg_rec = None

        edited_recommended = safe_data_editor(st.session_state.recommended_kpis, column_config=col_cfg_rec)
        if st.button("🔒 Validate Recommended KPIs"):
            st.session_state.recommended_kpis = edited_recommended.copy()
            st.success("Recommended KPIs updated!")

        st.dataframe(st.session_state.recommended_kpis.style.applymap(color_status, subset=["Status"]), use_container_width=True)

    elif st.session_state.active_tab == "JIRA":
        st.subheader("📌 JIRA Integration & Task Management")
        st.info("This is a placeholder for JIRA-related dashboards and tasks.")

    elif st.session_state.active_tab == "AI Insights":
        st.subheader("📈 AI Insights & Reporting")
        st.info("This is a placeholder for AI-driven insights & reports.")
