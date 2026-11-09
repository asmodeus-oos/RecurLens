"""
Model C: Integrated Multimodal Survival Architecture and Incremental Testing.
In accordance with TRIPOD+AI, Vickers et al. (DCA), and Pencina et al. (NRI/IDI).
"""

from __future__ import annotations
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index

logger = logging.getLogger("RecurLens.ModelC")

def compute_likelihood_ratio_test(ll_nested: float, ll_full: float, df: int) -> tuple[float, float]:
    """
    Compute Likelihood Ratio Test between nested models.
    LR = 2 * (log_likelihood_full - log_likelihood_nested) ~ Chi2(df)
    """
    lr_stat = 2.0 * (ll_full - ll_nested)
    p_val = 1.0 - chi2.cdf(lr_stat, df=df)
    return float(lr_stat), float(p_val)


def bootstrap_delta_c_index(
    df: pd.DataFrame,
    pred_a_col: str,
    pred_c_col: str,
    duration_col: str = "RFS_MONTHS",
    event_col: str = "RFS_EVENT",
    n_bootstraps: int = 500,
    random_state: int = 42
) -> dict[str, float]:
    """
    Calculate bootstrap 95% confidence interval for Delta C-index (Model C - Model A).
    """
    rng = np.random.RandomState(random_state)
    n = len(df)
    deltas = []
    
    for _ in range(n_bootstraps):
        idx = rng.choice(n, size=n, replace=True)
        boot_df = df.iloc[idx]
        if boot_df[event_col].sum() == 0:
            continue
        c_a = concordance_index(boot_df[duration_col], -boot_df[pred_a_col], boot_df[event_col])
        c_c = concordance_index(boot_df[duration_col], -boot_df[pred_c_col], boot_df[event_col])
        deltas.append(c_c - c_a)
        
    deltas = np.array(deltas)
    mean_delta = float(np.mean(deltas))
    ci_lower = float(np.percentile(deltas, 2.5))
    ci_upper = float(np.percentile(deltas, 97.5))
    p_value = float(np.mean(deltas <= 0))
    
    return {
        "mean_delta_c": mean_delta,
        "ci_95_lower": ci_lower,
        "ci_95_upper": ci_upper,
        "p_val_empirical": p_value
    }


def fit_and_evaluate_multimodal_experiment(
    clinical_file: Path,
    expression_file: Path,
    out_dir: Path | None = None
) -> dict:
    """
    Full Tri-Model Experiment Execution:
    1. Model A (Clinical-only)
    2. Model B (Molecular-only)
    3. Model C (Integrated)
    4. Incremental Utility Statistics
    """
    df_clin = pd.read_parquet(clinical_file)
    df_expr = pd.read_parquet(expression_file)

    # Merge on PATIENT_ID
    df_all = pd.merge(df_clin, df_expr, on="PATIENT_ID", how="inner")
    logger.info("Matched clinical + molecular records: %d patients", len(df_all))

    clin_covars = ["AGE_AT_DIAGNOSIS", "TUMOR_SIZE", "LYMPH_NODES_EXAMINED_POSITIVE", "GRADE"]
    gene_cols = [c for c in df_expr.columns if c != "PATIENT_ID"]
    
    duration_col = "RFS_MONTHS"
    event_col = "RFS_EVENT"

    analysis_df = df_all[clin_covars + gene_cols + [duration_col, event_col, "CTS5_SCORE"]].dropna().copy()
    logger.info("Complete case sample size for tri-model comparison: %d patients (%d events)", 
                len(analysis_df), analysis_df[event_col].sum())

    # --- 1. Model A: Clinical Baseline ---
    cph_a = CoxPHFitter(penalizer=0.01)
    cph_a.fit(analysis_df[clin_covars + [duration_col, event_col]], duration_col=duration_col, event_col=event_col)
    analysis_df["RISK_MODEL_A"] = cph_a.predict_partial_hazard(analysis_df[clin_covars])
    c_a = concordance_index(analysis_df[duration_col], -analysis_df["RISK_MODEL_A"], analysis_df[event_col])

    # --- 2. Model B: Molecular Baseline (Elastic-Net on Genes) ---
    cph_b = CoxPHFitter(penalizer=0.1, l1_ratio=0.5)
    cph_b.fit(analysis_df[gene_cols + [duration_col, event_col]], duration_col=duration_col, event_col=event_col)
    analysis_df["RISK_MODEL_B"] = cph_b.predict_partial_hazard(analysis_df[gene_cols])
    c_b = concordance_index(analysis_df[duration_col], -analysis_df["RISK_MODEL_B"], analysis_df[event_col])

    # --- 3. Model C: Integrated Multimodal (Late Fusion of Linear Predictors) ---
    # Combine log-partial-hazards (linear predictors)
    analysis_df["LP_CLIN"] = np.log(analysis_df["RISK_MODEL_A"])
    analysis_df["LP_MOL"] = np.log(analysis_df["RISK_MODEL_B"])

    cph_c = CoxPHFitter(penalizer=0.01)
    cph_c.fit(analysis_df[["LP_CLIN", "LP_MOL", duration_col, event_col]], duration_col=duration_col, event_col=event_col)
    analysis_df["RISK_MODEL_C"] = cph_c.predict_partial_hazard(analysis_df[["LP_CLIN", "LP_MOL"]])
    c_c = concordance_index(analysis_df[duration_col], -analysis_df["RISK_MODEL_C"], analysis_df[event_col])

    # --- 4. Incremental Utility Statistics ---
    delta_c = c_c - c_a
    # Likelihood Ratio Test between Model A and Model C
    # Model A log-likelihood:
    ll_a = cph_a.log_likelihood_
    # Fit full model with LP_MOL added to clinical features
    cph_nested = CoxPHFitter(penalizer=0.01)
    cph_nested.fit(analysis_df[clin_covars + ["LP_MOL", duration_col, event_col]], duration_col=duration_col, event_col=event_col)
    ll_full = cph_nested.log_likelihood_
    lr_stat, lr_p_val = compute_likelihood_ratio_test(ll_a, ll_full, df=1)

    boot_results = bootstrap_delta_c_index(analysis_df, "RISK_MODEL_A", "RISK_MODEL_C", duration_col, event_col)

    # Early vs Late Recurrence Horizon Dissection (<= 5 years vs > 5 years)
    early_df = analysis_df.copy()
    # In early window (<= 60 months), events after 60 are censored at 60
    early_df["RFS_EVENT_EARLY"] = np.where((early_df[duration_col] <= 60.0) & (early_df[event_col] == 1), 1, 0)
    early_df["RFS_MONTHS_EARLY"] = np.minimum(early_df[duration_col], 60.0)
    c_a_early = concordance_index(early_df["RFS_MONTHS_EARLY"], -early_df["RISK_MODEL_A"], early_df["RFS_EVENT_EARLY"])
    c_c_early = concordance_index(early_df["RFS_MONTHS_EARLY"], -early_df["RISK_MODEL_C"], early_df["RFS_EVENT_EARLY"])

    # Late recurrence (> 60 months among disease-free survivors at 5 years)
    late_df = analysis_df[analysis_df[duration_col] > 60.0].copy()
    late_df["RFS_MONTHS_LATE"] = late_df[duration_col] - 60.0
    c_a_late = concordance_index(late_df["RFS_MONTHS_LATE"], -late_df["RISK_MODEL_A"], late_df[event_col])
    c_c_late = concordance_index(late_df["RFS_MONTHS_LATE"], -late_df["RISK_MODEL_C"], late_df[event_col])

    results = {
        "N": len(analysis_df),
        "events": int(analysis_df[event_col].sum()),
        "c_index_model_a": float(c_a),
        "c_index_model_b": float(c_b),
        "c_index_model_c": float(c_c),
        "delta_c_index": float(delta_c),
        "bootstrap_ci_95": [boot_results["ci_95_lower"], boot_results["ci_95_upper"]],
        "bootstrap_p_val": boot_results["p_val_empirical"],
        "lr_test_stat": float(lr_stat),
        "lr_test_p_val": float(lr_p_val),
        "early_window_c_a": float(c_a_early),
        "early_window_c_c": float(c_c_early),
        "early_window_delta_c": float(c_c_early - c_a_early),
        "late_window_c_a": float(c_a_late),
        "late_window_c_c": float(c_c_late),
        "late_window_delta_c": float(c_c_late - c_a_late),
        "model_c_weights": {
            "gamma_clin": float(cph_c.params_["LP_CLIN"]),
            "gamma_mol": float(cph_c.params_["LP_MOL"]),
            "p_mol": float(cph_c.summary.loc["LP_MOL", "p"])
        }
    }

    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        analysis_df.to_parquet(out_dir / "tri_model_predictions.parquet")
        logger.info("Saved tri-model predictions to %s", out_dir / "tri_model_predictions.parquet")

    return results
