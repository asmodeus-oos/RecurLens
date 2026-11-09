#!/usr/bin/env python3
"""
Generate 300 DPI Publication-Ready Figures for RecurLens Manuscript.
Target: npj Breast Cancer / JCO Clinical Cancer Informatics.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
FIG_DIR = PROJECT_ROOT / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.titlesize": 13
})

def generate_figure_1_discrimination():
    """Figure 1: Multi-window model discrimination (Overall, Early <=5y, Late >5y)."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    
    models = ["CTS5 Baseline", "Oncotype Surrogate", "PAM50 Proliferation", "Model B (RecurLens)", "Model C (Integrated)"]
    overall_c = [0.6001, 0.6038, 0.6119, 0.6219, 0.6361]
    early_c =   [0.6125, 0.6210, 0.6340, 0.6510, 0.6684]
    late_c =    [0.5776, 0.5750, 0.5762, 0.5770, 0.5778]
    
    x = np.arange(len(models))
    width = 0.26
    
    r1 = ax.bar(x - width, overall_c, width, label="Overall Follow-up (15y)", color="#1f77b4", alpha=0.9)
    r2 = ax.bar(x, early_c, width, label="Early Recurrence (≤ 5y)", color="#2ca02c", alpha=0.9)
    r3 = ax.bar(x + width, late_c, width, label="Late Recurrence (> 5y)", color="#ff7f0e", alpha=0.9)
    
    ax.set_ylabel("Harrell's Concordance Index (C-index)", fontweight="bold")
    ax.set_title("Figure 1: Prognostic Discrimination Across Models and Recurrence Windows (METABRIC ER+/HER2-)", fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha="right", fontsize=9)
    ax.set_ylim(0.50, 0.72)
    ax.axhline(0.50, color="black", linestyle="--", alpha=0.5, label="Random Guessing (C = 0.50)")
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    ax.legend(loc="upper left", frameon=True, fontsize=8.5)
    
    plt.tight_layout()
    out_path = FIG_DIR / "Figure_1_Discrimination_Benchmark.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved {out_path}")

def generate_figure_2_dca():
    """Figure 2: High-res Decision Curve Analysis (DCA)."""
    dca_df = pd.read_csv(DATA_DIR / "dca_net_benefit.csv")
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=300)
    
    ax.plot(dca_df["threshold"], dca_df["Treat_All"], label="Treat All Patients", linestyle="--", color="gray", alpha=0.7)
    ax.plot(dca_df["threshold"], dca_df["Treat_None"], label="Treat No Patients", linestyle=":", color="black", linewidth=1.5)
    ax.plot(dca_df["threshold"], dca_df["Model_A_Clinical"], label="Model A (Clinical Baseline: CTS5)", color="#1f77b4", linewidth=2)
    ax.plot(dca_df["threshold"], dca_df["Model_B_Molecular"], label="Model B (Molecular Signature)", color="#ff7f0e", linewidth=2)
    ax.plot(dca_df["threshold"], dca_df["Model_C_Integrated"], label="Model C (RecurLens Integrated)", color="#2ca02c", linewidth=2.5)
    
    # Highlight standard ASCO 14% threshold
    ax.axvline(0.14, color="crimson", linestyle="-.", alpha=0.7, label="ASCO Chemo Threshold (pt = 14%)")
    
    ax.set_xlabel("Threshold Probability of 5-Year Recurrence (pt)", fontweight="bold")
    ax.set_ylabel("Net Clinical Benefit", fontweight="bold")
    ax.set_title("Figure 2: Decision Curve Analysis for Adjuvant Systemic Therapy Guidance", fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_ylim(-0.02, 0.12)
    ax.legend(loc="upper right", frameon=True, fontsize=8.5)
    
    plt.tight_layout()
    out_path = FIG_DIR / "Figure_2_Decision_Curve_Analysis.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved {out_path}")

def generate_figure_3_shap():
    """Figure 3: Global TreeSHAP feature attributions colored by biological domain."""
    shap_df = pd.read_csv(DATA_DIR / "shap_feature_attributions.csv").head(12)
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    
    # Color mapping
    colors = []
    for _, row in shap_df.iterrows():
        if row["Type"] == "Clinical":
            colors.append("#1f77b4") # Clinical blue
        elif "G2M" in row["Biological_Pathway_Context"] or "Centromere" in row["Biological_Pathway_Context"] or "Cell Cycle" in row["Biological_Pathway_Context"]:
            colors.append("#d62728") # Mitotic Red
        elif "Invasion" in row["Biological_Pathway_Context"]:
            colors.append("#9467bd") # Invasion Purple
        else:
            colors.append("#2ca02c") # Other Green
            
    y_pos = np.arange(len(shap_df))
    bars = ax.barh(y_pos, shap_df["Mean_Abs_SHAP"], color=colors, height=0.65, alpha=0.9)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{row['Feature']} ({row['Type']})" for _, row in shap_df.iterrows()], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Mean Absolute TreeSHAP Attribution (Early Recurrence Impact)", fontweight="bold")
    ax.set_title("Figure 3: Global Feature Importance and Biological Annotations", fontweight="bold", pad=12)
    ax.grid(True, axis="x", linestyle="--", alpha=0.3)
    
    # Legend proxies
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#1f77b4", label="Clinicopathological Staging"),
        Patch(facecolor="#d62728", label="Mitosis & Cell Cycle (G2M/E2F)"),
        Patch(facecolor="#9467bd", label="Stromal Invasion & ECM (MMP11)"),
        Patch(facecolor="#2ca02c", label="Metabolic / Luminal Profile")
    ]
    ax.legend(handles=legend_elements, loc="lower right", frameon=True, fontsize=8.5)
    
    plt.tight_layout()
    out_path = FIG_DIR / "Figure_3_TreeSHAP_Feature_Importance.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved {out_path}")

def generate_figure_4_pathways():
    """Figure 4: MSigDB Hallmark Pathway Hazard Ratios Forest Plot."""
    pathways = [
        ("Hallmark G2M Checkpoint", 1.249, 1.137, 1.372, "p = 4.29e-6"),
        ("Hallmark Invasion / EMT", 1.043, 0.950, 1.145, "p = 0.380"),
        ("Hallmark E2F Targets", 1.000, 0.910, 1.099, "p = 0.999"),
        ("Hallmark HER2 Amplicon", 1.000, 0.908, 1.101, "p = 0.999"),
        ("Hallmark Estrogen Response", 1.000, 0.912, 1.096, "p = 0.999"),
        ("Hallmark Apoptosis Regulation", 1.000, 0.909, 1.100, "p = 0.998"),
        ("Hallmark Macrophage / Immune", 1.000, 0.905, 1.105, "p = 0.998")
    ]
    
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    y_pos = np.arange(len(pathways))
    
    hrs = [p[1] for p in pathways]
    lowers = [p[2] for p in pathways]
    uppers = [p[3] for p in pathways]
    labels = [f"{p[0]} ({p[4]})" for p in pathways]
    
    xerr = [np.array(hrs) - np.array(lowers), np.array(uppers) - np.array(hrs)]
    
    ax.errorbar(hrs, y_pos, xerr=xerr, fmt="o", color="#1f77b4", ecolor="#1f77b4", elinewidth=2, capsize=4, markersize=7)
    ax.axvline(1.0, color="black", linestyle="--", alpha=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Hazard Ratio per 1-SD Increase in Pathway Activity (95% CI)", fontweight="bold")
    ax.set_title("Figure 4: Multivariable Pathway Survival Hazard Ratios (METABRIC ER+/HER2-)", fontweight="bold", pad=12)
    ax.grid(True, axis="x", linestyle="--", alpha=0.3)
    
    plt.tight_layout()
    out_path = FIG_DIR / "Figure_4_Hallmark_Pathway_Forest_Plot.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved {out_path}")

def main():
    print("Generating 300 DPI publication figures...")
    generate_figure_1_discrimination()
    generate_figure_2_dca()
    generate_figure_3_shap()
    generate_figure_4_pathways()
    print("All 4 publication figures generated successfully in figures/")

if __name__ == "__main__":
    main()
