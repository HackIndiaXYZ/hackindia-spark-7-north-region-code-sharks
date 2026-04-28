import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class Explainer:
    """Agent 3: Translates technical data into clinical advice using Gemini."""
    
    def __init__(self, api_key=None, model_name="gemini-1.5-pro"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # Check if api_key is valid and not a placeholder
        if self.api_key and ("your_gemini_api_key" in self.api_key or "your_openai_api_key" in self.api_key):
            self.api_key = None
            
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None

    def generate_recommendation(self, drug_name, enzyme_profile, metabolic_risk):
        """Generates a clinical recommendation based on the risk score and profile."""
        
        prompt = self._build_prompt(drug_name, enzyme_profile, metabolic_risk)
        
        if not self.model:
            return self._mock_llm_response(drug_name, enzyme_profile, metabolic_risk)
        
        try:
            # Use generation_config for JSON output if supported or just parse the text
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini call failed: {str(e)}")
            return self._mock_llm_response(drug_name, enzyme_profile, metabolic_risk)

    def _build_prompt(self, drug, profile, risk):
        return f"""
        You are a Clinical Pharmacogenomics Expert. Analyze the following pharmacogenomic data and provide a clinical recommendation.
        
        Drug: {drug}
        Enzyme Profile: {json.dumps(profile)}
        Metabolic Risk Score: {risk['metabolic_risk_score']}
        Target Enzyme: {risk['target_enzyme']}
        Patient Phenotype: {risk['patient_phenotype']}
        
        Return a JSON object with exactly these keys:
        - action: (Prescribe / Adjust Dose / Avoid)
        - risk_level: (Low / Moderate / High)
        - clinical_note: (A plain-English explanation for the clinician)
        - alternative_drug: (An alternative drug if the action is Avoid, otherwise null)
        """

    def _mock_llm_response(self, drug, profile, risk):
        """Fallback mock response for testing without API keys."""
        score = risk['metabolic_risk_score']
        phenotype = risk['patient_phenotype']
        
        if drug == "Codeine":
            if phenotype == "Poor Metabolizer":
                return {
                    "action": "Avoid",
                    "risk_level": "High",
                    "clinical_note": "Patient is a CYP2D6 Poor Metabolizer. Codeine will not be converted to its active form (Morphine), resulting in inadequate analgesia.",
                    "alternative_drug": "Morphine or Non-opioids"
                }
            if phenotype == "Ultra-Rapid":
                return {
                    "action": "Avoid",
                    "risk_level": "High",
                    "clinical_note": "Patient is a CYP2D6 Ultra-Rapid Metabolizer. Risk of rapid conversion to Morphine and potential toxicity.",
                    "alternative_drug": "Morphine (at reduced dose) or Non-opioids"
                }
        
        if score > 0.7:
            return {
                "action": "Avoid",
                "risk_level": "High",
                "clinical_note": f"High metabolic risk detected for {drug} due to {phenotype} status of {risk['target_enzyme']}.",
                "alternative_drug": "Consult clinical pharmacist for alternatives"
            }
        elif score > 0.4:
            return {
                "action": "Adjust Dose",
                "risk_level": "Moderate",
                "clinical_note": f"Moderate metabolic risk. Consider dose adjustment for {drug}.",
                "alternative_drug": None
            }
        else:
            return {
                "action": "Prescribe",
                "risk_level": "Low",
                "clinical_note": f"Standard dosing is likely appropriate for {drug} based on genomic profile.",
                "alternative_drug": None
            }

if __name__ == "__main__":
    explainer = Explainer() # Will use mock since no key
    mock_risk = {
        "metabolic_risk_score": 0.9,
        "target_enzyme": "CYP2D6",
        "patient_phenotype": "Poor Metabolizer"
    }
    result = explainer.generate_recommendation("Codeine", {"CYP2D6": "Poor Metabolizer"}, mock_risk)
    print(json.dumps(result, indent=4))
