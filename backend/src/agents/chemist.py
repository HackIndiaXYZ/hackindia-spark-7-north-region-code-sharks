import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class Chemist:
    """Agent 2: Interfaces with BioNeMo to simulate drug binding."""
    
    # Drug to SMILES mapping
    DRUG_SMILES = {
        "Codeine": "CN1CC[C@]23[C@@H]4Oc5c(OC)ccc6c5[C@@]2(CCN(C)[C@H]3C6)[C@H]1[C@@H]4O",
        "Warfarin": "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
        "Clopidogrel": "COC(=O)[C@H](c1ccccc1Cl)N2CCc3c(ccs3)C2",
        "Tamoxifen": "CC[C@](c1ccccc1)(c2ccc(OCCN(C)C)cc2)c3ccccc3"
    }

    # Enzyme to Drug mapping (which enzyme metabolizes which drug)
    DRUG_ENZYME_MAP = {
        "Codeine": "CYP2D6",
        "Warfarin": "CYP2C19", # Simplified
        "Clopidogrel": "CYP2C19",
        "Tamoxifen": "CYP2D6"
    }

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("BIONEMO_API_KEY")

    def simulate_binding(self, drug_name, enzyme_profile):
        """Simulates binding using BioNeMo logic (mocked)."""
        smiles = self.DRUG_SMILES.get(drug_name)
        if not smiles:
            return {"error": f"Drug {drug_name} not found in database."}

        target_enzyme = self.DRUG_ENZYME_MAP.get(drug_name)
        patient_phenotype = enzyme_profile.get(target_enzyme, "Unknown")

        # Mock BioNeMo API call
        if self.api_key:
            # Here you would make a real request to NVIDIA BioNeMo
            # e.g., requests.post("https://api.bionemo.nvidia.com/v1/...", ...)
            pass
        
        # Simulation logic (Mocked)
        risk_score = self._calculate_risk(drug_name, target_enzyme, patient_phenotype)
        
        return {
            "drug": drug_name,
            "smiles": smiles,
            "target_enzyme": target_enzyme,
            "patient_phenotype": patient_phenotype,
            "metabolic_risk_score": risk_score,
            "confidence": 0.95
        }

    def _calculate_risk(self, drug, enzyme, phenotype):
        """
        Logic for metabolic risk scoring:
        - Poor Metabolizer + Prodrug (Codeine) -> High Risk (No efficacy)
        - Ultra-Rapid Metabolizer + Prodrug (Codeine) -> High Risk (Toxicity)
        - Poor Metabolizer + Active Drug (Warfarin) -> High Risk (Toxicity)
        """
        # Codeine is a prodrug; needs CYP2D6 to become Morphine.
        if drug == "Codeine" and enzyme == "CYP2D6":
            if phenotype == "Poor Metabolizer":
                return 0.9 # High Risk: No efficacy
            if phenotype == "Ultra-Rapid":
                return 0.95 # High Risk: Toxicity (too much morphine)
            if phenotype == "Intermediate Metabolizer":
                return 0.5
            return 0.1 # Normal

        # Clopidogrel is a prodrug; needs CYP2C19.
        if drug == "Clopidogrel" and enzyme == "CYP2C19":
            if phenotype == "Poor Metabolizer":
                return 0.85
            return 0.2

        # Default fallback
        if "Poor" in phenotype or "Ultra-Rapid" in phenotype:
            return 0.7
        
        return 0.2

if __name__ == "__main__":
    chemist = Chemist()
    mock_profile = {"CYP2D6": "Poor Metabolizer"}
    result = chemist.simulate_binding("Codeine", mock_profile)
    print(json.dumps(result, indent=4))
