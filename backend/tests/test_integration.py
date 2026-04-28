import pytest
import os
from src.orchestrator import GeneticGuardrail

def test_e2e_codeine_high_risk():
    # Using the mock VCF where CYP2D6 is Poor Metabolizer
    vcf_path = os.path.join("data", "mock_variants.vcf")
    guardrail = GeneticGuardrail()
    
    result = guardrail.run_guardrail(vcf_path, "Codeine")
    
    assert result["status"] == "success"
    assert result["patient_profile"]["CYP2D6"] == "Poor Metabolizer"
    assert result["simulation"]["metabolic_risk_score"] >= 0.8
    assert result["recommendation"]["action"] == "Avoid"
    assert "analgesia" in result["recommendation"]["clinical_note"].lower()

def test_e2e_unknown_drug():
    vcf_path = os.path.join("data", "mock_variants.vcf")
    guardrail = GeneticGuardrail()
    
    result = guardrail.run_guardrail(vcf_path, "UnknownDrug")
    
    assert result["status"] == "error"
    assert "not found" in result["message"].lower()

def test_e2e_insufficient_data():
    # Create an empty VCF
    vcf_content = """##fileformat=VCFv4.2
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
"""
    temp_vcf = "data/temp_empty_e2e.vcf"
    os.makedirs("data", exist_ok=True)
    with open(temp_vcf, "w") as f:
        f.write(vcf_content)
        
    guardrail = GeneticGuardrail()
    result = guardrail.run_guardrail(temp_vcf, "Codeine")
    
    assert result["status"] == "success"
    assert result["patient_profile"]["CYP2D6"] == "Insufficient Genomic Data"
    
    if os.path.exists(temp_vcf):
        os.remove(temp_vcf)
