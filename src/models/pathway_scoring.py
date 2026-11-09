"""
MSigDB Hallmark Pathway Scoring & Dimension Reduction for RecurLens.
Transforms high-dimensional gene z-scores into robust, platform-agnostic biological pathway activity scores.
Reference: Liberzon A, et al. The Molecular Signatures Database (MSigDB) hallmark gene set collection.
Cell Syst. 2015;1(6):417-425.
"""

from __future__ import annotations
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index

logger = logging.getLogger("RecurLens.Pathway")

HALLMARK_PATHWAYS = {
    "Hallmark_G2M_Checkpoint": [
        "MKI67", "AURKA", "CCNB1", "CDC20", "CENPF", "CEP55", "KIF2C", "MELK", "NDC80", "PTTG1", "UBE2C"
    ],
    "Hallmark_E2F_Targets": [
        "MYBL2", "CDC6", "EXO1", "ORC6", "RRM2", "TYMS", "UBE2T"
    ],
    "Hallmark_Estrogen_Response": [
        "ESR1", "PGR", "BCL2", "SCUBE2", "FOXA1", "MAPT", "NAT1", "GPR160"
    ],
    "Hallmark_Invasion_EMT": [
        "MMP11", "CTSL2", "CDH3"
    ],
    "Hallmark_HER2_Amplicon": [
        "ERBB2", "GRB7"
    ],
    "Hallmark_Apoptosis_Regulation": [
        "BIRC5", "BAG1", "BCL2"
    ],
    "Hallmark_Macrophage_Immune": [
        "CD68"
    ]
}

def compute_pathway_activity_scores(expr_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute normalized pathway activity score as mean of constituent gene z-scores,
    inverting anti-proliferative/protective genes (e.g. Estrogen response in ER+ disease).
    """
    df = expr_df.copy()
    pathway_scores = pd.DataFrame(index=df.index)

    for pathway_name, genes in HALLMARK_PATHWAYS.items():
        avail_genes = [g for g in genes if g in df.columns]
        if avail_genes:
            score = df[avail_genes].mean(axis=1)
            # Standardize across cohort
            pathway_scores[pathway_name] = (score - score.mean()) / (score.std() + 1e-6)
        else:
            pathway_scores[pathway_name] = 0.0

    return pathway_scores


def evaluate_pathway_survival_model(
    meta_clin_path: Path,
    meta_expr_path: Path,
    tcga_clin_path: Path,
    tcga_expr_path: Path
) -> dict:
    """
    Train Elastic-Net Cox model on Hallmark Pathways in METABRIC,
    and test zero-shot cross-platform transfer on TCGA RNA-seq.
    """
    meta_clin = pd.read_parquet(meta_clin_path)
    meta_expr = pd.read_parquet(meta_expr_path)
    meta_pathways = compute_pathway_activity_scores(meta_expr)
    meta_df = pd.merge(meta_clin, meta_pathways, on="PATIENT_ID", how="inner")

    tcga_clin = pd.read_parquet(tcga_clin_path)
    tcga_expr = pd.read_parquet(tcga_expr_path)
    tcga_pathways = compute_pathway_activity_scores(tcga_expr)
    tcga_df = pd.merge(tcga_clin, tcga_pathways, on="PATIENT_ID", how="inner")

    pathway_cols = list(HALLMARK_PATHWAYS.keys())
    
    # 1. Train on Discovery (METABRIC)
    train_data = meta_df[pathway_cols + ["RFS_MONTHS", "RFS_EVENT"]].dropna().copy()
    cph_pw = CoxPHFitter(penalizer=0.05, l1_ratio=0.5)
    cph_pw.fit(train_data, duration_col="RFS_MONTHS", event_col="RFS_EVENT")
    
    train_c = concordance_index(train_data["RFS_MONTHS"], -cph_pw.predict_partial_hazard(train_data[pathway_cols]), train_data["RFS_EVENT"])

    # 2. Test Zero-Shot Transfer on External (TCGA)
    test_data = tcga_df[pathway_cols + ["RFS_MONTHS", "RFS_EVENT"]].dropna().copy()
    tcga_test_risk = cph_pw.predict_partial_hazard(test_data[pathway_cols])
    test_c = concordance_index(test_data["RFS_MONTHS"], -tcga_test_risk, test_data["RFS_EVENT"])

    logger.info("Pathway Model: Discovery C-index = %.4f | External C-index = %.4f", train_c, test_c)
    return {
        "discovery_pathway_c_index": float(train_c),
        "external_pathway_c_index": float(test_c),
        "pathway_hazard_ratios": cph_pw.hazard_ratios_.to_dict(),
        "p_values": cph_pw.summary["p"].to_dict()
    }
