import pytest
from app.services.parser_service import parser_service

def test_parse_observations_cbc():
    sample_text = """
    APOLLO DIAGNOSTICS
    Complete Blood Count (CBC)
    Hemoglobin 11.2 g/dL 13.0 - 17.0
    Total Leukocyte Count 7500 cells/mcL 4000 - 11000
    Platelet Count 2.5 lakhs/mcL 1.5 - 4.5
    """
    obs = parser_service.parse_observations(sample_text)
    assert len(obs) >= 3

    # Check Hemoglobin
    hb = next((o for o in obs if "Hemoglobin" in o["display_name"]), None)
    assert hb is not None
    assert hb["value_quantity"] == 11.2
    assert hb["interpretation"] == "Low"
    assert hb["unit"] == "g/dL"

    # Check WBC
    wbc = next((o for o in obs if "Leukocyte" in o["display_name"] or "WBC" in o["display_name"]), None)
    assert wbc is not None
    assert wbc["value_quantity"] == 7500.0
    assert wbc["interpretation"] == "Normal"

def test_parse_observations_diabetic_and_lipid():
    sample_text = """
    DR. LAL PATHLABS
    Fasting Blood Sugar 142 mg/dL 70 - 99
    HbA1c 7.6 % 4.0 - 5.6
    Total Cholesterol 230 mg/dL 125 - 200
    LDL Cholesterol 152 mg/dL 50 - 100
    """
    obs = parser_service.parse_observations(sample_text)
    assert len(obs) >= 4

    hba1c = next((o for o in obs if "HbA1c" in o["display_name"]), None)
    assert hba1c is not None
    assert hba1c["value_quantity"] == 7.6
    assert hba1c["interpretation"] == "High"

    chol = next((o for o in obs if "Total Cholesterol" in o["display_name"]), None)
    assert chol is not None
    assert chol["interpretation"] == "High"

def test_parse_medications_and_conditions():
    sample_text = """
    Clinical Diagnosis: Type 2 Diabetes Mellitus, Essential Hypertension
    Rx:
    Tab. Metformin 500 mg twice daily after meals
    Tab. Atorvastatin 10 mg at bedtime
    """
    meds, conditions = parser_service.parse_medications_and_conditions(sample_text)
    assert len(meds) >= 2
    assert len(conditions) >= 2

    cond_names = [c["display_name"] for c in conditions]
    assert any("Diabetes" in name for name in cond_names)
    assert any("Hypertension" in name for name in cond_names)

    med_names = [m["medication_name"] for m in meds]
    assert any("Metformin" in name for name in med_names)
    assert any("Atorvastatin" in name for name in med_names)


def test_wbc_unit_handling_and_normalization():
    """Regression test for WBC unit variations, equivalent values, and scale harmonization."""
    # 1. Scientific notation unit (x 10^3/µL)
    text1 = "Total Leukocyte Count (WBC) 7.2 × 10^3/µL 4.0 - 11.0"
    obs1 = parser_service.parse_observations(text1)
    wbc1 = next(o for o in obs1 if "WBC" in o["display_name"])
    assert wbc1["value_quantity"] == 7.2
    assert "10^3" in wbc1["unit"]
    assert wbc1["reference_range_low"] == 4.0
    assert wbc1["reference_range_high"] == 11.0
    assert wbc1["interpretation"] == "Normal"

    # 2. Standard cells/mcL unit
    text2 = "Total Leukocyte Count 7200 cells/mcL 4000 - 11000"
    obs2 = parser_service.parse_observations(text2)
    wbc2 = next(o for o in obs2 if "WBC" in o["display_name"])
    assert wbc2["value_quantity"] == 7200.0
    assert wbc2["unit"] == "cells/mcL"
    assert wbc2["reference_range_low"] == 4000.0
    assert wbc2["reference_range_high"] == 11000.0
    assert wbc2["interpretation"] == "Normal"

    # 3. Scale mismatch: value in 10^3/µL but range printed in cells/mcL (4000 - 11000)
    text3 = "WBC Count 7.2 10^3/µL 4000 - 11000"
    obs3 = parser_service.parse_observations(text3)
    wbc3 = next(o for o in obs3 if "WBC" in o["display_name"])
    assert wbc3["value_quantity"] == 7.2
    assert wbc3["reference_range_low"] == 4.0
    assert wbc3["reference_range_high"] == 11.0
    assert wbc3["interpretation"] == "Normal"

    # 4. Out of range values
    low_text = "Total Leukocyte Count 2.8 × 10^3/µL 4.0 - 11.0"
    wbc_low = next(o for o in parser_service.parse_observations(low_text) if "WBC" in o["display_name"])
    assert wbc_low["interpretation"] == "Low"

    high_text = "Total Leukocyte Count 16.5 × 10^3/µL 4.0 - 11.0"
    wbc_high = next(o for o in parser_service.parse_observations(high_text) if "WBC" in o["display_name"])
    assert wbc_high["interpretation"] == "High"


def test_platelet_unit_handling_and_normalization():
    """Regression test for Platelet unit variations, equivalent values, and scale harmonization."""
    # 1. Scientific notation unit (250 × 10^3/µL)
    text1 = "Platelet Count 250 × 10^3/µL 150 - 450"
    obs1 = parser_service.parse_observations(text1)
    plt1 = next(o for o in obs1 if "Platelet" in o["display_name"])
    assert plt1["value_quantity"] == 250.0
    assert "10^3" in plt1["unit"]
    assert plt1["reference_range_low"] == 150.0
    assert plt1["reference_range_high"] == 450.0
    assert plt1["interpretation"] == "Normal"

    # 2. Indian lab lakhs unit (2.5 lakhs/mcL)
    text2 = "Platelet Count 2.5 lakhs/mcL 1.5 - 4.5"
    obs2 = parser_service.parse_observations(text2)
    plt2 = next(o for o in obs2 if "Platelet" in o["display_name"])
    assert plt2["value_quantity"] == 2.5
    assert "lakh" in plt2["unit"]
    assert plt2["reference_range_low"] == 1.5
    assert plt2["reference_range_high"] == 4.5
    assert plt2["interpretation"] == "Normal"

    # 3. Absolute count unit (/mcL)
    text3 = "Platelet Count 250000 /mcL 150000 - 450000"
    obs3 = parser_service.parse_observations(text3)
    plt3 = next(o for o in obs3 if "Platelet" in o["display_name"])
    assert plt3["value_quantity"] == 250000.0
    assert plt3["interpretation"] == "Normal"

    # 4. Scale mismatch: value in thousands (250) but range printed in lakhs (1.5 - 4.5)
    text4 = "Platelet Count 250 × 10^3/µL 1.5 - 4.5"
    obs4 = parser_service.parse_observations(text4)
    plt4 = next(o for o in obs4 if "Platelet" in o["display_name"])
    assert plt4["value_quantity"] == 250.0
    assert plt4["reference_range_low"] == 150.0
    assert plt4["reference_range_high"] == 450.0
    assert plt4["interpretation"] == "Normal"

    # 5. Critical platelet threshold (< 50 x 10^3/µL or < 0.5 lakhs)
    crit_text = "Platelet Count 32 × 10^3/µL 150 - 450"
    plt_crit = next(o for o in parser_service.parse_observations(crit_text) if "Platelet" in o["display_name"])
    assert plt_crit["interpretation"] == "Critical"


def test_synthetic_cbc_all_expected_parameters():
    """Verify all 6 synthetic CBC sample values match user specifications and evaluate to Normal."""
    sample_text = """
    APOLLO DIAGNOSTICS & HEALTHCARE
    Patient: Arun Kumar (45Y / Male) | Date: 10-Oct-2026
    Hemoglobin (Hb) 13.8 g/dL 13.0 - 17.0
    RBC Count 4.7 × 10^6/µL 4.5 - 5.9
    Total Leukocyte Count (WBC) 7.2 × 10^3/µL 4.0 - 11.0
    Platelet Count 250 × 10^3/µL 150 - 450
    Packed Cell Volume (PCV) 41 % 40.0 - 50.0
    Mean Corpuscular Volume (MCV) 87 fL 80.0 - 100.0
    """
    obs = parser_service.parse_observations(sample_text)
    assert len(obs) == 6

    obs_map = {o["display_name"]: o for o in obs}

    # Hemoglobin 13.8 g/dL
    hb = next(o for name, o in obs_map.items() if "Hemoglobin" in name)
    assert hb["value_quantity"] == 13.8
    assert hb["unit"] == "g/dL"
    assert hb["interpretation"] == "Normal"

    # RBC 4.7 × 10^6/µL
    rbc = next(o for name, o in obs_map.items() if "RBC" in name)
    assert rbc["value_quantity"] == 4.7
    assert "10^6" in rbc["unit"]
    assert rbc["interpretation"] == "Normal"

    # WBC 7.2 × 10^3/µL
    wbc = next(o for name, o in obs_map.items() if "WBC" in name)
    assert wbc["value_quantity"] == 7.2
    assert "10^3" in wbc["unit"]
    assert wbc["interpretation"] == "Normal"

    # Platelets 250 × 10^3/µL
    plt = next(o for name, o in obs_map.items() if "Platelet" in name)
    assert plt["value_quantity"] == 250.0
    assert "10^3" in plt["unit"]
    assert plt["interpretation"] == "Normal"

    # PCV 41 %
    pcv = next(o for name, o in obs_map.items() if "PCV" in name)
    assert pcv["value_quantity"] == 41.0
    assert pcv["unit"] == "%"
    assert pcv["interpretation"] == "Normal"

    # MCV 87 fL
    mcv = next(o for name, o in obs_map.items() if "MCV" in name)
    assert mcv["value_quantity"] == 87.0
    assert mcv["unit"] == "fL"
    assert mcv["interpretation"] == "Normal"

