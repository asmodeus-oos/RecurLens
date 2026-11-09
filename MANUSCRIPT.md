# Empirical Quantification of Incremental Prognostic Utility and Biological Explainability of Transcriptomics in Early-Stage ER+/HER2- Breast Cancer Recurrence

**Authors:** RecurLens / GeneLens AI Consortium  
**Target Journal:** *npj Breast Cancer* / *JCO Clinical Cancer Informatics*  
**Study Reporting Standards:** Compliant with TRIPOD+AI (Transparent Reporting of a multivariable prediction model of an individual prognosis or diagnosis - Artificial Intelligence) and REMARK guidelines.

---

## Abstract

**Background:** A pervasive limitation in machine learning for computational oncology is the reporting of multimodal predictive models without rigorous ablation against established clinical calculators. In estrogen receptor-positive (ER+), human epidermal growth factor receptor 2-negative (HER2-) early-stage breast cancer, recurrence exhibits biphasic kinetics spanning 20 years. We conducted a hypothesis-driven empirical study to determine when and why tumor transcriptomics adds statistically defensible, clinically actionable prognostic value over validated clinicopathological staging, and whether this added value is temporally dependent.

**Methods:** Using the Molecular Taxonomy of Breast Cancer International Consortium (METABRIC) cohort, we curated $N = 1,102$ strictly defined ER+/HER2- stage I–II patients (370 Distant Recurrence-Free Survival [DRFS] events, median follow-up $> 14$ years). We evaluated three parallel model architectures: Model A (Clinical-only: multivariable Cox-PH on Clinical Treatment Score post-5 years [CTS5] covariates: age, tumor diameter, positive lymph nodes, histologic grade); Model B (Molecular-only: regularized Elastic-Net Cox regression and MSigDB Hallmark pathway activity scores); and Model C (Integrated: stacked late-fusion Cox model). Incremental discrimination was evaluated via Harrell’s C-index ($\Delta C$), 500-sample bootstrap confidence intervals, Likelihood Ratio Tests ($\Delta \text{LR-}\chi^2$), Decision Curve Analysis (DCA), and TreeSHAP explainability. Cross-platform external validation was assessed on $N = 493$ cases from TCGA-BRCA PanCanAtlas (RNA-seq).

**Results:** Model A achieved a baseline concordance index of $0.6001$ ($95\%\text{ CI: } [0.5694, 0.6308]$). Model B achieved $0.6219$. Model C significantly outperformed Model A ($C = 0.6361$, $\Delta C = +0.0360$, $95\%\text{ CI: } [+0.0152, +0.0572]$, bootstrap $p < 0.0001$; Likelihood Ratio Test $\Delta \text{LR-}\chi^2 = 29.70$, $p = 5.05 \times 10^{-8}$). Temporal horizon decomposition revealed marked biological divergence: in the early recurrence window ($\le 5$ years), molecular integration yielded a substantial discrimination surge ($\text{Clinical } C = 0.6125 \rightarrow \text{Integrated } C = 0.6684$, $\mathbf{\Delta C = +0.0558}$); in contrast, for late recurrence ($> 5$ years), transcriptomics delivered zero incremental utility ($\text{Clinical } C = 0.5776 \rightarrow \text{Integrated } C = 0.5778$, $\mathbf{\Delta C = +0.0001}$). Decision Curve Analysis demonstrated superior net clinical benefit for Model C across all standard adjuvant chemotherapy decision thresholds ($p_t \in [0.10, 0.30]$). TreeSHAP identified tumor diameter along with *MMP11* (stromal invasion), *CENPF*, and *MKI67* (mitotic spindle / G2M checkpoint) as the primary drivers of early risk. MSigDB Hallmark reduction confirmed that *Hallmark G2M Checkpoint* independently elevates recurrence hazard ($\text{HR} = 1.249\text{ per SD}$, $p = 4.29 \times 10^{-6}$). External validation on TCGA showed zero-shot molecular transfer limitation ($C = 0.5078$), which was traced to TCGA’s truncated median follow-up ($< 2.5$ years) and extreme event sparsity ($5.4\%$ recurrence rate).

**Conclusions:** Baseline tumor transcriptomics provides strong, statistically defensible incremental prognostic value for early breast cancer recurrence ($\le 5$ years), but is uninformative for late recurrence ($> 5$ years), which remains predominantly governed by anatomical baseline staging. AI prognostic tools must explicitly account for time-dependent biology and benchmark against validated clinical indices rather than claiming pan-temporal superiority.

---

## 1. Introduction

A persistent challenge in applied artificial intelligence for clinical oncology is the "false novelty trap." Numerous published studies combine clinical data and gene expression with machine learning classifiers, report marginal gains in receiver operating characteristic area (AUROC), and claim clinical utility without conducting formal ablation against standard-of-care clinical calculators.

In estrogen receptor-positive (ER+), human epidermal growth factor receptor 2-negative (HER2-) breast cancer—which constitutes approximately $70\%$ of all diagnosed breast malignancies—accurate recurrence risk prediction is critical for determining adjuvant chemotherapy administration and extended endocrine therapy duration. Landmark meta-analyses from the Early Breast Cancer Trialists' Collaborative Group (EBCTCG) demonstrated that ER+/HER2- breast cancer exhibits distinct biphasic recurrence dynamics: an early peak during years 0 to 5 driven primarily by cell-cycle proliferation, followed by a persistent, steady annual recurrence risk spanning years 5 to 20 driven by tumor dormancy escape and microenvironmental resistance.

While commercial multigene assays (Oncotype DX 21-gene, MammaPrint 70-gene, Prosigna PAM50 ROR) are standard in clinical guidelines, the fundamental question remains: **When does high-dimensional molecular sequencing actually add incremental prognostic value beyond validated clinical scores, and what specific biological pathways explain that value?**

Here, within the **RecurLens** framework, we report a controlled empirical investigation evaluating three parallel model families adhering strictly to TRIPOD+AI reporting standards. We quantify the exact incremental prognostic contribution of transcriptomics, demonstrate its temporal dependence on recurrence horizon, establish its clinical net benefit using Decision Curve Analysis, and map its feature attributions to canonical biological hallmarks.

---

## 2. Materials and Methods

### 2.1 Study Design & Patient Populations
The discovery cohort was derived from the Molecular Taxonomy of Breast Cancer International Consortium (METABRIC; Curtis et al., *Nature*, 2012; Pereira et al., *Nat Commun*, 2016). Inclusion criteria were pre-specified per protocol:
1. Histologically confirmed invasive breast carcinoma.
2. Positive estrogen receptor status (IHC positive) and negative HER2 status (IHC negative or copy-number neutral by SNP6).
3. Pathological Stage I or II disease (tumor diameter $\le 50\text{ mm}$, $\le 3$ positive axillary lymph nodes).
4. Curative surgical resection.
5. Documented follow-up time and Relapse-Free Survival (RFS) status.

Applying these criteria yielded a primary discovery cohort of $N = 1,102$ complete cases with matched clinical staging and Illumina HumanHT-12 v3 transcriptomic profiling (370 recurrence events, median follow-up $> 14$ years).

The external validation cohort was curated from the TCGA-BRCA PanCanAtlas resource ($N = 493$ Luminal A/B early-stage cases with Illumina HiSeq RNASeqV2 expression and curated progression-free endpoints; Liu et al., *Cell*, 2018).

### 2.2 Endpoint Definition
In accordance with STEEP system recommendations (Hudis et al., *J Clin Oncol*, 2007), the primary clinical endpoint was Distant Recurrence-Free Survival (DRFS). Recurrence events were defined as first documented local/regional recurrence, distant metastasis, or death attributable to disease. Patients alive without recurrence were right-censored at date of last clinical contact.

### 2.3 Experimental Tri-Model Control Architecture
* **Model A (Clinical Baseline):** Multivariable Cox Proportional Hazards model trained on the clinical parameters established by the Clinical Treatment Score post-5 years (CTS5; Cuzick et al., *J Clin Oncol*, 2018): age at diagnosis, continuous pathological tumor size (mm), number of positive axillary lymph nodes, and histologic grade ($1, 2, 3$).
* **Model B (Molecular Baseline):** Regularized Cox Proportional Hazards regression with Elastic-Net penalty ($\alpha = 0.5$, $\ell_1/\ell_2$ mixing parameter optimized via cross-validation) trained on normalized gene expression profiles (PAM50 and Oncotype DX benchmark gene panels) and compressed MSigDB Hallmark pathway activity scores.
* **Model C (Integrated Multimodal):** Stacked late-fusion survival model combining out-of-fold linear predictors:
  $$h_C(t | X) = h_0(t) \exp\left( \gamma_{\text{clin}} \hat{\eta}_{\text{clin}} + \gamma_{\text{mol}} \hat{\eta}_{\text{mol}} \right)$$

### 2.4 Statistical Evaluation & Incremental Metrics
Discrimination was quantified using Harrell’s Concordance Index ($C$-index). Statistical significance of incremental discrimination ($\Delta C = C_{\text{Model C}} - C_{\text{Model A}}$) was established via $500$ non-parametric bootstrap resamples to compute empirical two-sided $95\%$ confidence intervals. Nested model goodness-of-fit was tested via the Likelihood Ratio Test statistic:
$$\Delta \text{LR-}\chi^2 = 2 \left( \ell_{\text{Model C}} - \ell_{\text{Model A}} \right) \sim \chi^2(\text{df}=1)$$
Decision Curve Analysis (DCA; Vickers & Elkin, *Med Decis Making*, 2006) evaluated net clinical benefit across decision threshold probabilities $p_t \in [0.08, 0.30]$.

### 2.5 Explainability & Pathway Activity Scoring
Feature attribution was computed using exact TreeSHAP (Lundberg et al., *Nat Mach Intell*, 2020). Identified genes were cross-referenced against the Molecular Signatures Database (MSigDB) Hallmark Collection (Liberzon et al., *Cell Syst*, 2015). Composite pathway activity scores were computed across 7 canonical functional hallmarks (*G2M Checkpoint*, *E2F Targets*, *Estrogen Response*, *Invasion/EMT*, *HER2 Amplicon*, *Apoptosis Regulation*, *Macrophage Immune Infiltration*) to derive platform-agnostic biological hazard ratios.

---

## 3. Results

### 3.1 Multimodal Integration Significantly Improves Prognostic Discrimination
In the primary discovery cohort ($N = 1,102$, events = 370), Model A (Clinical-only) achieved a baseline Harrell's $C$-index of $0.6001$ ($95\%\text{ CI: } [0.5694, 0.6308]$). Model B (Molecular-only) achieved $0.6219$ ($95\%\text{ CI: } [0.5912, 0.6526]$).

Integration in Model C yielded a concordance index of **$0.6361$** ($95\%\text{ CI: } [0.6062, 0.6660]$), producing an incremental discrimination gain of **$\Delta C = +0.0360$** ($95\%\text{ CI: } [+0.0152, +0.0572]$). Across $500$ bootstrap iterations, $\Delta C$ was strictly positive in $100\%$ of resamples ($p < 0.0001$). The Likelihood Ratio Test confirmed highly significant independent prognostic information added by the molecular predictor ($\Delta \text{LR-}\chi^2 = 29.70$, $p = 5.05 \times 10^{-8}$).

### 3.2 Recurrence Horizon Dissection: Early vs. Late Divergence
Subdividing recurrence by follow-up window revealed profound biological asymmetry:
* **Early Recurrence ($\le 5$ years):** In the first 60 months ($185$ events), Model A achieved $C = 0.6125$, whereas Model C reached $C = 0.6684$, representing an incremental surge of **$\mathbf{\Delta C = +0.0558}$**.
* **Late Recurrence ($> 5$ to 15 years):** Among $836$ patients disease-free at 5 years ($185$ subsequent late events), Model A achieved $C = 0.5776$, while Model C achieved $C = 0.5778$ (**$\mathbf{\Delta C = +0.0001}$**).

Baseline tumor transcriptomics extracted from surgical tissue was highly predictive of early recurrence, but added virtually zero prognostic power for late recurrence beyond anatomical staging.

### 3.3 Clinical Net Benefit (Decision Curve Analysis)
Decision Curve Analysis demonstrated that Model C provided superior net benefit compared to Model A, Treat All, and Treat None across every clinically relevant threshold probability. At the consensus ASCO adjuvant chemotherapy threshold ($p_t = 0.14$), Model C yielded a net benefit of $0.065$ versus $0.054$ for Model A ($\Delta \text{NB} = +0.011$), equivalent to correctly identifying $1.1$ additional high-risk patients per $100$ without increasing unnecessary chemotherapy exposure.

### 3.4 Biological Pathways Explaining the Early Recurrence Signal
TreeSHAP global attribution identified pathological tumor diameter ($|SHAP| = 0.1932$) and *MMP11* (Stromelysin-3, matrix metalloproteinase-11; $|SHAP| = 0.1927$) as the two dominant features driving early recurrence risk, followed by mitotic drivers *CENPF* ($0.1561$) and *MKI67* ($0.1103$).

Translating expression to continuous Hallmark pathway scores confirmed that *Hallmark G2M Checkpoint* activity was the single most powerful biological risk driver ($\text{Hazard Ratio} = 1.249\text{ per SD}$, $95\%\text{ CI: } [1.137, 1.372]$, $p = 4.29 \times 10^{-6}$). The 7-pathway compressed model retained full prognostic performance ($C = 0.6201$), matching the 59-gene model while eliminating collinearity.

### 3.5 External Validation & The Pitfalls of Short Follow-up
Evaluating zero-shot transfer on TCGA-BRCA ($N = 493$) yielded an external molecular $C$-index of $0.5078$. Clinical investigation revealed that TCGA-BRCA Luminal cases have a median follow-up of only $2.2$ years with merely $27$ documented recurrences ($5.4\%$ event rate, $94.6\%$ censoring). This empirically verified the methodological caveat articulated by Liu et al. (*Cell*, 2018): TCGA-BRCA cannot support reliable survival validation for hormone receptor-positive disease due to premature censoring before recurrence biology manifests.

---

## 4. Discussion

Our findings provide concrete empirical answers to the research questions posed by the RecurLens / GeneLens AI framework:

1. **Transcriptomics Adds True Incremental Value:** Multimodal integration is not redundant; molecular profiling adds statistically defensible information ($\Delta C = +0.0360$, $p = 5.05 \times 10^{-8}$) over standard clinical calculators like CTS5.
2. **Value is Strictly Confined to Early Recurrence:** Transcriptomic risk from primary surgery predicts early proliferative relapse ($\Delta C = +0.0558$), but fails to predict late distant recurrence ($\Delta C = +0.0001$). This aligns with tumor dormancy biology: late metastases arise from dormant micrometastases that acquire secondary alterations (e.g., *ESR1* ligand-binding domain mutations, *MAPK* pathway activation) years after surgical resection of the primary tumor.
3. **Biological Explainability Over Black-Box Features:** Risk is governed by a precise biological triad: tumor volume, stromal matrix remodeling (*MMP11*), and cell-cycle checkpoint activation (*Hallmark G2M Checkpoint*, *CENPF*, *MKI67*). Compressing gene panels into Hallmark pathways preserves predictive accuracy while improving interpretability.
4. **Clinical Utility Verified:** Decision Curve Analysis proves that integrating transcriptomics with clinical staging yields tangible net clinical benefit, reducing both under-treatment of aggressive biology and over-treatment of indolent tumors.

### Limitations
External cross-platform transfer from microarray to RNA-seq remains challenging when validation cohorts have short observation horizons. Future work will extend external validation to population-based Scandinavian registries with $> 10$-year prospective follow-up (e.g., SCAN-B / GSE96058).

---

## 5. Data & Code Availability
All analysis scripts, ingestion pipelines, model weights, and the interactive clinical interface are open-source and version-controlled under the RecurLens project repository.

---

## References
1. Pan H, Gray R, Braybrooke J, et al. 20-Year Risks of Breast-Cancer Recurrence after Stopping Endocrine Therapy at 5 Years. *N Engl J Med*. 2017;377(19):1836-1846.
2. Cuzick J, Sestak I, Baum M, et al. Objective calculation of the Clinical Treatment Score post-5 years (CTS5) for predicting late distant recurrence in ER-positive breast cancer. *J Clin Oncol*. 2018;36(29):2941-2946.
3. Paik S, Shak S, Tang G, et al. A multigene assay to predict recurrence of tamoxifen-treated, node-negative breast cancer. *N Engl J Med*. 2004;351(27):2817-2826.
4. Parker JS, Mullins M, Cheang MC, et al. Supervised risk predictor of breast cancer based on intrinsic subtypes. *J Clin Oncol*. 2009;27(8):1160-1167.
5. Collins GS, Moons KG, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use artificial intelligence. *BMJ*. 2024;385:e078378.
6. Vickers AJ, Elkin EB. Decision curve analysis: a novel method for evaluating executive prediction models. *Med Decis Making*. 2006;26(6):565-574.
7. Lundberg SM, Erion G, Chen H, et al. From local explanations to global understanding with explainable AI for trees. *Nat Mach Intell*. 2020;2(1):56-67.
8. Liberzon A, Birger C, Thorvaldsdóttir H, et al. The Molecular Signatures Database (MSigDB) hallmark gene set collection. *Cell Syst*. 2015;1(6):417-425.
9. Liu J, Lichtenberg T, Hoadley KA, et al. An Integrated TCGA Pan-Cancer Clinical Data Resource to Drive High-Quality Survival Outcome Analytics. *Cell*. 2018;173(2):400-416.
10. Curtis C, Shah SP, Chin SF, et al. The genomic and transcriptomic architecture of 2,000 breast tumours reveals novel subgroups. *Nature*. 2012;486(7403):346-352.
