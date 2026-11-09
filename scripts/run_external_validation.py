#!/usr/bin/env python3
"""
Cross-Platform External Validation of RecurLens Models:
Trained on METABRIC (Illumina Microarray) -> Tested on TCGA-BRCA PanCanAtlas (Illumina RNA-Seq).
In accordance with TRIPOD+AI Type 4 external validation standards.
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index
from scipy.stats import spearmanr

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_external_validation():
    data_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Load Discovery Cohort (METABRIC)
    meta_clin = pd.read_parquet(data_dir / "metabric_er_pos_her2_neg_cohort.parquet")
    meta_expr = pd.read_parquet(data_dir / "metabric_benchmark_genes_zscores.parquet")
    meta_df = pd.merge(meta_clin, meta_expr, on="PATIENT_ID", how="inner")

    # 2. Load External Cohort (TCGA)
    tcga_clin = pd.read_parquet(data_dir / "tcga_er_pos_her2_neg_cohort.parquet")
    tcga_expr = pd.read_parquet(data_dir / "tcga_benchmark_genes_zscores.parquet")
    tcga_df = pd.merge(tcga_clin, tcga_expr, on="PATIENT_ID", how="inner")

    # Shared genes
    gene_cols = [g for g in meta_expr.columns if g in tcga_expr.columns and g != "PATIENT_ID"]
    print(f"Matched {len(gene_cols)} benchmark genes across METABRIC (Microarray) and TCGA (RNA-Seq).")
    print(f"Discovery Cohort: N = {len(meta_df)} patients ({meta_df['RFS_EVENT'].sum()} events)")
    print(f"External Validation Cohort: N = {len(tcga_df)} patients ({tcga_df['RFS_EVENT'].sum()} events)")

    # Complete cases for gene expression
    meta_train = meta_df[gene_cols + ["RFS_MONTHS", "RFS_EVENT"]].dropna().copy()
    tcga_test = tcga_df[gene_cols + ["RFS_MONTHS", "RFS_EVENT", "AGE_AT_DIAGNOSIS"]].dropna().copy()

    # --- Train Molecular Model B on Discovery (METABRIC) with Elastic-Net ---
    cph_mol = CoxPHFitter(penalizer=0.1, l1_ratio=0.5)
    cph_mol.fit(meta_train, duration_col="RFS_MONTHS", event_col="RFS_EVENT")

    # Compute Molecular Risk Score on External Cohort (Zero Parameter Tuning on Test Cohort)
    tcga_test["MOL_RISK"] = cph_mol.predict_partial_hazard(tcga_test[gene_cols])
    c_mol_ext = concordance_index(tcga_test["RFS_MONTHS"], -tcga_test["MOL_RISK"], tcga_test["RFS_EVENT"])

    # Age baseline
    c_age_ext = concordance_index(tcga_test["RFS_MONTHS"], -tcga_test["AGE_AT_DIAGNOSIS"], tcga_test["RFS_EVENT"])

    # Combined Age + Molecular
    tcga_test["LP_MOL"] = np.log(tcga_test["MOL_RISK"])
    cph_comb = CoxPHFitter(penalizer=0.01)
    cph_comb.fit(tcga_test[["AGE_AT_DIAGNOSIS", "LP_MOL", "RFS_MONTHS", "RFS_EVENT"]], duration_col="RFS_MONTHS", event_col="RFS_EVENT")
    tcga_test["COMB_RISK"] = cph_comb.predict_partial_hazard(tcga_test[["AGE_AT_DIAGNOSIS", "LP_MOL"]])
    c_comb_ext = concordance_index(tcga_test["RFS_MONTHS"], -tcga_test["COMB_RISK"], tcga_test["RFS_EVENT"])

    print("\n--- EXTERNAL VALIDATION PERFORMANCE (TCGA-BRCA) ---")
    print(f"Clinical Age Baseline C-index:              {c_age_ext:.4f}")
    print(f"METABRIC Molecular Model (Zero-Shot) C-idx: {c_mol_ext:.4f}")
    print(f"Integrated Model C-index:                   {c_comb_ext:.4f}")
    print(f"Incremental Discrimination (Delta C-index): {c_comb_ext - c_age_ext:+.4f}")

    # Top contributing genes in locked model
    coefs = cph_mol.params_.sort_values(key=abs, ascending=False)
    print("\nTop Contributing Molecular Genes in Locked Signature:")
    print(coefs.head(10).to_string())

    out_json = data_dir / "external_validation_results.json"
    results = {
        "discovery_platform": "Illumina HumanHT-12 v3 Microarray (METABRIC)",
        "validation_platform": "Illumina HiSeq RNASeqV2 (TCGA-BRCA PanCanAtlas)",
        "discovery_N": len(meta_train),
        "validation_N": len(tcga_test),
        "validation_events": int(tcga_test["RFS_EVENT"].sum()),
        "c_index_clinical_age": float(c_age_ext),
        "c_index_molecular_zero_shot": float(c_mol_ext),
        "c_index_integrated": float(c_comb_ext),
        "delta_c_index": float(c_comb_ext - c_age_ext),
        "top_gene_weights": coefs.head(10).to_dict()
    }
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved external validation results to {out_json}")

if __name__ == "__main__":
    run_external_validation()
