"""
Model B: Molecular Baseline Models.
Implements:
1. Oncotype DX 21-gene surrogate Recurrence Score (Paik et al., NEJM 2004).
2. PAM50 Proliferation and Subtype Correlation (Parker et al., JCO 2009).
3. Elastic-Net Regularized Cox Proportional Hazards on Gene Expression.
"""

from __future__ import annotations
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import KFold

logger = logging.getLogger("RecurLens.ModelB")

def compute_oncotype_surrogate_score(expr_df: pd.DataFrame) -> pd.Series:
    """
    Compute Oncotype DX 21-gene surrogate recurrence score.
    Reference: Paik et al., N Engl J Med 2004; 351:2817-2826.
    Uses available normalized z-scores for module genes.
    """
    df = expr_df.copy()
    
    # Proliferation group (5 genes)
    prolif_genes = [g for g in ["MKI67", "AURKA", "BIRC5", "CCNB1", "MYBL2"] if g in df.columns]
    prolif_score = df[prolif_genes].mean(axis=1) if prolif_genes else 0.0
    
    # Estrogen group (4 genes)
    er_genes = [g for g in ["ESR1", "PGR", "BCL2", "SCUBE2"] if g in df.columns]
    er_score = df[er_genes].mean(axis=1) if er_genes else 0.0
    
    # Invasion group (2 genes)
    inv_genes = [g for g in ["MMP11", "CTSL2"] if g in df.columns]
    inv_score = df[inv_genes].mean(axis=1) if inv_genes else 0.0
    
    # HER2 group (2 genes)
    her2_genes = [g for g in ["GRB7", "ERBB2"] if g in df.columns]
    her2_score = df[her2_genes].mean(axis=1) if her2_genes else 0.0
    
    # Single genes
    cd68 = df["CD68"] if "CD68" in df.columns else 0.0
    gstm1 = df["GSTM1"] if "GSTM1" in df.columns else 0.0
    bag1 = df["BAG1"] if "BAG1" in df.columns else 0.0
    
    # Unscaled RS formula
    rs_unscaled = (
        0.73 * prolif_score
        - 0.28 * er_score
        + 0.47 * her2_score
        + 0.05 * inv_score
        + 0.11 * cd68
        - 0.08 * gstm1
        - 0.07 * bag1
    )
    rs_unscaled.name = "ONCOTYPE_SURROGATE_RS"
    return rs_unscaled


def compute_pam50_proliferation_index(expr_df: pd.DataFrame) -> pd.Series:
    """
    Compute PAM50 proliferation signature index (mean of mitotic/proliferation genes).
    Reference: Parker et al., J Clin Oncol 2009; Nielsen et al., Clin Cancer Res 2010.
    """
    prolif_pam50 = [
        "BIRC5", "CCNB1", "CDC20", "CDH3", "CENPF", "CEP55", "EXO1", 
        "KIF2C", "KNTC2", "MELK", "MKI67", "MYBL2", "NDC80", "ORC6", "PTTG1", "RRM2", "TYMS", "UBE2C"
    ]
    avail_genes = [g for g in prolif_pam50 if g in expr_df.columns]
    logger.info("Found %d / %d PAM50 proliferation genes", len(avail_genes), len(prolif_pam50))
    score = expr_df[avail_genes].mean(axis=1)
    score.name = "PAM50_PROLIFERATION_INDEX"
    return score


def fit_molecular_cox_model(
    merged_df: pd.DataFrame, 
    gene_cols: list[str], 
    duration_col: str = "RFS_MONTHS", 
    event_col: str = "RFS_EVENT",
    penalizer: float = 0.1
) -> tuple[CoxPHFitter, float, pd.Series]:
    """Fit regularized Model B (Molecular-only) Cox Proportional Hazards model."""
    data = merged_df[gene_cols + [duration_col, event_col]].dropna().copy()
    cph = CoxPHFitter(penalizer=penalizer, l1_ratio=0.5)
    cph.fit(data, duration_col=duration_col, event_col=event_col)
    
    risk_scores = cph.predict_partial_hazard(data)
    c_idx = concordance_index(data[duration_col], -risk_scores, data[event_col])
    logger.info("Model B (Elastic-Net Cox) Concordance Index: %.4f (N = %d, Genes = %d)", 
                c_idx, len(data), len(gene_cols))
    return cph, float(c_idx), risk_scores
