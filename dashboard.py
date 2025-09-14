import streamlit as st
import pandas as pd
from io import BytesIO

# Correct imports for docx and PDF
import docx
import PyPDF2

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
if "extracted" not in st.session_state:
    st.session_state.extracted = pd.DataFrame()
if "recommended" not in st.session_state:
    st.session_state.recommended = pd.DataFrame()
if "preview_actions" not in st.session_state:
    st.session_state.preview_actions = {}  # Accept/Reject selections
if "final_kpis" not in st.session_state:
    st.session_state.final_kpis = pd.DataFrame()


# ---- Badge Renderer ----
def render_status_badge(status: str) -> str:
    colors = {
        "Extracted": "#007bff",
        "Validated": "#28a745",
        "Rejected": "#dc3545",
        "Recommended": "#17a2b8",
        "Accepted": "#ffc107",
    }
    color = colors.get(status, "#6c757d")
    return f"<span style='background-color:{color}; color:white; padding:3px 8px; border-radius:10px; font-size:13px;'>{status}</span>"


# ---- Function to read KPI from uploaded file ----
def extract_kpis_from_file(uploaded_file):
    kpi_list = []
    text_content = ""

    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        text_content = "\n".join([p.text for p in doc.paragraphs])
    elif uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        text_content = "\n".join([page.extract_text() for page in reader.pages])
    elif uploaded_file.type == "text/plain":
        text_content = str(uploaded_file.read(), 'utf-8')
    else:
        st.error("Unsupported file type!")
        return pd.DataFrame()

    # Simple parsing: assume each KPI line contains "KPI" keyword
    lines = [line.strip() for line in text_content.split("\n") if line.strip()]
    for line in lines:
        if ":" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                kpi_name = parts[0].strip()
                desc = parts[1].strip()
                kpi_list.append([kpi_name, desc, "-", "Extracted"])

    if not kpi_list:
        # Fallback if no ":" found
        for line in lines:
            kpi_list.append([line[:30], line, "-", "Extracted"])  # name first 30 chars

    return pd.DataFrame(kpi_list, columns=["KPI Name", "Description", "Target Value", "Status"])


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
            st.session_state.extracted = pd.DataFrame()
            st.session_state.recommended = pd.DataFrame()
            st.session_state.preview_actions = {}
            st.session_state.final_kpis = pd.DataFrame()
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
            st.session_state.brd_uploaded = True
            st.session_state.review_done = False
            st.session_state.preview_actions = {}
            st.session_state.final_kpis = pd.DataFrame()

            # Extract KPIs dynamically from file
            st.session_state.extracted = extract_kpis_from_file(uploaded_file)

            # Mock recommended KPIs
            st.session_state.recommended = pd.DataFrame([
                ["Involuntary Attrition", "HR BP 2", "-", "Recommended"],
                ["Absenteeism Rate", "HR BP 4", "-", "Recommended"],
                ["Time to Fill", "HR BP 1", "-", "Recommended"],
            ], columns=["KPI Name", "Owner/ SME", "Target Value", "Status"])

        # ---- Step 1: Preview Extracted ----
        if st.session_state.brd_uploaded:
            st.markdown("### 📊 Preview Extracted Goals & KPIs")
            st.caption("Decide Accept/Reject here. Status remains 'Extracted' until you confirm.")

            header_cols = st.columns([3, 5, 2, 2, 3])
            headers = ["KPI Name", "Description", "Target Value", "Status", "Actions"]
            for col, h in zip(header_cols, headers):
                col.markdown(f"**{h}**")

            for i, row in st.session_state.extracted.iterrows():
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
                # Transfer preview decisions into final_kpis
                extracted_with_status = []
                for i, row in st.session_state.extracted.iterrows():
                    status = st.session_state.preview_actions.get(i, "Extracted")
                    extracted_with_status.append([row["KPI Name"], "HR BP ?", row["Target Value"], status])

                df_preview = pd.DataFrame(
                    extracted_with_status,
                    columns=["KPI Name", "Owner/ SME", "Target Value", "Status"]
                )

                # Merge with recommended KPIs
                df_all = pd.concat([df_preview, st.session_state.recommended], ignore_index=True)
                st.session_state.final_kpis = df_all
                st.session_state.review_done = True
                st.rerun()

        # ---- Step 2: Extracted & Recommended KPIs ----
        if st.session_state.review_done:
            st.markdown("---")
            st.markdown("### 🔎 Extracted & Recommended KPIs")
            st.caption("Preview decisions are final. Recommended KPIs still require action.")

            df_all = st.session_state.final_kpis.copy()
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
                        cols[4].markdown(f"🔍 Review Details: **{row['Status']}**")
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

            st.button("🔒 Review Details", use_container_width=True)
