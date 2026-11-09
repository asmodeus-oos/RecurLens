#!/usr/bin/env python3
"""Execute Tri-Model Comparative Experiment (Model A vs B vs C) per Study Protocol."""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.integrated_model import fit_and_evaluate_multimodal_experiment

def main():
    data_dir = PROJECT_ROOT / "data" / "processed"
    clinical_file = data_dir / "metabric_er_pos_her2_neg_cohort.parquet"
    expression_file = data_dir / "metabric_benchmark_genes_zscores.parquet"

    print("=" * 60)
    print("RecurLens: Tri-Model Empirical Evaluation (TRIPOD+AI)")
    print("=" * 60)

    results = fit_and_evaluate_multimodal_experiment(clinical_file, expression_file, out_dir=data_dir)

    print("\n--- RESULTS SUMMARY ---")
    print(f"Sample Size (N): {results['N']} patients ({results['events']} recurrence events)")
    print(f"Model A (Clinical-only) C-index:    {results['c_index_model_a']:.4f}")
    print(f"Model B (Molecular-only) C-index:   {results['c_index_model_b']:.4f}")
    print(f"Model C (Integrated) C-index:       {results['c_index_model_c']:.4f}")
    print(f"Delta C-index (C - A):              {results['delta_c_index']:+.4f} (95% CI: [{results['bootstrap_ci_95'][0]:+.4f}, {results['bootstrap_ci_95'][1]:+.4f}])")
    print(f"Bootstrap p-value:                  {results['bootstrap_p_val']:.4f}")
    print(f"Likelihood Ratio Test (Model C vs A): Delta LR-Chi2 = {results['lr_test_stat']:.2f}, p-value = {results['lr_test_p_val']:.4e}")

    print("\n--- TEMPORAL HORIZON ANALYSIS ---")
    print(f"Early Window (<= 5 years): Clinical = {results['early_window_c_a']:.4f}, Integrated = {results['early_window_c_c']:.4f}, Delta = {results['early_window_delta_c']:+.4f}")
    print(f"Late Window  (> 5 years):  Clinical = {results['late_window_c_a']:.4f}, Integrated = {results['late_window_c_c']:.4f}, Delta = {results['late_window_delta_c']:+.4f}")

    print("\n--- MULTIMODAL WEIGHTING ---")
    print(f"Clinical Linear Predictor Weight (gamma_clin): {results['model_c_weights']['gamma_clin']:.4f}")
    print(f"Molecular Linear Predictor Weight (gamma_mol):  {results['model_c_weights']['gamma_mol']:.4f} (p = {results['model_c_weights']['p_mol']:.4e})")

    # Save results json
    results_path = data_dir / "tri_model_benchmark_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved benchmark results to {results_path}")

if __name__ == "__main__":
    main()
