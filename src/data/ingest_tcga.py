"""
TCGA-BRCA PanCanAtlas 2018 External Validation Cohort Ingestion.
Extracts RNA-seq expression and curated Disease-Free Survival / Progression-Free Survival endpoints.
"""

from __future__ import annotations
import logging
from pathlib import Path
import urllib.request
import pandas as pd
import numpy as np
from src.data.ingest_metabric import PAM50_GENES, ONCOTYPE_GENES, load_cbioportal_tsv, download_file_with_progress

logger = logging.getLogger("RecurLens.IngestTCGA")

BASE_URL = "https://media.githubusercontent.com/media/cBioPortal/datahub/master/public/brca_tcga_pan_can_atlas_2018"
CLINICAL_PATIENT_URL = f"{BASE_URL}/data_clinical_patient.txt"
CLINICAL_SAMPLE_URL = f"{BASE_URL}/data_clinical_sample.txt"
MRNA_RNASEQ_URL = f"{BASE_URL}/data_mrna_seq_v2_rsem_zscores_ref_diploid_samples.txt"

def process_tcga_cohort(patient_file: Path, sample_file: Path, out_path: Path) -> pd.DataFrame:
    """Filter TCGA-BRCA cohort to Luminal A/B early-stage cases with DFS/PFS follow-up."""
    logger.info("Processing TCGA-BRCA PanCanAtlas clinical data...")
    df_patient = load_cbioportal_tsv(patient_file)
    df_sample = load_cbioportal_tsv(sample_file)

    df_patient["PATIENT_ID"] = df_patient["PATIENT_ID"].astype(str).str.strip()
    df_sample["PATIENT_ID"] = df_sample["PATIENT_ID"].astype(str).str.strip()
    df_sample["SAMPLE_ID"] = df_sample["SAMPLE_ID"].astype(str).str.strip()

    merged = pd.merge(df_patient, df_sample, on="PATIENT_ID", how="inner")
    
    # Filter: Female, Luminal A or Luminal B (ER+/HER2-)
    merged = merged[merged["SEX"].astype(str).str.lower().str.startswith("f")]
    merged = merged[merged["SUBTYPE"].isin(["BRCA_LumA", "BRCA_LumB"])]
    
    # Stage I-II filter (T1-T2, N0-N1)
    if "PATH_T_STAGE" in merged.columns:
        t_ok = merged["PATH_T_STAGE"].str.upper().isin(["T1", "T1A", "T1B", "T1C", "T2", "TX"])
        merged = merged[t_ok | merged["PATH_T_STAGE"].isna()]
        
    if "PATH_N_STAGE" in merged.columns:
        n_ok = merged["PATH_N_STAGE"].str.upper().isin(["N0", "N0 (I-)", "N0 (I+)", "N0 (MOL+)", "N1", "N1A", "N1B", "N1C", "N1MI", "NX"])
        merged = merged[n_ok | merged["PATH_N_STAGE"].isna()]

    # Numeric age
    merged["AGE_AT_DIAGNOSIS"] = pd.to_numeric(merged["AGE"], errors="coerce")
    
    # Recurrence endpoint: Progression Free Survival (PFS) or Disease Free Survival (DFS)
    merged["RFS_MONTHS"] = pd.to_numeric(merged["PFS_MONTHS"], errors="coerce")
    merged["RFS_EVENT"] = merged["PFS_STATUS"].astype(str).apply(
        lambda s: 1 if "1" in s or "prog" in s.lower() else (0 if "0" in s or "cens" in s.lower() else np.nan)
    )
    
    # Require positive follow-up
    merged = merged[merged["RFS_MONTHS"].notna() & (merged["RFS_MONTHS"] > 0) & merged["RFS_EVENT"].notna()]
    merged["RFS_EVENT"] = merged["RFS_EVENT"].astype(int)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(out_path, index=False)
    merged.to_csv(out_path.with_suffix(".csv"), index=False)
    logger.info("Saved filtered TCGA cohort (%d patients, %d events) to %s", len(merged), merged["RFS_EVENT"].sum(), out_path)
    return merged


def extract_tcga_gene_matrix(expression_file: Path, target_samples: set[str], out_path: Path) -> pd.DataFrame:
    """Extract benchmark gene expressions from TCGA RNA-seq matrix."""
    logger.info("Extracting TCGA RNA-seq benchmark gene matrix...")
    all_target_genes = set(PAM50_GENES + ONCOTYPE_GENES)
    
    extracted_rows = []
    with open(expression_file, "r", encoding="utf-8", errors="replace") as f:
        header_line = f.readline().strip().split("\t")
        col_names = [col.strip() for col in header_line]
        
        # In TCGA, sample column names are e.g. TCGA-3C-AAAU-01; map to PATIENT_ID (first 12 chars)
        sample_patient_map = {}
        for idx, col in enumerate(col_names[2:], start=2):
            pat_id = "-".join(col.split("-")[:3])
            if pat_id in target_samples and pat_id not in sample_patient_map:
                sample_patient_map[pat_id] = idx

        target_pat_ids = list(sample_patient_map.keys())
        target_indices = [sample_patient_map[p] for p in target_pat_ids]
        
        for line in f:
            parts = line.strip().split("\t")
            gene = parts[0].strip()
            if gene in all_target_genes:
                vals = [float(parts[i]) if parts[i] not in ("NA", "null", "") else np.nan for i in target_indices]
                extracted_rows.append([gene] + vals)

    df_raw = pd.DataFrame(extracted_rows, columns=["Hugo_Symbol"] + target_pat_ids)
    df_grouped = df_raw.groupby("Hugo_Symbol").mean()
    df_expr = df_grouped.T
    df_expr.index.name = "PATIENT_ID"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_expr.to_parquet(out_path)
    df_expr.to_csv(out_path.with_suffix(".csv"))
    logger.info("Saved TCGA benchmark gene matrix (%d patients x %d genes) to %s", len(df_expr), df_expr.shape[1], out_path)
    return df_expr


def main(data_dir: Path | None = None):
    if data_dir is None:
        data_dir = Path("/home/vlad/Projects/RecurLens/data")

    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    
    patient_file = raw_dir / "tcga_clinical_patient.txt"
    sample_file = raw_dir / "tcga_clinical_sample.txt"
    rnaseq_file = raw_dir / "tcga_data_mrna_seq_v2_rsem_zscores.txt"

    download_file_with_progress(CLINICAL_PATIENT_URL, patient_file)
    download_file_with_progress(CLINICAL_SAMPLE_URL, sample_file)

    cohort_out = processed_dir / "tcga_er_pos_her2_neg_cohort.parquet"
    cohort_df = process_tcga_cohort(patient_file, sample_file, cohort_out)

    download_file_with_progress(MRNA_RNASEQ_URL, rnaseq_file)
    target_patients = set(cohort_df["PATIENT_ID"].tolist())
    matrix_out = processed_dir / "tcga_benchmark_genes_zscores.parquet"
    extract_tcga_gene_matrix(rnaseq_file, target_patients, matrix_out)
    logger.info("TCGA PanCanAtlas external dataset successfully prepared.")

if __name__ == "__main__":
    main()
