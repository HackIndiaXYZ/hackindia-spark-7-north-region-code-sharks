import asyncio
import json
from agents.agent2 import calculate_risk
from agents.agent3 import generate_clinical_recommendation

async def run_tests():
    patient_profile = {
        "CYP3A4": "Normal",
        "CYP2C9": "Poor Metabolizer",
        "CYP2D6": "Intermediate Metabolizer"
    }

    # Test 1: Dolo
    print("\n--- Test 1: Dolo ---")
    risk_dolo = await calculate_risk(patient_profile, "Dolo")
    print(f"Agent2 Result (Dolo): {json.dumps(risk_dolo, indent=2)}")
    
    if not risk_dolo.get("invalid_drug", False):
        rec_dolo = await generate_clinical_recommendation(
            findings={"CYP3A4": "Normal"},
            risk_level=risk_dolo["risk_level"],
            drug_name="Acetaminophen",
            confidence=risk_dolo["confidence"],
            clinical_note_override=risk_dolo.get("clinical_note_override")
        )
        print(f"Agent3 Result (Dolo): {json.dumps(rec_dolo, indent=2)}")
    
    # Test 2: UnknownDrug123
    print("\n--- Test 2: UnknownDrug123 ---")
    risk_unknown = await calculate_risk(patient_profile, "UnknownDrug123")
    print(f"Agent2 Result (UnknownDrug123): {json.dumps(risk_unknown, indent=2)}")
    
    # Test 3: Valid unknown drug (NewPharmaDrug)
    print("\n--- Test 3: NewPharmaDrug (assuming valid AI fallback) ---")
    # Forcing a mock since Gemini might not know NewPharmaDrug
    # But we'll test a real drug not in matrix, e.g. "Citalopram" (metabolized by CYP2C19/CYP3A4/CYP2D6)
    risk_real_unknown = await calculate_risk(patient_profile, "Citalopram")
    print(f"Agent2 Result (Citalopram): {json.dumps(risk_real_unknown, indent=2)}")
    
    if not risk_real_unknown.get("invalid_drug", False):
        rec_real_unknown = await generate_clinical_recommendation(
            findings={"CYP2C19": "Normal"}, # Example
            risk_level=risk_real_unknown["risk_level"],
            drug_name="Citalopram",
            confidence=risk_real_unknown["confidence"],
            clinical_note_override=risk_real_unknown.get("clinical_note_override")
        )
        print(f"Agent3 Result (Citalopram): {json.dumps(rec_real_unknown, indent=2)}")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(run_tests())
