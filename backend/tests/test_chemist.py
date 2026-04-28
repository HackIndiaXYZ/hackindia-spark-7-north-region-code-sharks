import pytest
from src.agents.chemist import Chemist

def test_chemist_codeine_poor_metabolizer():
    chemist = Chemist()
    profile = {"CYP2D6": "Poor Metabolizer"}
    result = chemist.simulate_binding("Codeine", profile)
    
    assert result["drug"] == "Codeine"
    assert result["metabolic_risk_score"] >= 0.8
    assert result["patient_phenotype"] == "Poor Metabolizer"

def test_chemist_codeine_ultra_rapid():
    chemist = Chemist()
    profile = {"CYP2D6": "Ultra-Rapid"}
    result = chemist.simulate_binding("Codeine", profile)
    
    assert result["metabolic_risk_score"] >= 0.9
    assert result["patient_phenotype"] == "Ultra-Rapid"

def test_chemist_unknown_drug():
    chemist = Chemist()
    result = chemist.simulate_binding("UnknownDrug", {})
    assert "error" in result

def test_chemist_normal_metabolizer():
    chemist = Chemist()
    profile = {"CYP2D6": "Normal Metabolizer"}
    result = chemist.simulate_binding("Codeine", profile)
    assert result["metabolic_risk_score"] <= 0.2
