"""
Explainable AI (XAI) Pipeline for RecurLens / GeneLens AI.
Uses TreeSHAP to attribute 5-year recurrence predictions to specific clinical parameters and biological pathways.
Reference: Lundberg SM, et al. From local explanations to global understanding with explainable AI for trees.
Nature Machine Intelligence. 2020;2(1):56-67.
"""

from __future__ import annotations
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import GradientBoostingClassifier

logger = logging.getLogger("RecurLens.XAI")

GENE_PATHWAY_MAP = {
    # Cell Cycle / Proliferation / Mitosis (E2F Targets, G2M Checkpoint)
    "MKI67": "Hallmark G2M Checkpoint / Mitosis",
    "AURKA": "Hallmark G2M Checkpoint / Centrosome",
    "BIRC5": "Hallmark Apoptosis Evasion / Mitosis",
    "CCNB1": "Hallmark Cell Cycle / G2-M Phase",
    "MYBL2": "Hallmark E2F Targets / Proliferation",
    "CDC20": "Hallmark Mitotic Spindle Assembly",
    "CDC6": "Hallmark DNA Replication Origin",
    "CENPF": "Hallmark Centromere / Chromosome Segregation",
    "CEP55": "Hallmark Cytokinesis Regulation",
    "EXO1": "Hallmark DNA Mismatch Repair",
    "KIF2C": "Hallmark Mitotic Spindle Motor",
    "MELK": "Hallmark Proliferation Signaling",
    "NDC80": "Hallmark Kinetochore Complex",
    "NUF2": "Hallmark Kinetochore Complex",
    "ORC6": "Hallmark DNA Pre-Replication",
    "PTTG1": "Hallmark Securin / Chromosome Stability",
    "RRM2": "Hallmark DNA Synthesis & Ribonucleotide Reductase",
    "TYMS": "Hallmark Folate Metabolism / Thymidylate Synthase",
    "UBE2C": "Hallmark Ubiquitin Conjugation / Anaphase",
    "UBE2T": "Hallmark DNA Crosslink Repair",
    # Hormone Signaling / Estrogen Response
    "ESR1": "Hallmark Estrogen Response Early/Late",
    "PGR": "Hallmark Progesterone Receptor Signaling",
    "BCL2": "Hallmark Anti-Apoptosis / Estrogen Dependent",
    "SCUBE2": "Hallmark Estrogen-Regulated Cell Adhesion",
    "FOXA1": "Hallmark Pioneer Factor for Estrogen Receptor",
    "MAPT": "Hallmark Microtubule Stability / Luminal A",
    "BAG1": "Hallmark Anti-Apoptosis / Chaperone",
    "NAT1": "Hallmark Luminal Differentiation / Metabolism",
    # Receptor Tyrosine Kinase / Growth Factor Signaling
    "ERBB2": "Hallmark HER2 Amplicon / Receptor Kinase",
    "GRB7": "Hallmark 17q12 Amplicon / RTK Signaling",
    "EGFR": "Hallmark EGFR / Basal-like Signaling",
    "FGFR4": "Hallmark Fibroblast Growth Factor Signaling",
    # Extracellular Matrix & Invasion
    "MMP11": "Hallmark Extracellular Matrix Degradation / Stromal Invasion",
    "CTSL2": "Hallmark Lysosomal Protease / Invasion",
    "CDH3": "Hallmark P-Cadherin / Cell Adhesion",
    # Immune & Basal Markers
    "CD68": "Hallmark Tumor-Associated Macrophages",
    "KRT5": "Hallmark Basal / Cytokeratin 5",
    "KRT14": "Hallmark Basal / Cytokeratin 14",
    "KRT17": "Hallmark Basal / Cytokeratin 17",
    "SFRP1": "Hallmark Wnt Signaling Regulation"
}

def run_shap_explainability_pipeline(data_dir: Path, landmark_months: float = 60.0) -> pd.DataFrame:
    """Train Gradient Boosting on 5-year recurrence, calculate exact TreeSHAP values, and map to pathways."""
    df_clin = pd.read_parquet(data_dir / "metabric_er_pos_her2_neg_cohort.parquet")
    df_expr = pd.read_parquet(data_dir / "metabric_benchmark_genes_zscores.parquet")

    df = pd.merge(df_clin, df_expr, on="PATIENT_ID", how="inner")
    
    # 5-year event definition
    valid_mask = (df["RFS_MONTHS"] > landmark_months) | (df["RFS_EVENT"] == 1)
    df = df[valid_mask].copy()
    y = np.where((df["RFS_MONTHS"] <= landmark_months) & (df["RFS_EVENT"] == 1), 1, 0)
    
    clin_cols = ["AGE_AT_DIAGNOSIS", "TUMOR_SIZE", "LYMPH_NODES_EXAMINED_POSITIVE", "GRADE"]
    gene_cols = [c for c in df_expr.columns if c != "PATIENT_ID"]
    all_feature_cols = clin_cols + gene_cols
    
    X = df[all_feature_cols].copy()
    # Impute median for missing values
    X = X.fillna(X.median())

    logger.info("Training Gradient Boosting model for SHAP attribution (N = %d, Features = %d)...", len(X), len(all_feature_cols))
    model = GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, random_state=42)
    model.fit(X, y)

    # Compute TreeSHAP values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    
    # In binary classification, check shape
    if isinstance(shap_values, list) and len(shap_values) == 2:
        vals = shap_values[1]
    elif len(shap_values.shape) == 3 and shap_values.shape[2] == 2:
        vals = shap_values[:, :, 1]
    else:
        vals = shap_values

    # Global feature importance = Mean absolute SHAP value
    mean_abs_shap = np.mean(np.abs(vals), axis=0)
    
    records = []
    for col_name, shap_val in zip(all_feature_cols, mean_abs_shap):
        is_clin = col_name in clin_cols
        pathway = "Clinicopathological Staging Parameter" if is_clin else GENE_PATHWAY_MAP.get(col_name, "Molecular / Transcriptomic Profile")
        records.append({
            "Feature": col_name,
            "Type": "Clinical" if is_clin else "Molecular",
            "Mean_Abs_SHAP": float(shap_val),
            "Biological_Pathway_Context": pathway
        })

    shap_df = pd.DataFrame(records).sort_values("Mean_Abs_SHAP", ascending=False).reset_index(drop=True)
    shap_df["Rank"] = shap_df.index + 1
    
    out_csv = data_dir / "shap_feature_attributions.csv"
    shap_df.to_csv(out_csv, index=False)
    logger.info("Saved top SHAP feature attributions to %s", out_csv)
    
    return shap_df
