"""
Model A: Clinical Baseline Survival Models (CTS5 benchmark and Cox Proportional Hazards).
Evaluates discrimination (Harrell's C-index) and calibration on ER+/HER2- breast cancer recurrence.
"""

from __future__ import annotations
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index

logger = logging.getLogger("RecurLens.ModelA")

def fit_clinical_cox_model(df: pd.DataFrame, duration_col: str = "RFS_MONTHS", event_col: str = "RFS_EVENT") -> tuple[CoxPHFitter, float]:
    """
    Fit Model A (Clinicopathological baseline Cox Proportional Hazards).
    Features: AGE_AT_DIAGNOSIS, TUMOR_SIZE, LYMPH_NODES_EXAMINED_POSITIVE, GRADE.
    """
    cols = ["AGE_AT_DIAGNOSIS", "TUMOR_SIZE", "LYMPH_NODES_EXAMINED_POSITIVE", "GRADE", duration_col, event_col]
    clean_df = df[cols].dropna().copy()
    
    cph = CoxPHFitter(penalizer=0.01)
    cph.fit(clean_df, duration_col=duration_col, event_col=event_col)
    
    # Calculate Harrell's C-index
    risk_scores = cph.predict_partial_hazard(clean_df)
    c_idx = concordance_index(clean_df[duration_col], -risk_scores, clean_df[event_col])
    
    logger.info("Model A (Fitted Cox-PH) Concordance Index: %.4f (N = %d, Events = %d)", 
                c_idx, len(clean_df), clean_df[event_col].sum())
    return cph, float(c_idx)

def evaluate_cts5_benchmark(df: pd.DataFrame, duration_col: str = "RFS_MONTHS", event_col: str = "RFS_EVENT") -> float:
    """Evaluate pre-computed CTS5 score discrimination without fitting parameters."""
    clean_df = df[["CTS5_SCORE", duration_col, event_col]].dropna().copy()
    # Higher CTS5 = higher risk -> negative score for concordance_index
    c_idx = concordance_index(clean_df[duration_col], -clean_df["CTS5_SCORE"], clean_df[event_col])
    logger.info("Model A Benchmark (Fixed CTS5) Concordance Index: %.4f (N = %d, Events = %d)", 
                c_idx, len(clean_df), clean_df[event_col].sum())
    return float(c_idx)
