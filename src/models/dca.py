"""
Decision Curve Analysis (DCA) for RecurLens / GeneLens AI.
Reference: Vickers AJ, Elkin EB. Decision curve analysis: a novel method for evaluating executive prediction models.
Med Decis Making. 2006;26(6):565-574.
"""

from __future__ import annotations
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter

logger = logging.getLogger("RecurLens.DCA")

def compute_5yr_risk_probabilities(
    df: pd.DataFrame,
    features: list[str],
    duration_col: str = "RFS_MONTHS",
    event_col: str = "RFS_EVENT",
    landmark_time: float = 60.0,
    penalizer: float = 0.01
) -> np.ndarray:
    """Fit Cox model and return predicted 5-year failure probabilities 1 - S(60 | x)."""
    cph = CoxPHFitter(penalizer=penalizer)
    data = df[features + [duration_col, event_col]].dropna().copy()
    cph.fit(data, duration_col=duration_col, event_col=event_col)
    
    # Baseline cumulative hazard H0(t)
    baseline_hazard = cph.baseline_cumulative_hazard_
    # Find hazard at landmark_time (60 months)
    closest_time_idx = baseline_hazard.index.asof(landmark_time)
    h0_60 = float(baseline_hazard.loc[closest_time_idx].iloc[0])
    s0_60 = np.exp(-h0_60)
    
    partial_hazards = cph.predict_partial_hazard(df[features]).values.flatten()
    pred_risk = 1.0 - (s0_60 ** partial_hazards)
    return np.clip(pred_risk, 0.0, 1.0)


def calculate_dca_table(
    y_true: np.ndarray,
    pred_risks: dict[str, np.ndarray],
    thresholds: np.ndarray | None = None
) -> pd.DataFrame:
    """Calculate Net Benefit across clinical threshold range."""
    if thresholds is None:
        thresholds = np.linspace(0.05, 0.35, 31)

    n = len(y_true)
    event_rate = np.mean(y_true)
    records = []

    for pt in thresholds:
        weight = pt / (1.0 - pt)
        
        # Treat None
        nb_none = 0.0
        
        # Treat All
        nb_all = event_rate - (1.0 - event_rate) * weight
        
        row = {
            "threshold": float(pt),
            "Treat_None": float(nb_none),
            "Treat_All": float(nb_all)
        }
        
        for model_name, p_hat in pred_risks.items():
            treat = (p_hat >= pt).astype(int)
            tp = np.sum((treat == 1) & (y_true == 1))
            fp = np.sum((treat == 1) & (y_true == 0))
            nb = (tp / n) - (fp / n) * weight
            row[model_name] = float(nb)
            
        records.append(row)

    return pd.DataFrame(records)


def run_decision_curve_analysis(data_dir: Path, landmark_months: float = 60.0) -> pd.DataFrame:
    """Execute complete DCA for Model A (Clinical), Model B (Molecular), and Model C (Integrated)."""
    df = pd.read_parquet(data_dir / "tri_model_predictions.parquet")
    
    # Filter complete cases at landmark
    valid_mask = (df["RFS_MONTHS"] > landmark_months) | (df["RFS_EVENT"] == 1)
    df_eval = df[valid_mask].copy()
    y_true = np.where((df_eval["RFS_MONTHS"] <= landmark_months) & (df_eval["RFS_EVENT"] == 1), 1, 0)
    logger.info("DCA cohort at %d months: N = %d, Events = %d (%.1f%%)", 
                landmark_months, len(df_eval), np.sum(y_true), np.mean(y_true) * 100)

    # 1. Model A risk
    clin_cols = ["AGE_AT_DIAGNOSIS", "TUMOR_SIZE", "LYMPH_NODES_EXAMINED_POSITIVE", "GRADE"]
    risk_a = compute_5yr_risk_probabilities(df_eval, clin_cols, landmark_time=landmark_months)

    # 2. Model B risk (using LP_MOL)
    risk_b = compute_5yr_risk_probabilities(df_eval, ["LP_MOL"], landmark_time=landmark_months)

    # 3. Model C risk (using LP_CLIN and LP_MOL)
    risk_c = compute_5yr_risk_probabilities(df_eval, ["LP_CLIN", "LP_MOL"], landmark_time=landmark_months)

    pred_dict = {
        "Model_A_Clinical": risk_a,
        "Model_B_Molecular": risk_b,
        "Model_C_Integrated": risk_c
    }

    thresholds = np.linspace(0.08, 0.30, 23)
    dca_df = calculate_dca_table(y_true, pred_dict, thresholds=thresholds)

    # Save CSV
    out_csv = data_dir / "dca_net_benefit.csv"
    dca_df.to_csv(out_csv, index=False)
    logger.info("Saved DCA net benefit table to %s", out_csv)

    # Plot figure
    plt.figure(figsize=(8, 6), dpi=150)
    plt.plot(dca_df["threshold"], dca_df["Treat_All"], label="Treat All", linestyle="--", color="gray", alpha=0.7)
    plt.plot(dca_df["threshold"], dca_df["Treat_None"], label="Treat None", linestyle=":", color="black")
    plt.plot(dca_df["threshold"], dca_df["Model_A_Clinical"], label="Model A (Clinical Baseline)", color="#1f77b4", linewidth=2)
    plt.plot(dca_df["threshold"], dca_df["Model_B_Molecular"], label="Model B (Molecular Baseline)", color="#ff7f0e", linewidth=2)
    plt.plot(dca_df["threshold"], dca_df["Model_C_Integrated"], label="Model C (Integrated RecurLens)", color="#2ca02c", linewidth=2.5)

    plt.xlabel("Threshold Probability of 5-Year Recurrence ($p_t$)", fontsize=11)
    plt.ylabel("Net Benefit", fontsize=11)
    plt.title("Decision Curve Analysis: 5-Year Recurrence Risk (METABRIC ER+/HER2-)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.ylim(-0.02, max(dca_df["Model_C_Integrated"]) * 1.25)
    plt.legend(loc="upper right", frameon=True)
    plt.tight_layout()

    out_png = data_dir / "dca_net_benefit_curve.png"
    plt.savefig(out_png)
    plt.close()
    logger.info("Saved DCA plot to %s", out_png)

    return dca_df
