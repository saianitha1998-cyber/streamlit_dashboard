# app.py
import streamlit as st
import pandas as pd
import io
import zipfile
import xml.etree.ElementTree as ET
import re

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

# ---- Helper: color mapping for statuses (used in styled preview) ----
def color_status(val):
    color_map = {
        "Validated": "background-color: #d4edda; color: #155724; font-weight:bold;",   # Green
        "Rejected": "background-color: #f8d7da; color: #721c24; font-weight:bold;",   # Red
        "Recommended": "background-color: #cce5ff; color: #004085; font-weight:bold;", # Blue
        "Accepted": "background-color: #fff3cd; color: #856404; font-weight:bold;",   # Yellow
        "Extracted": "background-color: #e2e3e5; color: #383d41; font-weight:bold;"   # Grey
    }
    return color_map.get(val, "")

# ---- Helper: safe data_editor wrapper (fall back if API differs) ----
def safe_data_editor(df, column_config=None):
    try:
        # Primary (newer Streamlit)
        if column_config:
            return st.data_editor(df, column_config=column_config, num_rows="dynamic", use_container_width=True)
        else:
            return st.data_editor(df, num_rows="dynamic", use_container_width=True)
    except Exception:
        try:
            # Older experimental API fallback
            if column_config:
                return st.experimental_data_editor(df, num_rows="dynamic", use_container_width=True)
            else:
                return st.experimental_data_editor(df, num_rows="dynamic", use_container_width=True)
        except Exception:
            # As last resort, show static dataframe and return it (no edits)
            st.warning("Interactive editor not available in this Streamlit version — showing read-only table.")
            st.dataframe(df, use_container_width=True)
            return df

# ---- Helper: docx text extraction using stdlib (no external package) ----
def extract_text_from_docx_bytes(content_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content_bytes)) as z:
            xml_content = z.read("word/document.xml")
    except Exception:
        return ""
    # parse XML and extract text from w:t elements
    try:
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

# ---- Helper: PDF extraction (optional external libs) ----
def extract_text_from_pdf_bytes(content_bytes: bytes) -> (str, str):
    """
    Attempts to extract PDF text using pdfplumber or PyPDF2 if installed.
    Returns (text, error_message). If both are missing or extraction fails, text="" and error_message set.
    """
    # try pdfplumber first
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n".join(pages), ""
    except Exception:
        # try PyPDF2
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(content_bytes))
            pages = []
            for p in reader.pages:
                txt = ""
                try:
                    txt = p.extract_text() or ""
                except Exception:
                    txt = ""
                pages.append(txt)
            return "\n".join(pages), ""
        except Exception:
            err = (
                "PDF parsing requires either 'pdfplumber' or 'PyPDF2' installed in the environment. "
                "You can either: upload a DOCX or TXT BRD, or install pdfplumber (recommended) via "
                "`pip install pdfplumber` in your environment."
            )
            return "", err

# ---- Unified extractor for uploaded files ----
def extract_text_from_uploaded_file(uploaded_file) -> (str, str):
    """
    Returns (text, error_msg). If successful, error_msg == "".
    """
    name = uploaded_file.name.lower()
    content = uploaded_file.read()  # bytes
    # Reset file pointer not necessary; we consumed it with .read()
    if name.endswith(".docx"):
        txt = extract_text_from_docx_bytes(content)
        if not txt.strip():
            return "", "Unable to extract text from DOCX (maybe the document is corrupted)."
        return txt, ""
    elif name.endswith(".pdf"):
        txt, err = extract_text_from_pdf_bytes(content)
        if err:
            return "", err
        if not txt.strip():
            return "", "No extractable text found in PDF."
        return txt, ""
    elif name.endswith(".txt"):
        try:
            return content.decode("utf-8", errors="ignore"), ""
        except Exception:
            return "", "Failed to decode TXT file."
    else:
        return "", "Unsupported file type. Please upload DOCX, PDF or TXT."

# ---- KPI extraction logic (keyword / pattern based) ----
def extract_kpis_from_text(text: str) -> pd.DataFrame:
    t = text.lower()
    kpis = []
    def add(name, desc, target):
        kpis.append([name, desc, target, "Extracted"])
    # Patterns / keywords derived from typical BRD pieces (customise as needed)
    if re.search(r"drop[\s-]?offs?|drop[\s-]?off", t):
        add("Application Drop-off Rate", "Percentage of candidates abandoning applications", "Reduce")
    if re.search(r"time[\s-]?to[\s-]?fill|time[- ]to[- ]fill", t):
        add("Time-to-Fill", "Average days from requisition to offer", "< 30 days")
    if "candidate satisfaction" in t or "candidate experience" in t or "satisfaction score" in t:
        add("Candidate Satisfaction Score", "Candidate survey rating", "> 8/10")
    if "automation" in t or "automate" in t:
        add("Automation Rate", "Percentage of workflows automated", "> 80%")
    if re.search(r"\b1000\b.*requisition|1000 requisition", t):
        add("Requisition Throughput", "No. of requisitions handled per day", "1000/day")
    if "uptime" in t or "availability" in t:
        add("System Uptime", "Service availability percentage", "> 99%")
    if "recruiter productivity" in t or "productivity" in t:
        add("Recruiter Productivity", "Avg. requisitions closed per recruiter", "Increase")
    if "integration" in t or "integrat" in t:
        add("Integration Success Rate", "Percent integrations working without manual intervention", "> 95%")
    # If no KPIs found, try to find lines under headings like "Success Criteria" or "Measurement"
    if not kpis:
        # naive attempt: split lines, find lines containing keywords and convert
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for ln in lines:
            if any(word in ln.lower() for word in ("success", "measure", "kpi", "drop", "time-to-fill", "satisfaction", "uptime", "automation")):
                # create small heuristic KPI from line
                shortened = ln if len(ln) < 80 else ln[:80] + "..."
                add("Inferred KPI", shortened, "-")
                if len(kpis) >= 6:
                    break
    # Deduplicate by KPI Name
    if kpis:
        df = pd.DataFrame(kpis, columns=["KPI Name", "Description", "Target Value", "Status"])
        df = df.drop_duplicates(subset=["KPI Name"])
        return df.reset_index(drop=True)
    else:
        return pd.DataFrame(columns=["KPI Name", "Description", "Target Value", "Status"])

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
    # ---- NAVBAR (simple) ----
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

    # ---- Pages ----
    if st.session_state.active_tab == "Dashboard":
        st.subheader("📊 Main Dashboard")
        st.info("This is a placeholder for the **Dashboard** page.")

    elif st.session_state.active_tab == "KPI Recommender":
        st.subheader("🤖 KPI Recommender")

        # ---- File Upload ----
        uploaded_file = st.file_uploader(
            "📂 Upload BRD (DOCX, PDF, TXT). DOCX preferred (no extra packages required).",
            type=["docx", "pdf", "txt"]
        )
        if uploaded_file:
            # Process when button clicked
            if st.button("Process BRD File"):
                with st.spinner("Extracting text from BRD..."):
                    text, err = extract_text_from_uploaded_file(uploaded_file)
                if err:
                    st.error(err)
                else:
                    # extract KPIs
                    df_extracted = extract_kpis_from_text(text)
                    if df_extracted.empty:
                        st.info("No clear KPIs found automatically. You can edit or add rows in the editor below.")
                    st.session_state.extracted_kpis = df_extracted.copy()

                    # create recommended table mapping owners heuristically
                    recommended = []
                    for _, row in df_extracted.iterrows():
                        # heuristic owner: TA / IT for ATS project
                        recommended.append([row["KPI Name"], "Talent Acquisition / IT", row["Target Value"], "Recommended"])
                    if recommended:
                        st.session_state.recommended_kpis = pd.DataFrame(recommended, columns=["KPI Name", "Owner/ SME", "Target Value", "Status"])
                    else:
                        st.session_state.recommended_kpis = pd.DataFrame(columns=["KPI Name", "Owner/ SME", "Target Value", "Status"])

                    st.success("✅ KPIs extracted and tables populated. Edit as needed below.")

        # ---- Extracted KPIs (editor + styled preview) ----
        st.subheader("📊 Preview Extracted Goals & KPIs")
        if st.session_state.extracted_kpis.empty:
            # Keep a helpful example row so editor is not empty
            sample = [
                ["Application Drop-off Rate", "Percentage of candidates abandoning applications", "Reduce", "Extracted"]
            ]
            st.session_state.extracted_kp
