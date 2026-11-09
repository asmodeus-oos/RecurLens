"""
METABRIC Ingestion & Cohort Harmonization Pipeline for RecurLens / GeneLens AI.
In accordance with TRIPOD+AI, REMARK, and STEEP guidelines.
"""

from __future__ import annotations
import os
import sys
import logging
from pathlib import Path
import urllib.request
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("RecurLens.Ingest")

# Primary DataHub raw URLs
BASE_URL = "https://media.githubusercontent.com/media/cBioPortal/datahub/master/public/brca_metabric"
CLINICAL_PATIENT_URL = f"{BASE_URL}/data_clinical_patient.txt"
CLINICAL_SAMPLE_URL = f"{BASE_URL}/data_clinical_sample.txt"
MRNA_ZSCORES_URL = f"{BASE_URL}/data_mrna_illumina_microarray_zscores_ref_diploid_samples.txt"
MRNA_RAW_URL = f"{BASE_URL}/data_mrna_illumina_microarray.txt"

# Canonical 50 PAM50 Genes
PAM50_GENES = [
    "ACTR3B", "ANLN", "BAG1", "BCL2", "BIRC5", "BLVRA", "CCNB1", "CCNE1", "CDC20", "CDC6",
    "CDH3", "CENPF", "CEP55", "CXXC5", "EGFR", "ERBB2", "ESR1", "EXO1", "FGFR4", "FOXA1",
    "FOXC1", "GPR160", "GRB7", "KIF2C", "KRT14", "KRT17", "KRT5", "MAPT", "MDM2", "MELK",
    "MIA", "MKI67", "MLPH", "MMP11", "MYBL2", "MYC", "NAT1", "NDC80", "NUF2", "ORC6",
    "PGR", "PTTG1", "RRM2", "SFRP1", "SLC39A6", "TMEM45B", "TYMS", "UBE2C", "UBE2T", "UCHL5"
]

# 21-gene Oncotype DX list (16 cancer genes + 5 reference)
ONCOTYPE_GENES = [
    "MKI67", "AURKA", "BIRC5", "CCNB1", "MYBL2",
    "MMP11", "CTSL2",
    "GRB7", "ERBB2",
    "ESR1", "PGR", "BCL2", "SCUBE2",
    "GSTM1", "CD68", "BAG1",
    "ACTB", "GAPDH", "RPLP0", "GUSB", "TFRC"
]

def download_file_with_progress(url: str, dest_path: Path) -> Path:
    """Download a remote file with progress report if not already present."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists() and dest_path.stat().st_size > 0:
        logger.info("File already exists: %s (%d bytes)", dest_path.name, dest_path.stat().st_size)
        return dest_path

    logger.info("Downloading %s -> %s", url, dest_path)
    tmp_path = dest_path.with_suffix(".tmp")
    
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100.0, downloaded * 100.0 / total_size)
            if block_num % 1000 == 0:
                logger.info("Progress %s: %.1f%% (%d / %d bytes)", dest_path.name, percent, downloaded, total_size)

    urllib.request.urlretrieve(url, tmp_path, reporthook=report_progress)
    tmp_path.rename(dest_path)
    logger.info("Download completed: %s (%d bytes)", dest_path.name, dest_path.stat().st_size)
    return dest_path


def load_cbioportal_tsv(file_path: Path) -> pd.DataFrame:
    """Load cBioPortal TSV skipping leading comment rows (#)."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        skip_rows = 0
        for line in f:
            if line.startswith("#"):
                skip_rows += 1
            else:
                break
    return pd.read_csv(file_path, sep="\t", skiprows=skip_rows, low_memory=False)


def compute_cts5(row: pd.Series) -> float:
    """
    Compute Clinical Treatment Score post-5 years (CTS5) continuous index.
    Reference: Cuzick et al., J Clin Oncol 2018 (36:2941-2946).
    Formula:
        CTS5 = 0.438 * NodeGroup + 0.988 * (0.2 * TumorSize) - 0.012 * (0.2 * TumorSize)^2 + 0.127 * Grade + 0.015 * Age
    where:
        NodeGroup: 0 for 0 nodes, 1 for 1-3 nodes, 2 for 4-9 nodes, 3 for >=10 nodes.
        TumorSize: continuous diameter in mm.
        Grade: 1, 2, or 3.
        Age: continuous age in years.
    """
    try:
        nodes = float(row.get("LYMPH_NODES_EXAMINED_POSITIVE", 0))
        if nodes == 0:
            node_group = 0
        elif 1 <= nodes <= 3:
            node_group = 1
        elif 4 <= nodes <= 9:
            node_group = 2
        else:
            node_group = 3

        size_mm = float(row.get("TUMOR_SIZE", np.nan))
        if np.isnan(size_mm) or size_mm <= 0:
            return np.nan

        grade = float(row.get("GRADE", np.nan))
        if np.isnan(grade) or grade not in (1.0, 2.0, 3.0):
            return np.nan

        age = float(row.get("AGE_AT_DIAGNOSIS", np.nan))
        if np.isnan(age) or age <= 0:
            return np.nan

        scaled_size = 0.2 * size_mm
        cts5 = (
            0.438 * node_group
            + 0.988 * scaled_size
            - 0.012 * (scaled_size ** 2)
            + 0.127 * grade
            + 0.015 * age
        )
        return float(cts5)
    except Exception:
        return np.nan


def parse_rfs_status(val) -> float:
    if pd.isna(val):
        return np.nan
    s = str(val).lower().strip()
    if "not recurred" in s or s.startswith("0"):
        return 0.0
    if "recurred" in s or s.startswith("1"):
        return 1.0
    return np.nan

def process_clinical_cohort(patient_file: Path, sample_file: Path, out_path: Path) -> pd.DataFrame:
    """
    Merge patient + sample records and apply eligibility criteria per Study Protocol:
    1. Female
    2. ER+/HER2-
    3. Stage I-II (pT1-pT2, <= 50mm, pN0-pN1, <= 3 positive nodes)
    4. Valid follow-up and RFS status
    """
    logger.info("Parsing clinical patient and sample files...")
    df_patient = load_cbioportal_tsv(patient_file)
    df_sample = load_cbioportal_tsv(sample_file)

    # Standardize IDs
    df_patient["PATIENT_ID"] = df_patient["PATIENT_ID"].astype(str).str.strip()
    df_sample["PATIENT_ID"] = df_sample["PATIENT_ID"].astype(str).str.strip()
    df_sample["SAMPLE_ID"] = df_sample["SAMPLE_ID"].astype(str).str.strip()

    # Retain primary tumor samples if multiple
    if "SAMPLE_TYPE" in df_sample.columns:
        df_sample = df_sample[df_sample["SAMPLE_TYPE"].str.lower().isin(["primary", "primary tumor", "tumor", "nan"]) | df_sample["SAMPLE_TYPE"].isna()]
    df_sample = df_sample.drop_duplicates(subset=["PATIENT_ID"], keep="first")

    merged = pd.merge(df_patient, df_sample, on="PATIENT_ID", how="inner", suffixes=("", "_SAMPLE"))
    logger.info("Total cohort before filtering: %d patients", len(merged))

    # Clean numeric types
    for col in ["AGE_AT_DIAGNOSIS", "RFS_MONTHS", "OS_MONTHS", "LYMPH_NODES_EXAMINED_POSITIVE", "TUMOR_SIZE", "GRADE"]:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

    # Clean RFS Status: '1:Recurred' -> 1, '0:Not Recurred' -> 0
    if "RFS_STATUS" in merged.columns:
        merged["RFS_EVENT"] = merged["RFS_STATUS"].apply(parse_rfs_status)
    else:
        merged["RFS_EVENT"] = np.nan

    # 1. Eligibility: Female
    if "SEX" in merged.columns:
        merged = merged[merged["SEX"].astype(str).str.lower().str.startswith("f")]

    # 2. Eligibility: ER+ / HER2-
    # In METABRIC, ER_IHC is 'Positive' or 'Positve', ER_STATUS in sample is 'Positive'
    er_pos = (
        merged["ER_STATUS"].astype(str).str.lower().str.startswith("pos")
        | merged["ER_IHC"].astype(str).str.lower().str.startswith("pos")
    )
    her2_neg = (
        merged["HER2_STATUS"].astype(str).str.lower().str.startswith("neg")
        | merged["HER2_SNP6"].astype(str).str.upper().isin(["NEUTRAL", "LOSS"])
    )
    merged = merged[er_pos & her2_neg]
    logger.info("After ER+/HER2- filter: %d patients", len(merged))

    # 3. Eligibility: Stage I-II (Tumor size <= 50 mm, Lymph nodes <= 3)
    size_ok = merged["TUMOR_SIZE"].isna() | (merged["TUMOR_SIZE"] <= 50.0)
    nodes_ok = merged["LYMPH_NODES_EXAMINED_POSITIVE"].isna() | (merged["LYMPH_NODES_EXAMINED_POSITIVE"] <= 3.0)
    merged = merged[size_ok & nodes_ok]
    logger.info("After Stage I-II (size <= 50mm, nodes <= 3) filter: %d patients", len(merged))

    # 4. Eligibility: Valid RFS time (> 0) and valid event indicator
    merged = merged[merged["RFS_MONTHS"].notna() & (merged["RFS_MONTHS"] > 0) & merged["RFS_EVENT"].notna()]
    merged["RFS_EVENT"] = merged["RFS_EVENT"].astype(int)
    logger.info("After valid RFS follow-up filter: %d patients", len(merged))

    # Compute CTS5 Score
    merged["CTS5_SCORE"] = merged.apply(compute_cts5, axis=1)
    
    # Categorize CTS5 risk category: Low (< 3.13), Intermediate (3.13 - 3.86), High (> 3.86)
    merged["CTS5_RISK_GROUP"] = merged["CTS5_SCORE"].apply(
        lambda x: "Low" if x < 3.13 else ("Intermediate" if x <= 3.86 else ("High" if not np.isnan(x) else "Unknown"))
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(out_path, index=False)
    merged.to_csv(out_path.with_suffix(".csv"), index=False)
    logger.info("Saved filtered cohort to %s and %s", out_path, out_path.with_suffix(".csv"))
    return merged


def extract_benchmark_genes_matrix(expression_file: Path, target_samples: set[str], out_path: Path) -> pd.DataFrame:
    """Extract expression for canonical PAM50 and Oncotype 21 genes across target cohort."""
    logger.info("Extracting benchmark gene expression matrix...")
    all_target_genes = set(PAM50_GENES + ONCOTYPE_GENES)
    
    extracted_rows = []
    with open(expression_file, "r", encoding="utf-8", errors="replace") as f:
        header_line = f.readline().strip().split("\t")
        col_names = [col.strip() for col in header_line]
        sample_indices = [i for i, col in enumerate(col_names) if col in target_samples]
        sample_names = [col_names[i] for i in sample_indices]
        
        for line in f:
            parts = line.strip().split("\t")
            gene = parts[0].strip()
            if gene in all_target_genes:
                vals = [float(parts[i]) if parts[i] not in ("NA", "null", "") else np.nan for i in sample_indices]
                extracted_rows.append([gene] + vals)
    
    df_raw = pd.DataFrame(extracted_rows, columns=["Hugo_Symbol"] + sample_names)
    # Average duplicate probes per gene (standard bioinformatic collapse for microarray)
    df_grouped = df_raw.groupby("Hugo_Symbol").mean()
    df_expr = df_grouped.T
    df_expr.index.name = "PATIENT_ID"
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_expr.to_parquet(out_path)
    df_expr.to_csv(out_path.with_suffix(".csv"))
    logger.info("Saved benchmark gene matrix (%d patients x %d genes) to %s", len(df_expr), df_expr.shape[1], out_path)
    return df_expr


def main(data_dir: Path | None = None):
    if data_dir is None:
        data_dir = Path("/home/vlad/Projects/RecurLens/data")

    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    patient_file = raw_dir / "data_clinical_patient.txt"
    sample_file = raw_dir / "data_clinical_sample.txt"
    zscores_file = raw_dir / "data_mrna_illumina_microarray_zscores_ref_diploid_samples.txt"

    # Step 1: Download clinical files
    download_file_with_progress(CLINICAL_PATIENT_URL, patient_file)
    download_file_with_progress(CLINICAL_SAMPLE_URL, sample_file)

    # Step 2: Harmonize and filter clinical cohort
    cohort_out = processed_dir / "metabric_er_pos_her2_neg_cohort.parquet"
    cohort_df = process_clinical_cohort(patient_file, sample_file, cohort_out)

    logger.info("Cohort summary:")
    logger.info("Total qualified patients: %d", len(cohort_df))
    logger.info("Recurrence events: %d (%.1f%%)", cohort_df["RFS_EVENT"].sum(), cohort_df["RFS_EVENT"].mean() * 100)
    logger.info("CTS5 calculated: %d patients", cohort_df["CTS5_SCORE"].notna().sum())
    logger.info("CTS5 Risk Group breakdown:\n%s", cohort_df["CTS5_RISK_GROUP"].value_counts().to_string())

    # Step 3: Download & extract benchmark gene matrix (PAM50 + Oncotype)
    download_file_with_progress(MRNA_ZSCORES_URL, zscores_file)
    target_samples = set(cohort_df["PATIENT_ID"].tolist())
    benchmark_out = processed_dir / "metabric_benchmark_genes_zscores.parquet"
    extract_benchmark_genes_matrix(zscores_file, target_samples, benchmark_out)

    logger.info("Ingestion completed successfully.")

if __name__ == "__main__":
    main()
