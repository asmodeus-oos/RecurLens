# RecurLens / GeneLens AI: Formal Study Protocol

**Title:** Quantifying the Incremental Prognostic Utility and Biological Explainability of Transcriptomic Profiling over Standard Clinicopathological Baselines in Early-Stage ER+/HER2- Breast Cancer Recurrence.

**Protocol Standard:** Formulated in compliance with TRIPOD+AI (Transparent Reporting of a multivariable prediction model of an individual prognosis or diagnosis - Artificial Intelligence; Collins et al., *BMJ*, 2024) and REMARK (Reporting Recommendations for Tumor Marker Prognostic Studies; McShane et al., *J Clin Oncol*, 2005).

---

## 1. Scientific Background & Rationale

Breast cancer prognosis relies on clinicopathological staging parameters (age, tumor diameter, lymph node involvement, histologic grade, hormone receptor status). While commercial multigene assays (e.g., Oncotype DX 21-gene assay [Paik et al., *NEJM*, 2004], MammaPrint 70-gene signature [van 't Veer et al., *Nature*, 2002], Prosigna PAM50 ROR [Parker et al., *JCO*, 2009]) guide adjuvant chemotherapy decisions in estrogen receptor-positive (ER+), human epidermal growth factor receptor 2-negative (HER2-) disease, machine learning literature frequently reports multimodal classifiers without formal ablation against validated clinical risk scores.

Furthermore, ER+/HER2- breast cancer exhibits distinct biphasic recurrence kinetics: early recurrences (years 0–5) driven by high proliferative biology, and late distant recurrences (years 5–20) driven by indolent tumor dormancy and endocrine resistance mechanisms (Pan et al., Early Breast Cancer Trialists' Collaborative Group [EBCTCG], *NEJM*, 2017).

This protocol defines a rigorous, hypothesis-driven benchmark to determine:
1. Whether tumor transcriptomics adds statistically defensible, clinically meaningful incremental prognostic information beyond established clinical calculators.
2. Whether this added value is temporally dependent (early vs late recurrence).
3. Whether explainable AI (XAI) feature attributions represent biologically reproducible pathway signals that validate in independent external patient populations.

---

## 2. Study Objectives & Hypotheses

### 2.1 Primary Objective
To quantify the incremental prognostic discrimination ($\Delta \text{C-index}$) and statistical improvement ($\Delta \text{LR-}\chi^2$, continuous NRI) obtained by integrating high-dimensional transcriptomics with the Clinical Treatment Score post-5 years (CTS5; Cuzick et al., *JCO*, 2018) for predicting Distant Recurrence-Free Survival (DRFS) in early-stage ER+/HER2- breast cancer.

### 2.2 Secondary Objectives
1. **Temporal Horizon Dissection:** Assess whether transcriptomic signatures deliver differential prognostic utility for early distant recurrence ($\le 5$ years) versus late distant recurrence ($> 5$ to 15 years).
2. **Benchmark Against Approved Assays:** Directly benchmark Model B (de novo transcriptomic model) against computational reconstructions of validated prognostic gene signatures: PAM50 Risk of Recurrence (ROR-S/ROR-P; Parker et al., 2009) and the 21-gene recurrence score surrogate.
3. **Biological Interpretability & Signature Stability:** Quantify whether TreeSHAP feature attributions on biological pathway scores (MSigDB Hallmark Gene Sets; Liberzon et al., *Cell Syst*, 2015) remain stable and concordant across discovery and validation cohorts.

### 2.3 Formal Hypotheses
* **Null Hypothesis ($H_{0}$):** $\Delta C = C_{\text{Integrated (Model C)}} - C_{\text{Clinical (Model A)}} \le 0$ on external validation.
* **Alternative Hypothesis ($H_{1}$):** $\Delta C > 0$ with two-sided $p < 0.05$ and positive net clinical benefit across decision thresholds ($10\%\text{--}25\%$) on Decision Curve Analysis.
* **Pre-declared Negative Result Acceptance:** If Model C fails to outperform Model A ($\Delta C \le 0.01$, LRT $p \ge 0.05$), the study formally concludes that whole-transcriptome sequencing offers no incremental prognostic utility over optimized clinicopathological staging in the target population.

---

## 3. Patient Cohorts & Eligibility Criteria

```
                        Total METABRIC Cohort (N = 1,980)
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            │ Apply Protocol Inclusion / Exclusion Criteria     │
            │  • Invasive breast carcinoma (IDC/ILC/MDLC)       │
            │  • ER+/HER2- confirmed status                     │
            │  • Stage I–II (pT1–pT2, pN0–pN1)                  │
            │  • Curative surgical resection                    │
            │  • Valid RFS/DRFS follow-up and survival time     │
            │  • Exclude: Stage IV, Neoadjuvant, Bilateral      │
            └─────────────────────────┬─────────────────────────┘
                                      │
                                      ▼
                        Discovery Cohort (N ≈ 1,200–1,400)
                                      │
                         5-Fold Nested Cross-Validation
                                      │
                                      ▼
                      External Validation: SCAN-B (GSE96058)
                              (N ≈ 2,000–2,500 ER+/HER2-)
```

### 3.1 Discovery Cohort: METABRIC
* **Source:** Molecular Taxonomy of Breast Cancer International Consortium (Curtis et al., *Nature*, 2012; Pereira et al., *Nat Commun*, 2016).
* **Sample Size:** 1,980 primary breast tumors with long-term clinical annotation (median follow-up $> 14$ years).
* **Platform:** Illumina HumanHT-12 v3 expression beadchips.

### 3.2 External Validation Cohort: SCAN-B
* **Source:** Sweden Cancerome Analysis Network - Breast (GSE96058; Saal et al., *JCO Precis Oncol*, 2020; Staaf et al., *JCO*, 2022).
* **Sample Size:** Population-based cohort ($N = 3,273$), with $> 2,200$ ER+/HER2- patients.
* **Platform:** Poly-A mRNA sequencing (Illumina HiSeq 2500 / NovaSeq).

### 3.3 Inclusion Criteria
1. Female patients aged $\ge 18$ years at diagnosis.
2. Histologically confirmed primary invasive ductal, lobular, or mixed breast carcinoma.
3. Estrogen receptor-positive ($\text{ER}+ \ge 1\%$ by IHC) and HER2-negative (IHC 0/1+ or FISH/SNP6 copy-neutral).
4. Pathological tumor stage: pT1–pT2 ($\le 5.0\text{ cm}$).
5. Pathological nodal stage: pN0 (node-negative) or pN1 ($1\text{--}3$ positive axillary lymph nodes).
6. Curative surgical resection (mastectomy or breast-conserving surgery) with negative margins.
7. Systemic adjuvant endocrine therapy administered (tamoxifen and/or aromatase inhibitor).

### 3.4 Exclusion Criteria
1. Distant metastatic disease at initial diagnosis (Stage IV / M1).
2. Administration of neoadjuvant systemic chemotherapy or endocrine therapy (alters baseline tumor biology and pathological staging).
3. Bilateral breast cancer or history of prior synchronous/metachronous invasive malignancies.
4. Missing survival time or missing relapse-free event status.
5. Incomplete clinical variables required for CTS5 calculation.

---

## 4. Endpoints & Censoring Methodology

In accordance with STEEP system criteria (Hudis et al., *JCO*, 2007):

* **Primary Endpoint:** Relapse-Free Survival (RFS) / Distant Recurrence-Free Survival (DRFS).
  * **Event Definition ($E = 1$):** First documented occurrence of local/regional recurrence, distant metastasis, or death attributable to breast cancer.
  * **Censoring ($E = 0$):** Patient alive and event-free at date of last clinical follow-up, or death due to non-breast cancer causes without prior documented recurrence.
* **Survival Time ($T$):** Time elapsed in months from definitive surgical resection to event or censoring.
* **Time Horizons:**
  * 0–5 years: Early recurrence window.
  * 5–15 years: Late recurrence window (evaluating disease-free survivors at 5-year landmark).

---

## 5. Model Specifications & Experimental Tri-Model Control

```
Patient Profile ──┬──> [Model A: Clinical Baseline] ─────> Risk Score A ──┐
                  │    (CTS5 / Cox-PH on Clinicopath)                     │
                  │                                                       ├──> Comparative &
                  ├──> [Model B: Molecular Baseline] ────> Risk Score B ──┼──> Incremental Analysis
                  │    (Elastic-Net Cox / PAM50 ROR)                      │    (ΔC, LRT, NRI, DCA)
                  │                                                       │
                  └──> [Model C: Integrated Multimodal] ─> Risk Score C ──┘
                       (Late Fusion / Stacked Cox-PH)
```

### 5.1 Model A: Clinical Baseline
* **Predictor Set:** Standard clinicopathological variables formalized by the Clinical Treatment Score post-5 years (CTS5; Cuzick et al., 2018):
  1. Age at diagnosis (continuous, years).
  2. Tumor size (continuous, mm).
  3. Positive lymph node count ($0$, $1\text{--}3$, continuous or categorized).
  4. Histologic tumor grade ($1, 2, 3$).
* **Estimator:** Multivariable Cox Proportional Hazards regression model:
  $$h_A(t | X_{clin}) = h_0(t) \exp\left( \beta_1 \text{Age} + \beta_2 \text{Size} + \beta_3 \text{Nodes} + \beta_4 \text{Grade} \right)$$
* **Benchmark:** Fixed mathematical CTS5 prognostic index without re-fitting.

### 5.2 Model B: Molecular Baseline
* **Predictor Set:** Preprocessed transcriptomic expression matrix.
  * Feature pre-filtering: Top 1,000 genes by Median Absolute Deviation (MAD), or biological dimension reduction into 50 MSigDB Hallmark pathway activity scores via Gene Set Variation Analysis (GSVA).
* **Estimator:**
  * Regularized Cox Proportional Hazards with Elastic-Net penalty ($\alpha = 0.5$, $\ell_1/\ell_2$ mixing parameter selected via inner cross-validation).
  * Random Survival Forest (RSF; 500 trees, log-rank splitting rule).
* **Reference Assays:**
  * In-silico PAM50 Risk of Recurrence (ROR-S: subtype score; ROR-P: subtype + proliferation score).
  * 21-gene Oncotype DX recurrence score surrogate algorithm.

### 5.3 Model C: Integrated Multimodal Architecture
* **Fusion Strategy:** Late integration via stacked Cox proportional hazards regression:
  $$h_C(t | X) = h_0(t) \exp\left( \gamma_1 \hat{\eta}_{clin} + \gamma_2 \hat{\eta}_{mol} \right)$$
  Where $\hat{\eta}_{clin} = X_{clin}\hat{\beta}_{clin}$ and $\hat{\eta}_{mol} = X_{mol}\hat{\beta}_{mol}$ represent the linear predictors derived out-of-fold from Models A and B.

---

## 6. Statistical Evaluation & Incremental Metrics

In adherence to TRIPOD and Pencina et al. (*Stat Med*, 2011):

1. **Survival Discrimination:**
   * Harrell's Concordance Index ($C$-index) and Uno's inverse probability of censoring weighted (IPCW) $C$-index.
   * Time-dependent cumulative/dynamic Area Under the ROC Curve ($C^\tau$) at $t = 5$ years and $t = 10$ years (Heagerty & Zheng, *Biometrics*, 2005).
2. **Incremental Discrimination:**
   * $\Delta C = C_{\text{Model C}} - C_{\text{Model A}}$. 95% Confidence Intervals computed using 1,000 bootstrap resamples.
   * Likelihood Ratio Test (LRT) for nested Cox models:
     $$\Delta \text{LR-}\chi^2 = 2 \left( \ell(\text{Model C}) - \ell(\text{Model A}) \right) \sim \chi^2(\text{df} = k)$$
3. **Reclassification Metrics:**
   * Continuous Net Reclassification Improvement for survival data ($\text{NRI}_{>0}(t)$) at 5 and 10 years.
   * Integrated Discrimination Improvement ($\text{IDI}(t)$).
4. **Calibration & Fit:**
   * Integrated Brier Score (IBS) across follow-up duration $[0, \tau_{max}]$.
   * Landmark calibration plots at 5 and 10 years (observed Kaplan-Meier risk vs predicted decile risks).
5. **Clinical Decision Utility:**
   * Decision Curve Analysis (DCA; Vickers & Elkin, *Med Decis Making*, 2006). Evaluates Net Benefit ($\text{NB}$) across clinical threshold probabilities $p_t \in [0.05, 0.35]$:
     $$\text{NB}(p_t) = \frac{\text{True Positives}}{N} - \frac{\text{False Positives}}{N} \left( \frac{p_t}{1 - p_t} \right)$$

---

## 7. Explainable AI (XAI) & Biological Validation Protocol

```
Input Expression Matrix (Genes / Pathways)
                    │
                    ▼
          Trained Survival Model
                    │
                    ▼
         TreeSHAP / KernelSHAP
     (Attribution per Patient-Feature)
                    │
                    ▼
           Global Feature Ranking
                    │
       ┌────────────┴────────────┐
       ▼                         ▼
Discovery Cohort         Validation Cohort
   (METABRIC)                (SCAN-B)
       │                         │
       └────────────┬────────────┘
                    ▼
       Cross-Cohort Concordance
       (Spearman Rank Correlation ρ)
                    │
                    ▼
  Pathway Enrichment: MSigDB Hallmark
 (E2F Targets, G2M Checkpoint, ER Response)
```

1. **Feature Attribution:** Exact TreeSHAP (Lundberg et al., *Nat Mach Intell*, 2020) applied to tree ensembles to generate local feature impact values for every individual patient:
   $$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ f_x(S \cup \{i\}) - f_x(S) \right]$$
2. **Stability Selection:**
   * Subsampling bootstrap ($B = 500$ iterations, $80\%$ sample size per iteration).
   * Feature retention threshold: $\pi_{threshold} \ge 0.75$.
3. **Cross-Cohort Stability Test:**
   * Rank top 20 most influential biological features in METABRIC.
   * Compute identical attributions in SCAN-B.
   * Calculate rank concordance: Spearman's rank correlation $\rho \ge 0.60$ required to claim reproducible biological signal.

---

## 8. Data Management & Project Governance

* **Data Provenance:**
  * METABRIC: Publicly authenticated cBioPortal data repository (`cBioPortal/datahub`).
  * SCAN-B: NCBI Gene Expression Omnibus (GEO accession `GSE96058`).
* **Environment & Tooling:**
  * Python 3.12 managed via `uv`.
  * Libraries: `scikit-survival`, `lifelines`, `scikit-learn`, `pandas`, `numpy`, `scipy`.
* **Reproducibility Guarantee:**
  * Fixed pseudorandom seeds (`random_state=42`) across all cross-validation splits and bootstrap resamples.
  * Code repository version controlled under Git.
  * Strict separation of discovery cohort training from external validation test locks.
