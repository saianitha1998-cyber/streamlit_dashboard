import streamlit as st
import pandas as pd

st.set_page_config(page_title="KPI Recommender", layout="wide")

# ---------- CUSTOM STYLES ----------
st.markdown("""
    <style>
        .card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #fff;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.05);
        }
        .status-extracted {background:#e7f1fb;color:#0056b3;font-weight:bold;padding:4px 8px;border-radius:6px;}
        .status-validated {background:#d4edda;color:#155724;font-weight:bold;padding:4px 8px;border-radius:6px;}
        .status-recommended {background:#e2f7e2;color:#0a530a;font-weight:bold;padding:4px 8px;border-radius:6px;}
        .status-rejected {background:#f8d7da;color:#721c24;font-weight:bold;padding:4px 8px;border-radius:6px;}
        table td, table th {padding: 8px; text-align: left;}
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("📊 KPI Recommender")

# ---------- FILE UPLOAD ----------
st.subheader("Upload Business Requirements Document (BRD)")

col1, col2 = st.columns([3, 2])
with col1:
    uploaded_file = st.file_uploader("Drag & drop files here, or click to browse", type=["pdf", "doc", "docx", "txt"])
with col2:
    st.info("Easily upload BRDs to extract and track key performance metrics for your work initiatives.")
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
    if st.button("Process Uploaded File"):
        st.write("🔄 Processing file... (AI extraction simulation)")

st.write("---")

# ---------- PREVIEW EXTRACTED GOALS & KPIs ----------
st.subheader("Preview Extracted Goals & KPIs")

preview_data = pd.DataFrame({
    "KPI Name": ["Employee Turnover Rate", "Employee Satisfaction Score", "Employee Retention Rate (1 YR)"],
    "Description": [
        "Percentage of employees leaving the company within a year.",
        "Average score from quarterly employee surveys.",
        "Percentage of employees remaining after 12 months."
    ],
    "Target Value": ["< 15%", "> 8.0/10", "> 85%"],
    "Status": ["Extracted", "Extracted", "Extracted"],
    "Actions": ["Review", "Review", "Review"]
})

st.dataframe(preview_data, use_container_width=True)

if st.button("Review and Accept"):
    st.success("✅ KPIs Accepted")

st.write("---")

# ---------- EXTRACTED & RECOMMENDED KPIs ----------
st.subheader("Extracted & Recommended KPIs")

kpi_data = pd.DataFrame({
    "KPI Name": [
        "Employee Turnover Rate",
        "Employee Satisfaction Score",
        "Employee Retention Rate (1 YR)",
        "Involuntary Attrition",
        "Absenteeism Rate",
        "Time to Fill"
    ],
    "Owner/ SME": ["HR BP 1", "HR BP 3", "HR BP 3", "HR BP 2", "HR BP 4", "HR BP 1"],
    "Target Value": ["< 15%", "> 8.0/10", "> 85%", "-", "-", "-"],
    "Status": ["Rejected", "Validated", "Extracted", "Recommended", "Recommended", "Rejected"],
    "Actions": ["Review Details", "Review Details", "Review Details", "Review Details", "Review Details", "Review Details"]
})

# Display with styling
st.dataframe(kpi_data, use_container_width=True)

if st.button("Validate"):
    st.success("✅ Selected KPIs Validated")
