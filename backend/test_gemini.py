from google import genai
import os
from dotenv import load_dotenv
import json
import re

load_dotenv(".env")

PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.5-pro"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def clean_json_response(text):
    text = re.sub(r"```json\n?", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()

def call_model(model_name, prompt):
    return client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )

def generate_clinical_recommendation(enzyme_profile, risk_score, drug_name):
    
    # 🔒 Handle missing genomic data
    if not enzyme_profile or len(enzyme_profile) == 0:
        return {
            "action": "Insufficient Data",
            "risk_level": "Unknown",
            "clinical_note": "Insufficient genomic data to make a recommendation",
            "alternative": None
        }

    prompt = f"""
You are a clinical pharmacogenomics expert.

Patient Enzyme Profile:
{enzyme_profile}

Drug: {drug_name}
Risk Score: {risk_score}

Respond ONLY with valid JSON.

Format:
{{
  "action": "Prescribe/Adjust/Avoid",
  "risk_level": "Low/Moderate/High",
  "clinical_note": "Short explanation",
  "alternative": "Optional safer drug"
}}
"""

    try:
        # 🔹 Primary attempt
        response = call_model(PRIMARY_MODEL, prompt)
        cleaned = clean_json_response(response.text)
        return json.loads(cleaned)

    except Exception:
        try:
            # 🔹 Fallback attempt
            response = call_model(FALLBACK_MODEL, prompt)
            cleaned = clean_json_response(response.text)
            return json.loads(cleaned)

        except Exception:
            return {
                "action": "Error",
                "risk_level": "Unknown",
                "clinical_note": "Model failed to generate a valid response",
                "alternative": None
            }


if __name__ == "__main__":
    enzyme_profile = {
        "CYP2D6": "Ultra-Rapid Metabolizer",
        "CYP2C19": "Normal",
        "CYP3A4": "Normal"
    }

    result = generate_clinical_recommendation(
        enzyme_profile,
        risk_score="High",
        drug_name="Codeine"
    )

    print(result)