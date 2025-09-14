import streamlit as st
import pandas as pd
import docx
import PyPDF2

st.set_page_config(page_title="Prospectra Dashboard", layout="wide")

# ---- Helpers ----
def read_docx(file):
    doc = docx.Document(file)
    text = []
    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text.strip())
    return text

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = []
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            text.extend(content.split("\n"))
    return text

def read_txt(file):
    return file.read().decode("utf-8").splitlines()

def extract_kpis_from_text(lines):
    """Very basic KPI extractor from text lines"""
    kpis = []
    for line in lines:
        if "kpi" in line.lower() or "goal" in line.lower():
            parts = line.split(":")
            if len(parts) > 1:
                kpi_name = parts[0].strip()
                desc = parts[1].strip()
            else:
                kpi_name = line.strip()
                desc = "No description available"
            kpis.append([kpi_name, desc, "-", "Extracted"])
    # fallback: take first 5 non-empty lines if no KPI markers
    if not kpis:
        for i, line in enumerate(lines[:5]):
            kpis.append([f"KPI {i+1}", line, "-", "Extracted"])
    return pd.DataFrame(kpis, columns=["KPI Name", "Description", "Target Value", "Status"])

# ---- Mock credentials ----
USER_CREDENTIALS = {"admin": "admin123", "user": "user123"}

# ---- Session State ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "brd_uploaded" not in st.session_state:
    st.session_state.brd_uploaded = False
if "review_done" not in st.session_state:
    st.session_state.review_done = False
if "preview_actions" not in st.session_state:
    st.session_state.preview_actions = {}
if "final_kpis" not in st.session_state:
    st.session_state.final_kpis = pd.DataFrame()

# ---- Badge Renderer ----
def render_status_badge(status: str) -> str:
    colors = {
        "Extracted": "#007bff",     # Blue
        "Validated": "#28a745",     # Green
        "Rejected": "#dc3545",      # Red
        "Recommended": "#17a2b8",   # Cyan
        "Accepted": "#ffc107",      # Yellow,
    }
    color = colors.get(status, "#6c757d")
    return f"<span style='background-color:{color}; color:white; padding:3px 8px; border-radius:10px; font-size:13px;'>{status}</span>"

# ---- Login Page ----
if not st.session_state.logged_in:
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

else:
    st.subheader("🤖 KPI Recommender")

    uploaded_file = st.file_uploader("📂 Upload BRD (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

    if uploaded_file and st.button("Process Uploaded File"):
        # Extract text depending on file type
        if uploaded_file.name.endswith(".docx"):
            lines = read_docx(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            lines = read_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            lines = read_txt(uploaded_file)
        else:
            st.error("Unsupported file type")
            lines = []

        # Extract KPIs
        df_extracted = extract_kpis_from_text(lines)

        st.session_state.extracted = df_extracted
        st.session_state.brd_uploaded = True
        st.session_state.review_done = False
        st.session_state.preview_actions = {}
        st.session_state.final_kpis = pd.DataFrame()

    # ---- Step 1: Preview Table ----
    if st.session_state.brd_uploaded:
        st.markdown("### 📊 Preview Extracted Goals & KPIs")
        st.caption("Decide Accept/Reject for extracted KPIs. Status = Extracted")

        df_extracted = st.session_state.extracted

        header_cols = st.columns([3, 5, 2, 2, 3])
        headers = ["KPI Name", "Description", "Target Value", "Status", "Actions"]
        for col, h in zip(header_cols, headers):
            col.markdown(f"**{h}**")

        for i, row in df_extracted.iterrows():
            cols = st.columns([3, 5, 2, 2, 3])
            cols[0].write(row["KPI Name"])
            cols[1].write(row["Description"])
            cols[2].write(row["Target Value"])
            cols[3].markdown(render_status_badge("Extracted"), unsafe_allow_html=True)

            with cols[4]:
                c1, c2 = st.columns([1, 1])
                if c1.button("✅ Accept", key=f"accept_prev_{i}"):
                    st.session_state.preview_actions[i] = "Accepted"
                    st.rerun()
                if c2.button("❌ Reject", key=f"reject_prev_{i}"):
                    st.session_state.preview_actions[i] = "Rejected"
                    st.rerun()

            if i in st.session_state.preview_actions:
                cols[4].markdown(f"➡️ Selected: **{st.session_state.preview_actions[i]}**")

        if st.button("✅ Review and Accept", use_container_width=True):
            extracted_with_status = []
            for i, row in df_extracted.iterrows():
                status = st.session_state.preview_actions.get(i, "Extracted")
                extracted_with_status.append([row["KPI Name"], "HR BP ?", row["Target Value"], status])

            df_preview = pd.DataFrame(extracted_with_status,
                                      columns=["KPI Name", "Owner/ SME", "Target Value", "Status"])

            # Example recommended KPIs
            df_recommended = pd.DataFrame([
                ["Involuntary Attrition", "HR BP 2", "-", "Recommended"],
                ["Absenteeism Rate", "HR BP 4", "-", "Recommended"],
            ], columns=["KPI Name", "Owner/ SME", "Target Value", "Status"])

            df_all = pd.concat([df_preview, df_recommended], ignore_index=True)

            st.session_state.final_kpis = df_all
            st.session_state.review_done = True
            st.rerun()

    # ---- Step 2: Final Table ----
    if st.session_state.review_done:
        st.markdown("---")
        st.markdown("### 🔎 Extracted & Recommended KPIs")

        df_all = st.session_state.final_kpis

        header_cols = st.columns([3, 3, 2, 2, 3])
        headers = ["KPI Name", "Owner/ SME", "Target Value", "Status", "Actions"]
        for col, h in zip(header_cols, headers):
            col.markdown(f"**{h}**")

        for i, row in df_all.iterrows():
            cols = st.columns([3, 3, 2, 2, 3])
            cols[0].write(row["KPI Name"])
            cols[1].write(row["Owner/ SME"])
            cols[2].write(row["Target Value"])
            cols[3].markdown(render_status_badge(row["Status"]), unsafe_allow_html=True)

            with cols[4]:
                if row["Status"] in ["Accepted", "Rejected"]:
                    cols[4].markdown(f"✔️ Finalized: **{row['Status']}**")
                else:
                    c1, c2 = st.columns([1, 1])
                    if c1.button("✔️ Validate", key=f"validate_final_{i}"):
                        df_all.at[i, "Status"] = "Validated"
                        st.session_state.final_kpis = df_all
                        st.rerun()
                    if c2.button("❌ Reject", key=f"reject_final_{i}"):
                        df_all.at[i, "Status"] = "Rejected"
                        st.session_state.final_kpis = df_all
                        st.rerun()

        st.button("🔒 Finalize Validation", use_container_width=True)
