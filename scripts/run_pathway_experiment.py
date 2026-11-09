#!/usr/bin/env python3
"""Run Pathway-Level (MSigDB Hallmark) Survival Modeling for RecurLens."""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.pathway_scoring import evaluate_pathway_survival_model

def main():
    data_dir = PROJECT_ROOT / "data" / "processed"
    meta_clin = data_dir / "metabric_er_pos_her2_neg_cohort.parquet"
    meta_expr = data_dir / "metabric_benchmark_genes_zscores.parquet"
    tcga_clin = data_dir / "tcga_er_pos_her2_neg_cohort.parquet"
    tcga_expr = data_dir / "tcga_benchmark_genes_zscores.parquet"

    print("=" * 60)
    print("RecurLens: MSigDB Hallmark Pathway-Level Evaluation")
    print("=" * 60)

    results = evaluate_pathway_survival_model(meta_clin, meta_expr, tcga_clin, tcga_expr)

    print("\n--- PATHWAY MODEL PERFORMANCE ---")
    print(f"Discovery (METABRIC) Pathway Model C-index: {results['discovery_pathway_c_index']:.4f}")
    print(f"External (TCGA) Pathway Model C-index:    {results['external_pathway_c_index']:.4f}")

    print("\n--- BIOLOGICAL PATHWAY HAZARD RATIOS (METABRIC) ---")
    for pw, hr in sorted(results["pathway_hazard_ratios"].items(), key=lambda x: x[1], reverse=True):
        p_val = results["p_values"].get(pw, 1.0)
        sig = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else ""))
        print(f"{pw:<35}: HR = {hr:.3f} (p = {p_val:.4e}) {sig}")

    out_file = data_dir / "pathway_benchmark_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved pathway benchmark results to {out_file}")

if __name__ == "__main__":
    main()
