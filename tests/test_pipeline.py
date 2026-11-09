"""
Automated Unit Test Suite for RecurLens / GeneLens AI Pipeline.
Verifies CTS5 calculations, surrogate genomic signatures, DCA, and pathway scores.
"""

import pytest
import numpy as np
import pandas as pd
from src.data.ingest_metabric import compute_cts5
from src.models.molecular_baseline import compute_oncotype_surrogate_score, compute_pam50_proliferation_index
from src.models.dca import calculate_dca_table
from src.models.pathway_scoring import compute_pathway_activity_scores

def test_cts5_calculation_standard_case():
    """Verify CTS5 matches exact Cuzick 2018 formula."""
    # Age 50, size 20mm (scaled 4), grade 2, nodes 0
    row = pd.Series({
        "AGE_AT_DIAGNOSIS": 50.0,
        "TUMOR_SIZE": 20.0,
        "GRADE": 2.0,
        "LYMPH_NODES_EXAMINED_POSITIVE": 0.0
    })
    score = compute_cts5(row)
    # 0 + 0.988*4 - 0.012*16 + 0.127*2 + 0.015*50 = 3.952 - 0.192 + 0.254 + 0.75 = 4.764
    assert pytest.approx(score, abs=1e-3) == 4.764

def test_cts5_calculation_node_positive():
    """Verify CTS5 node group scaling (1-3 nodes = group 1)."""
    row = pd.Series({
        "AGE_AT_DIAGNOSIS": 60.0,
        "TUMOR_SIZE": 15.0,
        "GRADE": 1.0,
        "LYMPH_NODES_EXAMINED_POSITIVE": 2.0
    })
    score = compute_cts5(row)
    # Node group 1 (0.438*1 = 0.438)
    # scaled size = 3.0 -> 0.988*3 - 0.012*9 = 2.964 - 0.108 = 2.856
    # grade 1 -> 0.127
    # age 60 -> 0.900
    # total = 0.438 + 2.856 + 0.127 + 0.900 = 4.321
    assert pytest.approx(score, abs=1e-3) == 4.321

def test_cts5_missing_values_return_nan():
    """Verify NaN safety in clinical calculator."""
    row = pd.Series({
        "AGE_AT_DIAGNOSIS": np.nan,
        "TUMOR_SIZE": 20.0,
        "GRADE": 2.0,
        "LYMPH_NODES_EXAMINED_POSITIVE": 0.0
    })
    assert np.isnan(compute_cts5(row))

def test_oncotype_surrogate_computation():
    """Verify Oncotype 21-gene surrogate calculates unscaled recurrence score."""
    data = {
        "MKI67": [1.0, -1.0],
        "AURKA": [1.0, -1.0],
        "BIRC5": [1.0, -1.0],
        "CCNB1": [1.0, -1.0],
        "MYBL2": [1.0, -1.0],
        "ESR1": [0.0, 1.0],
        "PGR": [0.0, 1.0],
        "BCL2": [0.0, 1.0],
        "SCUBE2": [0.0, 1.0],
        "MMP11": [0.5, -0.5],
        "CTSL2": [0.5, -0.5],
        "GRB7": [0.0, 0.0],
        "ERBB2": [0.0, 0.0]
    }
    df = pd.DataFrame(data, index=["Patient_High", "Patient_Low"])
    rs = compute_oncotype_surrogate_score(df)
    assert len(rs) == 2
    assert rs["Patient_High"] > rs["Patient_Low"]

def test_pam50_proliferation_index():
    """Verify PAM50 proliferation index calculation."""
    df = pd.DataFrame({
        "MKI67": [2.0, -2.0],
        "AURKA": [2.0, -2.0],
        "CENPF": [2.0, -2.0]
    }, index=["P1", "P2"])
    score = compute_pam50_proliferation_index(df)
    assert score["P1"] == 2.0
    assert score["P2"] == -2.0

def test_dca_net_benefit_calculation():
    """Verify DCA calculation on synthetic predictions."""
    y_true = np.array([1, 1, 0, 0, 0])
    pred_risks = {
        "Perfect": np.array([0.9, 0.9, 0.1, 0.1, 0.1]),
        "Random": np.array([0.5, 0.5, 0.5, 0.5, 0.5])
    }
    thresholds = np.array([0.20])
    dca_df = calculate_dca_table(y_true, pred_risks, thresholds=thresholds)
    
    assert "Treat_All" in dca_df.columns
    assert "Treat_None" in dca_df.columns
    assert "Perfect" in dca_df.columns
    assert dca_df["Treat_None"].iloc[0] == 0.0
    assert dca_df["Perfect"].iloc[0] > dca_df["Random"].iloc[0]

def test_pathway_activity_scoring():
    """Verify pathway z-score aggregation and standardization."""
    df = pd.DataFrame({
        "MKI67": [1.0, 0.0, -1.0],
        "AURKA": [1.0, 0.0, -1.0],
        "CENPF": [1.0, 0.0, -1.0]
    }, index=["P1", "P2", "P3"])
    pw = compute_pathway_activity_scores(df)
    assert "Hallmark_G2M_Checkpoint" in pw.columns
    assert pw["Hallmark_G2M_Checkpoint"].iloc[0] > pw["Hallmark_G2M_Checkpoint"].iloc[2]
