import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prospectra Dashboard", layout="wide")

# ---- HEADER ----
st.markdown("""
    <style>
        .main-header {
            font-size:28px;
            font-weight:bold;
            color:#8B0000;
        }
        .status-green {color:green; font-weight:bold;}
        .status-yellow {color:orange; font-weight:bold;}
        .status-red {color:red; font-weight:bold;}
        .card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background-color: #fff;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>📊 Prospectra - Dashboard</div>", unsafe_allow_html=True)

# ---- SEARCH + FILTERS ----
col1, col2, col3, col4, col5 = st.columns([3,2,2,2,2])
with col1: st.text_input("Global Search...")
with col2: st.selectbox("Department", ["All","HR","Finance","IT","Product"])
with col3: st.selectbox("Owner", ["All","John","Mary","David"])
with col4: st.selectbox("Timeline", ["All","Q1","Q2","Q3","Q4"])
with col5: st.selectbox("Status", ["All","On Track","At Risk","Behind Schedule"])

st.write("---")

# ---- ACTIVE PROJECTS ----
st.subheader("Active Projects (25)")

projects = [
    {"title":"Attrition and Retention Analysis","dept":"Employee Experience","completion":34,"status":"On Track","desc":"Analyzing why employees leave (attrition) and why they stay (retention)."},
    {"title":"New Feature Development","dept":"Product Development","completion":60,"status":"At Risk","desc":"Identify and address blocker tasks in sprint 3. Reallocate resources."},
    {"title":"IT Infrastructure Upgrade","dept":"IT Operations","completion":40,"status":"Behind Schedule","desc":"Deep-dive analysis of recent delays. Urgent issue resolution required."},
    {"title":"Talent Acquisition Initiative","dept":"Human Resources","completion":75,"status":"On Track","desc":"Leverage LinkedIn Sales Navigator for outreach to passive candidates."},
    {"title":"Financial Audit & Reporting","dept":"Finance","completion":80,"status":"At Risk","desc":"Prioritize reconciliation of outstanding discrepancies in audit reports."}
]

cols = st.columns(3)
for i, project in enumerate(projects):
    with cols[i % 3]:
        color = "status-green" if project["status"]=="On Track" else "status-yellow" if project["status"]=="At Risk" else "status-red"
        st.markdown(f"""
            <div class='card'>
                <h4>{project['title']}</h4>
                <b>{project['dept']}</b><br>
                Completion: {project['completion']}%<br>
                Status: <span class='{color}'>{project['status']}</span><br><br>
                {project['desc']}
            </div>
        """, unsafe_allow_html=True)

st.write("---")

# ---- KEY INSIGHTS ----
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='card'><h4>Risks Identified</h4>"
                "<ul><li>IT team facing workload delays</li>"
                "<li>Feature X over budget by 10%</li>"
                "<li>Marketing campaign underperforming</li></ul>"
                "</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'><h4>AI Recommendations</h4>"
                "<ul><li>Projects 'At Risk' need stakeholder sync + daily quick-check</li>"
                "<li>Forecast positive impact of 1.2M USD from Q3 campaign</li></ul>"
                "</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='card'><h4>Overall Project Summary</h4>"
                "Total Projects: <b>25</b><br>"
                "✅ On Track: <b>18</b><br>"
                "⚠️ At Risk: <b>05</b><br>"
                "⏳ Behind Schedule: <b>01</b><br>"
                "</div>", unsafe_allow_html=True)
