import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prospectra Dashboard", layout="wide")

# ---- Mock credentials ----
USER_CREDENTIALS = {"admin": "admin123", "user": "user123"}

# ---- Session state defaults ----
for key, value in {
    "logged_in": False,
    "username": "",
    "active_tab": "Dashboard",
    "brd_uploaded": False,
    "review_done": False,
    "extracted": pd.DataFrame(),
    "recommended": pd.DataFrame(),
    "preview_actions": {},
    "final_kpis": pd.DataFrame()
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
    # ---- Navbar with Tabs, Home, Search, Notifications ----
    nav_left, nav_center, nav_right = st.columns([2, 6, 2])

    # Home button
    with nav_left:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.active_tab = "Dashboard"
            st.rerun()

    # Tabs and Search
    with nav_center:
        st.markdown(
            """
            <div style="display:flex; align-items:center; justify-content:center; gap:10px;">
                <img src="https://i.ibb.co/h8rjN50/prospectra-icon.png" width="40">
                <h3 style="margin:0; color:#d00000;">Prospectra</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
        search_query = st.text_input("🔍 Search...", key="search_box")

    # Notifications and Logout
    with nav_right:
        if st.button("🔔 Notifications", use_container_width=True):
            st.info("You have new notifications!")
        if st.button("Logout", use_container_width=True):
            for key in ["logged_in","username","brd_uploaded","review_done","extracted","recommended","preview_actions","final_kpis"]:
                st.session_state[key] = False if isinstance(st.session_state[key], bool) else pd.DataFrame() if isinstance(st.session_state[key], pd.DataFrame) else {}
            st.rerun()

    st.markdown("---")

    # ---- Sidebar Tabs ----
    tabs = ["Dashboard", "KPI Recommender", "JIRA / Task Management", "AI Insights & Reporting"]
    tab_cols = st.columns(len(tabs))
    for i, tab in enumerate(tabs):
        if tab_cols[i].button(tab, use_container_width=True):
            st.session_state.active_tab = tab
            st.rerun()

    st.markdown("---")

    # ---- Render Pages Based on Tab ----
    active_tab = st.session_state.active_tab

    if active_tab == "Dashboard":
        st.header("📊 Dashboard")
        st.info("This is the main dashboard overview. KPIs, charts, and summary metrics will appear here.")

    elif active_tab == "KPI Recommender":
        st.header("🤖 KPI Recommender")

        # ---- Upload BRD (mocked) ----
        uploaded_file = st.file_uploader(
            "📂 Upload Business Requirements Document (BRD)",
            type=["docx", "pdf", "txt"]
        )

        if uploaded_file and st.button("Process Uploaded File"):
            st.session_state.brd_uploaded = True
            st.session_state.review_done = False
            st.session_state.preview_actions = {}
            st.session_state.final_kpis = pd.DataFrame()

            # ---- Mock extracted KPIs ----
            st.session_state.extracted = pd.DataFrame([
                ["Employee Turnover Rate", "Percentage leaving within a year.", "< 15%", "Extracted"],
                ["Employee Satisfaction Score", "Average quarterly survey score.", "> 8.0/10", "Extracted"],
                ["Employee Retention Rate (1 YR)", "Employees staying after 12 months.", "> 85%", "Extracted"],
            ], columns=["KPI Name", "Description", "Target Value", "Status"])

            # ---- Mock recommended KPIs ----
            st.session_state.recommended = pd.DataFrame([
                ["Involuntary Attrition", "HR BP 2", "-", "Recommended"],
                ["Absenteeism Rate", "HR BP 4", "-", "Recommended"],
                ["Time to Fill", "HR BP 1", "-", "Recommended"],
            ], columns=["KPI Name", "Owner/ SME", "Target Value", "Status"])

        # ---- Step 1: Preview Extracted ----
        if st.session_state.brd_uploaded:
            st.subheader("📊 Preview Extracted Goals & KPIs")
            st.caption("Decide Accept/Reject here. Status remains 'Extracted' until you confirm.")

            df_preview = st.session_state.extracted.copy()
            if search_query:
                df_preview = df_preview[df_preview["KPI Name"].str.contains(search_query, case=False)]

            header_cols = st.columns([3,5,2,2,3])
            for col, h in zip(header_cols, ["KPI Name","Description","Target Value","Status","Actions"]):
                col.markdown(f"**{h}**")

            for i, row in df_preview.iterrows():
                cols = st.columns([3,5,2,2,3])
                cols[0].write(row["KPI Name"])
                cols[1].write(row["Description"])
                cols[2].write(row["Target Value"])
                cols[3].markdown(render_status_badge("Extracted"), unsafe_allow_html=True)

                with cols[4]:
                    c1, c2 = st.columns([1,1])
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
                for i, row in st.session_state.extracted.iterrows():
                    status = st.session_state.preview_actions.get(i, "Extracted")
                    extracted_with_status.append([row["KPI Name"], "HR BP ?", row["Target Value"], status])

                df_all = pd.concat([pd.DataFrame(extracted_with_status, columns=["KPI Name","Owner/ SME","Target Value","Status"]),
                                    st.session_state.recommended], ignore_index=True)
                st.session_state.final_kpis = df_all
                st.session_state.review_done = True
                st.rerun()

        # ---- Step 2: Final KPIs ----
        if st.session_state.review_done:
            st.subheader("🔎 Extracted & Recommended KPIs")
            st.caption("Preview decisions are final. Recommended KPIs still require action.")

            df_all = st.session_state.final_kpis.copy()
            if search_query:
                df_all = df_all[df_all["KPI Name"].str.contains(search_query, case=False)]

            header_cols = st.columns([3,3,2,2,3])
            for col, h in zip(header_cols, ["KPI Name","Owner/ SME","Target Value","Status","Actions"]):
                col.markdown(f"**{h}**")

            for i, row in df_all.iterrows():
                cols = st.columns([3,3,2,2,3])
                cols[0].write(row["KPI Name"])
                cols[1].write(row["Owner/ SME"])
                cols[2].write(row["Target Value"])
                cols[3].markdown(render_status_badge(row["Status"]), unsafe_allow_html=True)

                with cols[4]:
                    if row["Status"] in ["Accepted","Rejected"]:
                        cols[4].markdown(f"🔍 Review Details: **{row['Status']}**")
                    else:
                        c1,c2 = st.columns([1,1])
                        if c1.button("✔️ Validate", key=f"validate_final_{i}"):
                            df_all.at[i,"Status"] = "Validated"
                            st.session_state.final_kpis = df_all
                            st.rerun()
                        if c2.button("❌ Reject", key=f"reject_final_{i}"):
                            df_all.at[i,"Status"] = "Rejected"
                            st.session_state.final_kpis = df_all
                            st.rerun()

            st.button("🔒 Review Details", use_container_width=True)

    elif active_tab == "JIRA / Task Management":
        st.header("📝 JIRA / Task Management")
        st.info("Integration with JIRA and task tracking will be available here.")

    elif active_tab == "AI Insights & Reporting":
        st.header("🤖 AI Insights & Reporting")
        st.info("AI-based insights, analytics, and reporting dashboards will appear here.")
