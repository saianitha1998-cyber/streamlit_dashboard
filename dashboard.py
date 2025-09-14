import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prospectra - KPI Recommender", layout="wide")

# ---- HEADER ----
st.markdown(
    """
    <style>
        .title {font-size:32px; font-weight:600; color:#8B0000;}
        .subtitle {font-size:18px; color:grey;}
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
st.markdown("## 🚀 Prospectra KPI Recommender")
st.write("---")

# ---- FILE UPLOAD ----
st.subheader("📂 Upload Business Requirements Document (BRD)")
uploaded_file = st.file_uploader("Drag & drop or browse (PDF, DOC, DOCX, TXT)", type=["pdf", "doc", "docx", "txt"])

if uploaded_file:
    st.success("✅ File uploaded successfully!")
    if st.button("Process Uploaded File"):
        st.info("🔄 Processing file... (mock example)")

st.write("---")

# ---- PREVIEW EXTRACTED GOALS & KPIs ----
st.subheader("📊 Preview Extracted Goals & KPIs")

data_extracted = [
    ["Employee Turnover Rate", "Percentage of employees leaving within a year.", "< 15%", "Extracted"],
    ["Employee Satisfaction Score", "Average score from quarterly surveys.", "> 8.0/10", "Extracted"],
    ["Employee Retention Rate (1 YR)", "Employees remaining after 12 months.", "> 85%", "Extracted"]
]

df_extracted = pd.DataFrame(data_extracted, columns=["KPI Name", "Description", "Target Value", "Status"])

def render_status(status):
    return f"<span class='status-tag {status}'>{status}</span>"

df_extracted["Status"] = df_extracted["Status"].apply(lambda x: render_status(x))

st.write(
    df_extracted.to_html(escape=False, index=False),
    unsafe_allow_html=True
)

st.button("✅ Review and Accept")

st.write("---")

# ---- RECOMMENDED KPIs ----
st.subheader("🤖 Extracted & Recommended KPIs")

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

st.write(
    df_recommended.to_html(escape=False, index=False),
    unsafe_allow_html=True
)

st.button("🔒 Validate")
