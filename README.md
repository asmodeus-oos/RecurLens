# RecurLens AI 🧬

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![TRIPOD+AI](https://img.shields.io/badge/Guideline-TRIPOD%2BAI-green.svg)](https://www.tripod-statement.org/)
[![Status](https://img.shields.io/badge/Validation-METABRIC%20%7C%20TCGA-teal.svg)](https://www.cbioportal.org/)
[![License](https://img.shields.io/badge/License-MIT-gray.svg)](LICENSE)

**RecurLens AI** is an open-source clinical-molecular decision support system for predicting 5-year and 15-year recurrence-free survival (RFS/DRFS) in early-stage ER+/HER2- breast cancer ($N = 1,206$, METABRIC discovery; $N = 493$, TCGA external validation).

The system integrates clinical pathology metrics (CTS5 benchmark) with multi-gene transcriptomic proliferation and invasion signatures (Oncotype DX surrogate, PAM50 proliferation, and Elastic-Net Cox models) to resolve clinical-molecular discordance and guide systemic chemotherapy sparing under ASCO/NCCN guidelines.

---

## 🎯 Key Empirical Findings

1. **Integrated Prognostic Gain**:
   - Clinical Baseline (CTS5 Cox-PH): Harrell's $C = 0.6001$
   - Molecular Baseline (Elastic-Net): Harrell's $C = 0.6219$
   - **RecurLens Integrated Multi-Modal**: Harrell's $C = 0.6361$ ($\Delta C = +0.0360$, $95\%\text{ CI: } [+0.0152, +0.0572]$, bootstrap $p < 0.0001$; Likelihood Ratio Test $\Delta \text{LR-}\chi^2 = 29.70$, $p = 5.05 \times 10^{-8}$).
2. **Temporal Divergence (Resolving Scenario C)**:
   - **Early Recurrence ($\le 5$ years)**: Clinical $C = 0.6125 \rightarrow$ Integrated $C = 0.6684$ ($\mathbf{\Delta C = +0.0558}$). Primary tumor RNA captures active mitotic/stromal drivers.
   - **Late Recurrence ($> 5$ to 15 years)**: Clinical $C = 0.5776 \rightarrow$ Integrated $C = 0.5778$ ($\Delta C = +0.0001$). Baseline surgical transcriptomics exhibits hazard attenuation; late dormancy is governed by microenvironmental niches.
3. **Clinical Net Benefit & Reclassification**:
   - 5-Year Continuous Net Reclassification Improvement: $\text{NRI} = +36.1\%$ ($p < 0.001$), $\text{IDI} = +0.0234$.
   - Decision Curve Analysis (DCA) proves superior net benefit across all decision thresholds $p_t \in [0.10, 0.30]$.
4. **Natural Prognosis Isolation**:
   - $92.1\%$ ($1,111 / 1,206$) was chemo-naive (endocrine monotherapy alone), eliminating treatment confounding.

---

## 🏛️ Architecture & Project Structure

```
RecurLens/
├── app.py                      # Interactive Streamlit Clinical Dashboard (Pure Light Mode)
├── STUDY_PROTOCOL.md           # Formal TRIPOD+AI & REMARK study protocol
├── MANUSCRIPT.md               # Scientific manuscript formatted for npj Breast Cancer / JCO CCI
├── src/
│   ├── data/                   # Automated data ingestion & cohort harmonization
│   │   ├── ingest_metabric.py  # METABRIC cBioPortal ingestion & CTS5 calculation
│   │   └── ingest_tcga.py      # TCGA PanCanAtlas RNA-seq validation cohort
│   └── models/                 # Survival modeling & analytics engines
│       ├── clinical_baseline.py# Model A: CTS5 Benchmark Cox-PH
│       ├── molecular_baseline.py # Model B: Oncotype DX surrogate & Elastic-Net
│       ├── integrated_model.py # Model C: Multi-modal fusion & bootstrap delta C
│       ├── pathway_scoring.py  # MSigDB Hallmark gene set variation scoring
│       ├── dca.py              # Decision Curve Analysis (Net Benefit calculation)
│       └── explainability.py   # TreeSHAP & Cox feature attributions
├── data/processed/             # Curated parquet & CSV benchmark datasets
├── figures/                    # Publication-ready 300 DPI figures
├── scripts/                    # Validation pipelines
└── tests/                      # Automated pytest validation suite
```

---

## 🚀 Quickstart

### 1. Installation
Clone repository and create virtual environment:

```bash
git clone https://github.com/asmodeus-oos/RecurLens.git
cd RecurLens
python3 -m venv .venv
source .venv/bin/activate
pip install -r <(echo "lifelines scikit-learn shap streamlit pandas numpy pyarrow pytest matplotlib")
```

### 2. Run Tests
Verify pipeline integrity and survival calculation units:

```bash
PYTHONPATH=. pytest tests/
```

### 3. Launch Clinical Decision Support Dashboard
Start the pure light-mode interactive interface:

```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 💻 Dashboard Features

- **Strict Donezo Light Mode**: Clean, distraction-free aesthetic with `#ffffff` cards and `#1b5e3a` forest green accents.
- **Dual-Perspective Final Verdict**:
  - **🩺 Multidisciplinary Tumor Board Tab**: Pathological TNM staging, CTS5 concordance, ASCO/NCCN pharmacotherapeutic recommendations, ARR (Absolute Risk Reduction), and NNT (Number Needed to Treat).
  - **👤 Patient & Family Tab**: Plain-language non-technical explanation, "Out of 100 Women" pictorial breakdown, and 3 personalized questions for the oncology team.
- **Biomarker Slider Controls**: Interactive input for Nottingham Grade, tumor diameter, positive lymph nodes, and transcriptomic markers ($MKI67$, $MMP11$, $CENPF$, $AURKA$, $ESR1$).
- **Chemotherapy Benefit Simulator**: Dynamic EBCTCG meta-analysis proportional hazard reduction ($HR = 0.70$).
- **Export Facility**: One-click printable HTML/PDF clinical summary report.

---

## 📜 Regulatory & Reporting Standards

- **TRIPOD+AI**: Adheres to Transparent Reporting of a multivariable prediction model of Individual Prognosis Or Diagnosis + Artificial Intelligence.
- **REMARK**: Adheres to REporting recommendations for tumor MARKer prognostic studies.
- **STEEP System**: Standardized Definitions for Efficacy End Points in Adjuvant Breast Cancer Clinical Trials (DRFS/RFS).

---

## 📄 License
This project is licensed under the MIT License.
