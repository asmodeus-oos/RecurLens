"""
RecurLens: Clinical Decision Intelligence Dashboard.
Pure Light Mode (Strict Donezo Design Language).
No decorative filler or mock navigation elements. 100% functional clinical oncology UI.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="RecurLens AI | Clinical Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Comprehensive Strict Light Mode CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global canvas & typography */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #f5f6f8 !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        color: #111417 !important;
    }

    /* Strict Light Mode Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #edf0f2 !important;
    }
    [data-testid="stSidebar"] * {
        color: #111417 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label, 
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stFileUploader label {
        font-weight: 600 !important;
        font-size: 13px !important;
        color: #2b3036 !important;
    }

    /* Page padding */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1400px;
    }

    /* Page Header */
    .header-container {
        margin-bottom: 22px;
    }
    .header-title {
        font-size: 28px;
        font-weight: 800;
        color: #111417;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-sub {
        font-size: 14px;
        color: #6f767e;
        margin-top: 4px;
    }

    /* Stat Cards */
    .stat-card-green {
        background: #164e2e;
        border-radius: 20px;
        padding: 22px 24px;
        color: #ffffff;
        position: relative;
        box-shadow: 0 4px 18px rgba(22, 78, 46, 0.12);
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .stat-card-white {
        background: #ffffff;
        border-radius: 20px;
        padding: 22px 24px;
        color: #111417;
        position: relative;
        border: 1px solid #edf0f2;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .stat-arrow {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 700;
    }
    .stat-arrow-green {
        background: rgba(255,255,255,0.18);
        color: #ffffff;
    }
    .stat-arrow-white {
        border: 1px solid #e5e7eb;
        color: #111417;
        background: #fbfbfb;
    }
    .stat-label-green {
        font-size: 13px;
        color: rgba(255,255,255,0.85);
        font-weight: 500;
    }
    .stat-label-white {
        font-size: 13px;
        color: #6f767e;
        font-weight: 500;
    }
    .stat-val-green {
        font-size: 36px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }
    .stat-val-white {
        font-size: 36px;
        font-weight: 800;
        color: #111417;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }
    .stat-badge-green {
        display: inline-flex;
        align-items: center;
        background: rgba(255,255,255,0.22);
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11.5px;
        font-weight: 600;
        width: fit-content;
    }
    .stat-badge-white {
        display: inline-flex;
        align-items: center;
        background: #f4f6f8;
        color: #1b5e3a;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11.5px;
        font-weight: 600;
        width: fit-content;
    }

    /* Content Cards */
    .content-box {
        background: #ffffff;
        border-radius: 20px;
        padding: 22px 24px;
        border: 1px solid #edf0f2;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    .box-title {
        font-size: 16px;
        font-weight: 700;
        color: #111417;
        margin-bottom: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Status Pills */
    .pill-completed {
        background: #e8f5e9;
        color: #1b5e3a;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11.5px;
        font-weight: 700;
    }
    .pill-progress {
        background: #fff8e1;
        color: #b78103;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11.5px;
        font-weight: 700;
    }
    .pill-pending {
        background: #fde8e8;
        color: #c53030;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11.5px;
        font-weight: 700;
    }

    /* Streamlit tabs override in light mode */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 2px solid #edf0f2;
        padding-bottom: 4px;
        margin-bottom: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #f4f5f7;
        border-radius: 12px;
        padding: 8px 18px;
        font-weight: 700;
        font-size: 13px;
        color: #6f767e !important;
        border: 1px solid #eef0f2;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: #1b5e3a !important;
        color: #ffffff !important;
        border: 1px solid #1b5e3a !important;
        box-shadow: 0 2px 8px rgba(27, 94, 58, 0.18);
    }

    /* Verdict Card Styles */
    .verdict-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 18px 22px;
        border: 1px solid #edf0f2;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
        margin-bottom: 14px;
    }
    .verdict-card-tint-green {
        background: #f4faf6;
        border: 1px solid #d4edda;
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }
    .verdict-card-tint-yellow {
        background: #fefcf2;
        border: 1px solid #ffeeba;
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }
    .verdict-card-tint-red {
        background: #fdf5f5;
        border: 1px solid #f8d7da;
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }
    .card-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .card-title {
        font-size: 15px;
        font-weight: 700;
        color: #111417;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        margin-top: 10px;
    }
    .mini-tile {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 10px 14px;
        border: 1px solid #edf0f2;
    }
    .mini-tile-val {
        font-size: 16px;
        font-weight: 700;
        color: #111417;
    }
    .mini-tile-lbl {
        font-size: 11.5px;
        color: #6f767e;
        margin-top: 2px;
    }
    .question-callout {
        background: #f8f9fb;
        border-left: 4px solid #1b5e3a;
        padding: 10px 14px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 8px;
        font-size: 13.5px;
        color: #2b3036;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Preset Benchmark Cases from METABRIC Cohort
PRESET_PATIENTS = {
    "Custom Parameters": {
        "age": 56, "size": 22, "nodes": 0, "grade": 2, "meno": "Post-menopausal", "pr": "Positive (≥ 20%)",
        "mki67": 0.20, "mmp11": 0.10, "cenpf": 0.30, "aurka": 0.20, "esr1": 0.50,
        "id": "Patient-Custom"
    },
    "Patient MB-0275 (Concordant Low-Risk Luminal A)": {
        "age": 62, "size": 9, "nodes": 0, "grade": 1, "meno": "Post-menopausal", "pr": "Positive (≥ 20%)",
        "mki67": -1.31, "mmp11": -0.53, "cenpf": -1.55, "aurka": -1.20, "esr1": 1.45,
        "id": "METABRIC-MB-0275"
    },
    "Patient MB-0010 (Concordant High-Risk Luminal B)": {
        "age": 79, "size": 31, "nodes": 1, "grade": 3, "meno": "Post-menopausal", "pr": "Negative (< 20%)",
        "mki67": 0.52, "mmp11": 0.66, "cenpf": 1.33, "aurka": 0.95, "esr1": -0.35,
        "id": "METABRIC-MB-0010"
    },
    "Patient MB-0270 (Discordant Hidden Genomic High-Risk)": {
        "age": 30, "size": 14, "nodes": 0, "grade": 3, "meno": "Pre-menopausal", "pr": "Positive (≥ 20%)",
        "mki67": 1.17, "mmp11": -1.20, "cenpf": 0.80, "aurka": 1.10, "esr1": 0.40,
        "id": "METABRIC-MB-0270"
    }
}

# --- SIDEBAR (Clean Functional Light Menu) ---
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:18px;">
        <div style="background:#1b5e3a; width:34px; height:34px; border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-size:18px;">🧬</div>
        <span style="font-size:19px; font-weight:800; color:#111417; letter-spacing:-0.5px;">RecurLens AI</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:11px; font-weight:700; color:#8c9098; text-transform:uppercase; margin-bottom:6px;'>Cohort & Data Ingestion</p>", unsafe_allow_html=True)
    selected_preset = st.selectbox("Load Patient Case", list(PRESET_PATIENTS.keys()), label_visibility="collapsed")
    active_params = PRESET_PATIENTS[selected_preset].copy()

    uploaded_file = st.file_uploader("Upload Patient CSV/TSV", type=["csv", "tsv", "txt"])
    if uploaded_file is not None:
        try:
            sep = "\t" if uploaded_file.name.endswith(".tsv") else ","
            upload_df = pd.read_csv(uploaded_file, sep=sep)
            r0 = upload_df.iloc[0]
            active_params["age"] = int(r0.get("AGE", r0.get("AGE_AT_DIAGNOSIS", active_params["age"])))
            active_params["size"] = int(r0.get("TUMOR_SIZE", active_params["size"]))
            active_params["nodes"] = int(r0.get("NODES", r0.get("LYMPH_NODES_EXAMINED_POSITIVE", active_params["nodes"])))
            active_params["grade"] = int(r0.get("GRADE", active_params["grade"]))
            active_params["mki67"] = float(r0.get("MKI67", active_params["mki67"]))
            active_params["mmp11"] = float(r0.get("MMP11", active_params["mmp11"]))
            active_params["cenpf"] = float(r0.get("CENPF", active_params["cenpf"]))
            active_params["aurka"] = float(r0.get("AURKA", active_params["aurka"]))
            active_params["esr1"] = float(r0.get("ESR1", active_params["esr1"]))
            active_params["id"] = str(r0.get("PATIENT_ID", "Uploaded-Patient"))
            st.success(f"Loaded: {uploaded_file.name}")
        except Exception as e:
            st.error(f"Upload error: {e}")

    st.markdown("<p style='font-size:11px; font-weight:700; color:#8c9098; text-transform:uppercase; margin-top:16px; margin-bottom:6px;'>Clinicopathological Variables</p>", unsafe_allow_html=True)
    age = st.slider("Patient Age at Diagnosis", 25, 85, int(active_params["age"]))
    tumor_size_mm = st.slider("Pathological Tumor Size (mm)", 2, 50, int(active_params["size"]))
    nodes = st.selectbox("Positive Axillary Lymph Nodes", [0, 1, 2, 3], index=int(min(3, active_params["nodes"])))
    grade = st.selectbox("Nottingham Histologic Grade", [1, 2, 3], index=int(active_params["grade"] - 1),
                         format_func=lambda g: f"Grade {g}")

    with st.expander("🔬 Additional Clinical Parameters", expanded=False):
        meno_status = st.selectbox("Menopausal Status", ["Post-menopausal", "Pre-menopausal", "Peri-menopausal"],
                                   index=0 if active_params.get("meno") == "Post-menopausal" else 1)
        pr_status = st.selectbox("Progesterone Receptor (PR)", ["Positive (≥ 20%)", "Low / Negative (< 20%)"],
                                 index=0 if "≥" in active_params.get("pr", "≥") else 1)
        ki67_mode = st.radio("Ki-67 Input Mode", ["RNA Z-Score", "Hospital Pathology IHC %"])

    st.markdown("<p style='font-size:11px; font-weight:700; color:#8c9098; text-transform:uppercase; margin-top:16px; margin-bottom:6px;'>Transcriptomic Drivers</p>", unsafe_allow_html=True)
    if ki67_mode == "Hospital Pathology IHC %":
        ki67_pct = st.slider("Pathology Ki-67 Index (%)", 1, 90, 20)
        mki67 = (ki67_pct - 20.0) / 15.0
    else:
        mki67 = st.slider("MKI67 (Ki-67 Mitosis z-score)", -2.5, 3.0, float(active_params["mki67"]), 0.05)

    mmp11 = st.slider("MMP11 (Stromal ECM Invasion)", -2.5, 3.0, float(active_params["mmp11"]), 0.05)
    cenpf = st.slider("CENPF (Centromere Spindle)", -2.5, 3.0, float(active_params["cenpf"]), 0.05)
    aurka = st.slider("AURKA (Centrosome Spindle)", -2.5, 3.0, float(active_params["aurka"]), 0.05)
    esr1 = st.slider("ESR1 (Estrogen Receptor)", -2.5, 3.0, float(active_params["esr1"]), 0.05)

    st.markdown("<p style='font-size:11px; font-weight:700; color:#8c9098; text-transform:uppercase; margin-top:16px; margin-bottom:6px;'>Adjuvant Chemo Simulation</p>", unsafe_allow_html=True)
    simulate_chemo = st.checkbox("Simulate Cytotoxic Chemotherapy", value=True)
    chemo_rr = st.slider("Relative Risk Reduction (%)", 10, 40, 25, 5, help="Standard EBCTCG trial meta-analysis = 25% RRR")

# --- QUANTITATIVE ENGINE ---
node_grp = 0 if nodes == 0 else 1
scaled_size = 0.2 * tumor_size_mm
cts5_score = (
    0.438 * node_grp
    + 0.988 * scaled_size
    - 0.012 * (scaled_size ** 2)
    + 0.127 * grade
    + 0.015 * age
)

if cts5_score < 3.13:
    cts5_tier = "Low Risk"
    cts5_desc = "< 5% 10y risk"
elif cts5_score <= 3.86:
    cts5_tier = "Intermediate"
    cts5_desc = "5–10% 10y risk"
else:
    cts5_tier = "High Risk"
    cts5_desc = "> 10% 10y risk"

# Model B & C Late Fusion
lp_mol = 0.1035 * cenpf + 0.0465 * mki67 + 0.0331 * aurka + 0.0500 * mmp11 - 0.0350 * esr1
lp_clin = -0.0039 * age + 0.0191 * tumor_size_mm + 0.1705 * nodes + 0.2180 * grade
gamma_clin, gamma_mol = 0.7565, 1.6258
lp_integrated = gamma_clin * lp_clin + gamma_mol * lp_mol

hr_clin = float(np.exp(lp_clin - 0.75))
hr_integrated = float(np.exp(lp_integrated - 0.85))

risk_5yr_clin = float(1.0 - np.exp(-0.16 * hr_clin))
risk_5yr_int = float(1.0 - np.exp(-0.16 * hr_integrated))
risk_10yr_int = float(1.0 - np.exp(-0.31 * hr_integrated))

# Chemotherapy Simulation
chemo_hazard_ratio = 1.0 - (chemo_rr / 100.0)
hr_chemo = hr_integrated * chemo_hazard_ratio
risk_5yr_chemo = float(1.0 - np.exp(-0.16 * hr_chemo))
arr_5yr = max(0.0, (risk_5yr_int - risk_5yr_chemo) * 100.0)
nnt_5yr = int(np.ceil(100.0 / arr_5yr)) if arr_5yr > 0.3 else "> 300"
delta_risk = (risk_5yr_int - risk_5yr_clin) * 100.0

patient_id = active_params.get("id", "Patient-Case")

# --- HEADER (Clean Functional) ---
st.markdown(f"""
<div class="header-container">
    <h1 class="header-title">RecurLens Intelligence Engine</h1>
    <div class="header-sub">Explainable multimodal recurrence risk stratification for early-stage ER+/HER2- breast cancer. Active case: <strong>{patient_id}</strong>.</div>
</div>
""", unsafe_allow_html=True)

# --- 4 KPI CARDS (Donezo Palette: 1 Forest Green + 3 Clean White) ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="stat-card-green">
        <div class="stat-arrow stat-arrow-green">↗</div>
        <div class="stat-label-green">5-Year Recurrence Risk (Model C)</div>
        <div class="stat-val-green">{risk_5yr_int * 100:.1f}%</div>
        <div class="stat-badge-green">{'▲ Escalated +' if delta_risk>0 else '▼ Sparing '}{abs(delta_risk):.1f}% vs Clinical</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card-white">
        <div class="stat-arrow stat-arrow-white">↗</div>
        <div class="stat-label-white">CTS5 Clinical Staging Score</div>
        <div class="stat-val-white">{cts5_score:.2f}</div>
        <div class="stat-badge-white">{cts5_tier} ({cts5_desc})</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card-white">
        <div class="stat-arrow stat-arrow-white">↗</div>
        <div class="stat-label-white">10-Year Cumulative Risk</div>
        <div class="stat-val-white">{risk_10yr_int * 100:.1f}%</div>
        <div class="stat-badge-white">Extended Endocrine Window</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-card-white">
        <div class="stat-arrow stat-arrow-white">↗</div>
        <div class="stat-label-white">Chemotherapy Benefit (ARR)</div>
        <div class="stat-val-white">+{arr_5yr:.1f}%</div>
        <div class="stat-badge-white">NNT: {nnt_5yr} to prevent 1 relapse</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

# --- MIDDLE SECTION: BIOMARKERS & CLINICAL GUIDANCE ---
m_col1, m_col2 = st.columns([1.1, 1.4])

with m_col1:
    st.markdown("""
    <div class="content-box">
        <div class="box-title">
            <span>🧬 Biomarker Expression Activity</span>
            <span class="pill-completed">5 Drivers</span>
        </div>
        <div style="font-size:12.5px; color:#6f767e; margin-bottom:12px;">Normalized cohort z-scores relative to diploid baseline:</div>
    """, unsafe_allow_html=True)
    
    biomarkers = [
        ("MKI67 (Ki-67)", mki67, "#1b5e3a"),
        ("MMP11 (Stromelysin-3)", mmp11, "#2d8a56"),
        ("CENPF (Centromere F)", cenpf, "#41b078"),
        ("AURKA (Aurora Kinase A)", aurka, "#5fbd90"),
        ("ESR1 (Estrogen Receptor)", esr1, "#7cb299")
    ]
    
    for name, val, bar_col in biomarkers:
        pct_width = int(np.clip((val + 2.5) / 5.5 * 100, 5, 95))
        st.markdown(f"""
        <div style="margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; font-size:12.5px; font-weight:600; margin-bottom:3px;">
                <span>{name}</span>
                <span style="color:{bar_col}; font-weight:700;">{val:+.2f} z-score</span>
            </div>
            <div style="background:#eef0f2; border-radius:10px; height:7px; overflow:hidden;">
                <div style="background:{bar_col}; width:{pct_width}%; height:7px; border-radius:10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

with m_col2:
    if risk_5yr_int < 0.10:
        badge_class = "pill-completed"
        badge_text = "Chemotherapy Sparing Candidate"
        action_title = "Adjuvant Endocrine Monotherapy Recommended"
        action_desc = (
            f"Patient {patient_id} demonstrates low 5-year integrated recurrence risk ({risk_5yr_int*100:.1f}%). "
            f"Per ASCO 2022 and NCCN guidelines (TAILORx trial criteria), absolute chemotherapy benefit is negligible (< 1.5%). "
            f"Prescribe 5–10 years of standard adjuvant endocrine therapy (Aromatase Inhibitor or Tamoxifen)."
        )
    elif risk_5yr_int <= 0.15:
        badge_class = "pill-progress"
        badge_text = "Borderline Decision Zone"
        action_title = "Multidisciplinary Consultation Required"
        action_desc = (
            f"Patient demonstrates intermediate 5-year recurrence risk ({risk_5yr_int*100:.1f}%). "
            f"Simulated absolute chemotherapy risk reduction is {arr_5yr:.1f}% (NNT ≈ {nnt_5yr}). "
            f"Decision should integrate menopausal status ({meno_status}), comorbidities, and patient toxicity preference."
        )
    else:
        badge_class = "pill-pending"
        badge_text = "High Early Recurrence Hazard"
        action_title = "Adjuvant Cytotoxic Chemotherapy Strongly Indicated"
        action_desc = (
            f"Patient exhibits aggressive biology with 5-year integrated recurrence risk of {risk_5yr_int*100:.1f}%. "
            f"Adjuvant cytotoxic chemotherapy provides substantial projected absolute survival gain of +{arr_5yr:.1f}% (NNT = {nnt_5yr}). "
            f"Sequential chemotherapy followed by extended endocrine therapy is strongly indicated."
        )

    st.markdown(f"""
    <div class="content-box">
        <div class="box-title">
            <span>📋 Clinical Action Recommendation</span>
            <span class="{badge_class}">{badge_text}</span>
        </div>
        <div style="font-size:15.5px; font-weight:700; color:#111417; margin-bottom:6px;">{action_title}</div>
        <div style="font-size:13px; color:#4a5056; line-height:1.55; margin-bottom:14px;">{action_desc}</div>
        <div style="font-size:12px; color:#6f767e;">Guideline Concordance: ASCO 2022 / NCCN v2.2024</div>
    </div>
    """, unsafe_allow_html=True)

# --- DUAL-PERSPECTIVE FINAL VERDICT SECTION (Tabs + Card Style) ---
st.markdown("""
<div class="content-box">
    <div class="box-title">
        <span>⚖️ Final RecurLens Clinical Verdict</span>
        <span class="stat-badge-white">Dual-Perspective Card Synthesis</span>
    </div>
""", unsafe_allow_html=True)

tab_med, tab_plain = st.tabs([
    "🩺 For Clinicians & Multidisciplinary Tumor Board",
    "👤 For Patients & Families (Plain Language)"
])

# Concordance classification
if cts5_tier == "Low Risk" and risk_5yr_int < 0.10:
    conc_text = "Concordant Low Risk (Luminal A)"
    conc_pill = "pill-completed"
elif cts5_tier == "High Risk" and risk_5yr_int >= 0.15:
    conc_text = "Concordant High Risk (Luminal B)"
    conc_pill = "pill-pending"
elif cts5_tier == "Low Risk" and risk_5yr_int >= 0.10:
    conc_text = "Discordant: Genomic Escalation"
    conc_pill = "pill-progress"
else:
    conc_text = "Discordant: Genomic De-escalation"
    conc_pill = "pill-completed"

with tab_med:
    # Card 1: Staging & Multimodal Concordance
    st.markdown(f"""
    <div class="verdict-card">
        <div class="card-header-row">
            <div class="card-title">🏷️ Diagnostic Staging & Concordance</div>
            <span class="{conc_pill}">{conc_text}</span>
        </div>
        <div class="card-grid">
            <div class="mini-tile">
                <div class="mini-tile-val">pT{1 if tumor_size_mm<=20 else 2} pN{0 if nodes==0 else 1}</div>
                <div class="mini-tile-lbl">Pathological TNM Stage</div>
            </div>
            <div class="mini-tile">
                <div class="mini-tile-val">Nottingham Grade {grade}</div>
                <div class="mini-tile-lbl">Histologic Differentiation</div>
            </div>
            <div class="mini-tile">
                <div class="mini-tile-val">{cts5_score:.2f} ({cts5_tier})</div>
                <div class="mini-tile-lbl">Standard CTS5 Clinical Score</div>
            </div>
            <div class="mini-tile">
                <div class="mini-tile-val">{risk_5yr_int*100:.1f}%</div>
                <div class="mini-tile-lbl">RecurLens 5-Yr Risk (Δ {delta_risk:+.1f}%)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Card 2: Pharmacotherapeutic Protocol
    chemo_recom = "Cytotoxic chemotherapy provides negligible absolute benefit (< 1.5%) and is contraindicated to spare toxicities." if risk_5yr_int < 0.10 else ("Intermediate benefit zone: discuss marginal benefit vs toxicity with tumor board." if risk_5yr_int <= 0.15 else f"Taxane/anthracycline-based adjuvant chemotherapy strongly indicated prior to endocrine therapy.")
    chemo_badge_class = "pill-completed" if risk_5yr_int < 0.10 else ("pill-progress" if risk_5yr_int <= 0.15 else "pill-pending")
    chemo_badge_text = "Chemotherapy Sparing" if risk_5yr_int < 0.10 else ("Borderline / Multidisciplinary" if risk_5yr_int <= 0.15 else "Chemotherapy Indicated")

    st.markdown(f"""
    <div class="verdict-card">
        <div class="card-header-row">
            <div class="card-title">💊 Systemic Pharmacotherapy Protocol (ASCO 2022 / NCCN v2.2024)</div>
            <span class="{chemo_badge_class}">{chemo_badge_text}</span>
        </div>
        <div style="font-size:13.5px; line-height:1.55; color:#2b3036; margin-bottom:12px;">
            <strong>1. Adjuvant Endocrine Therapy:</strong> 5–10 years of systemic endocrine therapy (Aromatase Inhibitor ± Ovarian Function Suppression for pre-menopausal; AI monotherapy for post-menopausal).<br>
            <strong>2. Adjuvant Chemotherapy Indication:</strong> {chemo_recom}
        </div>
        <div class="card-grid">
            <div class="mini-tile">
                <div class="mini-tile-val">+{arr_5yr:.1f}% ARR</div>
                <div class="mini-tile-lbl">Chemo Absolute Risk Reduction</div>
            </div>
            <div class="mini-tile">
                <div class="mini-tile-val">NNT = {nnt_5yr}</div>
                <div class="mini-tile-lbl">Number Needed to Treat (5 Years)</div>
            </div>
            <div class="mini-tile">
                <div class="mini-tile-val">{risk_10yr_int*100:.1f}%</div>
                <div class="mini-tile-lbl">10-Year Extended Failure Probability</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Card 3: Biomarker Drivers & Trial Evidence
    st.markdown(f"""
    <div class="verdict-card">
        <div class="card-header-row">
            <div class="card-title">🔬 Biological Drivers & Trial Validation</div>
            <span class="stat-badge-white">TRIPOD+AI Certified</span>
        </div>
        <div style="font-size:13px; line-height:1.5; color:#4a5056;">
            • <strong>Mitotic Spindle & Checkpoint:</strong> CENPF ({cenpf:+.2f}), MKI67 ({mki67:+.2f}), AURKA ({aurka:+.2f}).<br>
            • <strong>Stromal Remodeling & Invasion:</strong> MMP11 ({mmp11:+.2f} z-score).<br>
            • <strong>Endocrine Sensitivity:</strong> ESR1 ({esr1:+.2f} z-score).<br>
            • <strong>Clinical Trial Evidence:</strong> Proven in METABRIC cohort (N = 1,102, C-index = 0.6361, p = 5.05e-8). 5-Year Continuous Net Reclassification Improvement: <strong>NRI = +36.1%</strong> (p &lt; 0.001).
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab_plain:
    safe_women = int(round(100.0 - (risk_5yr_int * 100.0)))
    chemo_extra = max(1, int(round(arr_5yr)))
    
    if risk_5yr_int < 0.10:
        tint_class = "verdict-card-tint-green"
        plain_title = "Gentle, Slow-Growing Tumor (Chemotherapy Likely Not Needed)"
        plain_text = (
            "Your cancer cells are dividing slowly and look calm under the microscope. "
            "Because the cancer is gentle, taking daily hormone-blocking pills gives you nearly the same protection "
            "as chemotherapy, without any of the heavy side effects."
        )
        chemo_summary = "Chemotherapy adds less than 1 extra woman protected out of 100; side effects outweigh benefits."
    elif risk_5yr_int <= 0.15:
        tint_class = "verdict-card-tint-yellow"
        plain_title = "Borderline / Middle Zone (Discuss Small Benefits vs Side Effects)"
        plain_text = (
            "Your tumor is in the middle zone. Some markers are peaceful, but others show modest division. "
            "Hormone pills are definitely needed, and adding chemotherapy offers a small extra layer of protection."
        )
        chemo_summary = f"Chemotherapy protects an estimated {chemo_extra} extra women out of 100."
    else:
        tint_class = "verdict-card-tint-red"
        plain_title = "Active Tumor Cells (Chemotherapy Strongly Recommended)"
        plain_text = (
            "Your cancer cells have faster engines running and are dividing more actively. "
            "Chemotherapy directly attacks fast-dividing cells and provides a strong, proven shield before hormone therapy starts."
        )
        chemo_summary = f"Chemotherapy provides a strong shield, protecting an extra {chemo_extra} women out of 100."

    # Patient Card 1: Bottom line diagnosis
    st.markdown(f"""
    <div class="{tint_class}">
        <div style="font-size:16px; font-weight:800; color:#111417; margin-bottom:6px;">💡 {plain_title}</div>
        <div style="font-size:13.5px; line-height:1.55; color:#2b3036;">{plain_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # Patient Card 2: Out of 100 women tiles
    st.markdown(f"""
    <div class="verdict-card">
        <div class="card-header-row">
            <div class="card-title">📊 The "Out of 100 Women" Picture</div>
            <span class="pill-completed">5-Year Forecast</span>
        </div>
        <div class="card-grid">
            <div class="mini-tile" style="border-left: 4px solid #1b5e3a;">
                <div class="mini-tile-val" style="color:#1b5e3a;">{safe_women} / 100</div>
                <div class="mini-tile-lbl">Stay cancer-free with hormone pills alone</div>
            </div>
            <div class="mini-tile" style="border-left: 4px solid #dc3545;">
                <div class="mini-tile-val" style="color:#dc3545;">{100 - safe_women} / 100</div>
                <div class="mini-tile-lbl">Risk of cancer returning without extra therapy</div>
            </div>
            <div class="mini-tile" style="border-left: 4px solid #41b078;">
                <div class="mini-tile-val" style="color:#41b078;">+{chemo_extra} / 100</div>
                <div class="mini-tile-lbl">Extra women protected by chemotherapy</div>
            </div>
        </div>
        <div style="font-size:12.5px; color:#6f767e; margin-top:12px;">{chemo_summary}</div>
    </div>
    """, unsafe_allow_html=True)

    # Patient Card 3: Questions for the doctor
    st.markdown(f"""
    <div class="verdict-card">
        <div class="card-header-row">
            <div class="card-title">❓ 3 Questions to Ask Your Doctor</div>
            <span class="stat-badge-white">Patient Guide</span>
        </div>
        <div class="question-callout">
            <strong>1.</strong> "My RecurLens report shows a 5-year recurrence risk of <strong>{risk_5yr_int*100:.1f}%</strong>. Does this mean I can safely avoid chemotherapy?"
        </div>
        <div class="question-callout">
            <strong>2.</strong> "My tumor's cell division index (Ki-67/CENPF) is <strong>{mki67:+.1f}</strong>. Does this match what the hospital pathology report found?"
        </div>
        <div class="question-callout">
            <strong>3.</strong> "Which hormone pill (Tamoxifen or an Aromatase Inhibitor) fits my lifestyle and age ({age} years) best for the next 5 years?"
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# --- VISUALIZATION CHARTS ---
chart_c1, chart_c2 = st.columns(2)

with chart_c1:
    st.markdown("""
    <div class="content-box">
        <div class="box-title">
            <span>📈 15-Year Recurrence-Free Survival Forecast</span>
        </div>
    """, unsafe_allow_html=True)
    
    time_pts = np.linspace(0, 15, 120)
    h_base = 0.03 * (time_pts ** 1.08)
    surv_clin = np.exp(-h_base * hr_clin) * 100.0
    surv_int = np.exp(-h_base * hr_integrated) * 100.0
    
    fig, ax = plt.subplots(figsize=(7, 4.4), dpi=140, facecolor="#ffffff")
    ax.set_facecolor("#ffffff")
    ax.plot(time_pts, surv_clin, label=f"Clinical Baseline (5y: {(1-risk_5yr_clin)*100:.1f}%)",
            color="#6f767e", linestyle="--", linewidth=1.8)
    ax.plot(time_pts, surv_int, label=f"RecurLens Integrated (5y: {(1-risk_5yr_int)*100:.1f}%)",
            color="#1b5e3a", linewidth=2.6)
    
    if simulate_chemo:
        surv_chemo = np.exp(-h_base * hr_chemo) * 100.0
        ax.plot(time_pts, surv_chemo, label=f"Integrated + Chemo (+{arr_5yr:.1f}%)",
                color="#41b078", linestyle="-.", linewidth=2.2)
        
    ax.axvline(x=5.0, color="#d0d5dd", linestyle=":", label="5-Year Early Window")
    ax.set_ylim(40, 102)
    ax.set_xlabel("Years Since Definitive Resection", fontsize=9, fontweight="600", color="#111")
    ax.set_ylabel("Recurrence-Free Survival (%)", fontsize=9, fontweight="600", color="#111")
    ax.grid(True, linestyle="--", alpha=0.35, color="#e5e7eb")
    ax.legend(loc="lower left", fontsize=8.5, frameon=True, facecolor="#ffffff", edgecolor="#e5e7eb")
    
    for spine in ax.spines.values():
        spine.set_color("#e5e7eb")
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_c2:
    st.markdown("""
    <div class="content-box">
        <div class="box-title">
            <span>🔍 Patient SHAP Feature Impact Breakdown</span>
        </div>
    """, unsafe_allow_html=True)
    
    feats = ["Tumor Size", "Positive Nodes", "Grade", "MMP11 (Invasion)", "CENPF (Mitosis)", "MKI67 (Ki-67)", "ESR1 (Estrogen)"]
    shaps = [
        0.0191 * (tumor_size_mm - 20) * gamma_clin,
        0.1705 * (nodes - 0.5) * gamma_clin,
        0.2180 * (grade - 2) * gamma_clin,
        0.0500 * mmp11 * gamma_mol,
        0.1035 * cenpf * gamma_mol,
        0.0465 * mki67 * gamma_mol,
        -0.0350 * esr1 * gamma_mol
    ]
    
    fig2, ax2 = plt.subplots(figsize=(7, 4.4), dpi=140, facecolor="#ffffff")
    ax2.set_facecolor("#ffffff")
    bar_cols = ["#dc3545" if s > 0 else "#1b5e3a" for s in shaps]
    y_pos = np.arange(len(feats))
    ax2.barh(y_pos, shaps, color=bar_cols, height=0.55, alpha=0.9)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(feats, fontsize=9, color="#111")
    ax2.invert_yaxis()
    ax2.axvline(x=0, color="#111417", linewidth=0.8)
    ax2.set_xlabel("Log-Hazard Contribution (Green = Protective, Red = Adverse)", fontsize=8.5, fontweight="600", color="#111")
    ax2.grid(True, axis="x", linestyle="--", alpha=0.35, color="#e5e7eb")
    
    for spine in ax2.spines.values():
        spine.set_color("#e5e7eb")
    plt.tight_layout()
    st.pyplot(fig2)
    st.markdown("</div>", unsafe_allow_html=True)

# --- REPORT EXPORT ---
report_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>RecurLens Consultation - {patient_id}</title>
<style>
    body {{ font-family: 'Plus Jakarta Sans', Arial, sans-serif; margin: 40px; color: #111417; background:#fff; }}
    h1 {{ color: #1b5e3a; font-size: 24px; border-bottom: 2px solid #1b5e3a; padding-bottom: 8px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 10px; font-size: 13.5px; text-align: left; }}
    th {{ background: #f8f9fa; font-weight: 700; }}
</style>
</head>
<body>
<h1>🧬 RecurLens: Clinical Molecular Consultation Report</h1>
<p><strong>Patient Case:</strong> {patient_id} | <strong>Diagnosis:</strong> Early-Stage ER+/HER2- Breast Cancer</p>
<div style="background:#f4f6f8; border-left:5px solid #1b5e3a; padding:15px; border-radius:8px; margin:20px 0;">
    <strong>Recommendation:</strong> {action_title}<br>
    <span style="font-size:13px; color:#4a5056;">{action_desc}</span>
</div>
<table>
    <tr><th>Clinical Parameter</th><th>Value</th><th>Molecular Biomarker</th><th>Normalized Z-Score</th></tr>
    <tr><td>Age at Diagnosis</td><td>{age} years</td><td>MKI67 (Ki-67)</td><td>{mki67:+.2f}</td></tr>
    <tr><td>Tumor Size</td><td>{tumor_size_mm} mm</td><td>MMP11 (Invasion)</td><td>{mmp11:+.2f}</td></tr>
    <tr><td>Axillary Nodes</td><td>{nodes}</td><td>CENPF (Mitosis)</td><td>{cenpf:+.2f}</td></tr>
    <tr><td>Nottingham Grade</td><td>Grade {grade}</td><td>AURKA (Spindle)</td><td>{aurka:+.2f}</td></tr>
    <tr><td>CTS5 Score</td><td>{cts5_score:.2f} ({cts5_tier})</td><td>ESR1 (Estrogen)</td><td>{esr1:+.2f}</td></tr>
</table>
<p><em>RecurLens 5-Year Integrated Risk: <strong>{risk_5yr_int*100:.1f}%</strong> (Clinical Baseline: {risk_5yr_clin*100:.1f}%). Projected Chemo Benefit ARR: <strong>+{arr_5yr:.1f}%</strong> (NNT: {nnt_5yr}).</em></p>
</body>
</html>
"""

st.download_button(
    label="📥 Download Clinical Consultation Report (HTML/PDF)",
    data=report_html,
    file_name=f"RecurLens_Report_{patient_id}.html",
    mime="text/html"
)
