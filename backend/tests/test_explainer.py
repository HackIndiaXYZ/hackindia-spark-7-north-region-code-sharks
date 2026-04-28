import pytest
from src.agents.explainer import Explainer

def test_explainer_codeine_poor_metabolizer_mock():
    explainer = Explainer() # Mock mode
    profile = {"CYP2D6": "Poor Metabolizer"}
    risk = {
        "metabolic_risk_score": 0.9,
        "target_enzyme": "CYP2D6",
        "patient_phenotype": "Poor Metabolizer"
    }
    
    result = explainer.generate_recommendation("Codeine", profile, risk)
    
    assert result["action"] == "Avoid"
    assert "analgesia" in result["clinical_note"].lower()

def test_explainer_normal_metabolizer_mock():
    explainer = Explainer()
    profile = {"CYP2D6": "Normal Metabolizer"}
    risk = {
        "metabolic_risk_score": 0.1,
        "target_enzyme": "CYP2D6",
        "patient_phenotype": "Normal Metabolizer"
    }
    
    result = explainer.generate_recommendation("Codeine", profile, risk)
    
    assert result["action"] == "Prescribe"
    assert result["risk_level"] == "Low"
