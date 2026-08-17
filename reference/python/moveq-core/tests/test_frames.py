import numpy as np
import pandas as pd
import pytest

from moveq_core.frames import compute_vulnerability_index, identify_multiply_deprived


def test_vulnerability_index_basic():
    df = pd.DataFrame({
        "deprivation": [10.0, 20.0, 30.0],
        "no_car_pct": [0.0, 50.0, 100.0],
        "unemployment": [5.0, 10.0, 15.0],
    })
    # For each column:
    # row 0: (10-10)/(30-10)=0%, (0-0)/(100-0)=0%, (5-5)/(15-5)=0% -> mean 0.0
    # row 1: (20-10)/20=50%, (50-0)/100=50%, (10-5)/10=50% -> mean 50.0
    # row 2: (30-10)/20=100%, (100-0)/100=100%, (15-5)/10=100% -> mean 100.0
    vuln = compute_vulnerability_index(df, ["deprivation", "no_car_pct", "unemployment"])

    assert len(vuln) == 3
    assert vuln.iloc[0] == 0.0
    assert vuln.iloc[1] == 50.0
    assert vuln.iloc[2] == 100.0


def test_vulnerability_index_constant_column():
    df = pd.DataFrame({
        "constant_factor": [5.0, 5.0, 5.0],
        "variable_factor": [0.0, 50.0, 100.0],
    })
    # constant_factor is normalized to 0.0 because mx == mn
    # row 0: (0 + 0) / 2 = 0.0
    # row 1: (0 + 50) / 2 = 25.0
    # row 2: (0 + 100) / 2 = 50.0
    vuln = compute_vulnerability_index(df, ["constant_factor", "variable_factor"])
    assert vuln.iloc[0] == 0.0
    assert vuln.iloc[1] == 25.0
    assert vuln.iloc[2] == 50.0


def test_vulnerability_index_single_factor():
    df = pd.DataFrame({"factor": [10.0, 30.0]})
    vuln = compute_vulnerability_index(df, ["factor"])
    assert vuln.iloc[0] == 0.0
    assert vuln.iloc[1] == 100.0


def test_identify_multiply_deprived():
    # 4 rows, 3 factors
    df = pd.DataFrame({
        "f1": [1.0, 2.0, 3.0, 4.0],
        "f2": [10.0, 20.0, 30.0, 40.0],
        "f3": [100.0, 200.0, 300.0, 400.0],
        "f4": [1000.0, 2000.0, 3000.0, 4000.0],
    })
    # Quantile(2/3):
    # Rows 2 and 3 should be >= 2/3 quantile across all factors
    flagged_3 = identify_multiply_deprived(df, ["f1", "f2", "f3", "f4"], min_factors=3)
    assert not flagged_3.iloc[0]
    assert not flagged_3.iloc[1]
    assert flagged_3.iloc[2]
    assert flagged_3.iloc[3]


def test_identify_multiply_deprived_custom_min_factors():
    df = pd.DataFrame({
        "f1": [1.0, 2.0, 3.0],
        "f2": [1.0, 1.0, 3.0],
        "f3": [1.0, 1.0, 1.0],
    })
    flagged_1 = identify_multiply_deprived(df, ["f1", "f2", "f3"], min_factors=1)
    assert isinstance(flagged_1, pd.Series)
    assert flagged_1.dtype == bool
    assert flagged_1.iloc[2]
