import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prospectra Dashboard", layout="wide")

# ---- Mock credentials ----
USER_CREDENTIALS = {
    "admin": "admin123",
    "user": "user123"
}

# ---- Session state to store login ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

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
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

else:
    # ---- NAVBAR STYLING ----
    st.markdown("""
        <style>
        .nav-tabs {
            display: flex;
            justify-content: flex-start;
            gap: 30px;
            font-size: 18px;
            margin-bottom: 20px;
        }
        .nav-item {
            cursor: pointer;
            padding-bottom: 5px;
            color: #333333;
            font-weight: 500;
        }
        .nav-item:hover {
            color: #d00000;
        }
        .active-tab {
            border-bottom: 3px solid #d00000;
            font-weight: 700;
            color: #d00000;
        }
        </style>
    """, unsafe_allow_html=True)

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Dashboard"

    # ---- Navbar UI ----
    tabs_html = f"""
    <div class="nav-tabs">
        <div class="nav-item {'active-tab' if st.session_state.active_tab=='Dashboard' else ''}" 
            onclick="window.location.href='/?tab=Dashboard'">Dashboard</div>
        <div class="nav-item {'active-tab' if st.session_state.active_tab=='KPI Recommender' else ''}" 
            onclick="window.location.href='/?tab=KPI Recommender'">KPI Recommender</div>
        <div class="nav-item {'active-tab' if st.session_state.active_tab=='JIRA' else ''}" 
            onclick="window.location.href='/?tab=JIRA'">JIRA Integration & Task Management</div>
        <div class="nav-item {'active-tab' if
