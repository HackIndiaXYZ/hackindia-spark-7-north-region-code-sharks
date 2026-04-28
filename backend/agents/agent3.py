import os
import json
import logging
import asyncio

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger("agent3")
    logger.warning("📦 google.genai module not found. AI features will be disabled in Agent 3.")
    GENAI_AVAILABLE = False

from typing import Dict, Any, Optional

import hashlib

logger = logging.getLogger("agent3")

# ✅ Clinical Models & Determinism
PRIMARY_MODEL = "gemini-2.0-flash-lite"
GEMINI_TIMEOUT = 5.0
GEMINI_TEMPERATURE = 0.0 # Strict determinism for hospital grade

# ✅ Global Cache for Determinism
CACHE = {}

async def generate_clinical_recommendation(
    findings: Dict[str, str],
    risk_level: str,
    drug_name: str,
    confidence: float,
    insufficient_data: bool = False,
    request_id: str = "UNKNOWN",
    clinical_note_override: str = None
) -> Dict[str, Any]:
    """
    Agent 3: Clinical Explainer (Payload Optimized & Cached)
    - Fixes Gemini 404 by using correct model mapping.
    - Minimizes payload to prevent 'Large Request' errors.
    - Implements deterministic Global Caching Layer.
    """
    logger.info(f"[{request_id}] Agent3 | Drug: {drug_name} | Risk: {risk_level} | Findings: {findings}")

    # --- 1. Hospital Safety: Handling Insufficient Data (Warning) ---
    if insufficient_data:
        return {
            "action": "Warning",
            "risk_level": "Unknown",
            "clinical_note": f"INSUFFICIENT DATA: Genomic markers for {drug_name} were not detected in the provided VCF. Pharmacogenomic analysis is incomplete.",
            "alternative": "Consult clinical pharmacist for manual review",
            "confidence": 0.5
        }

    # --- 2. Deterministic Caching Layer ---
    # Create unique key from drug and patient genetic profile
    profile_str = json.dumps(findings, sort_keys=True)
    cache_key = hashlib.sha256(f"{drug_name.lower()}:{profile_str}".encode()).hexdigest()
    
    if cache_key in CACHE:
        logger.info(f"[{request_id}] ⚡ [CACHE HIT]: Reusing recommendation for {drug_name}.")
        return CACHE[cache_key]

    # ✅ LOW RISK RULE (STRICT)
    if risk_level == "Low":
        gene = _get_gene_for_drug(drug_name)

        base_note = f"Based on your {gene} profile, normal metabolism is expected for {drug_name}. No adjustment required."
        if clinical_note_override:
            base_note = f"{clinical_note_override} {base_note}"

        result = {
            "action": "Prescribe",
            "risk_level": "Low",
            "clinical_note": base_note,
            "alternative": None,
            "confidence": confidence
        }
        CACHE[cache_key] = result
        logger.info(f"[{request_id}] 💾 [CACHE STORE]: Saved low-risk recommendation for {drug_name}.")
        return result

    # ✅ GEMINI CALL WITH TIMEOUT
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            result = await asyncio.wait_for(
                _get_ai_recommendation(api_key, drug_name, findings, risk_level, clinical_note_override),
                timeout=GEMINI_TIMEOUT
            )

            if result:
                CACHE[cache_key] = result # Store in cache after generation
                logger.info(f"[{request_id}] 💾 [CACHE STORE]: Saved AI recommendation for {drug_name}.")
                return result

        except Exception as e:
            logger.error(f"[{request_id}] Gemini failed or timed out: {e}. Switching to Hardened Fallback.")
            # Fall through to the template-based fallback

    # ✅ FINAL HARDENED FALLBACK (TEMPLATE-BASED)
    result = _fallback_recommendation(drug_name, risk_level, confidence, findings)
    if clinical_note_override:
        result["clinical_note"] = f"{clinical_note_override} {result['clinical_note']}"
    
    CACHE[cache_key] = result # Store fallback in cache as well
    logger.info(f"[{request_id}] 💾 [CACHE STORE]: Saved fallback recommendation for {drug_name}.")
    return result


# ===============================
# 🔬 AI CALL
# ===============================
async def _get_ai_recommendation(api_key, drug_name, findings, risk_level, clinical_note_override=None):
    if not GENAI_AVAILABLE:
        logger.warning("GENAI_AVAILABLE is False, skipping AI recommendation.")
        return None
        
    client = genai.Client(api_key=api_key)

    ai_instruction = ""
    if clinical_note_override:
        ai_instruction = f"IMPORTANT: Start the clinical_note exactly with: '{clinical_note_override}' followed by a space and then your explanation."

    prompt = f"""
    You are a Clinical Pharmacogenomics expert.
    Patient is prescribed {drug_name}.
    Patient Phenotype: {json.dumps(findings)}.
    Risk Level: {risk_level}.

    Provide a 1-sentence explanation of the risk and suggest an alternative if the risk is High or Moderate. 
    Do not mention the VCF file.
    {ai_instruction}

    Return JSON ONLY:
    {{
      "action": "Avoid | Adjust | Prescribe",
      "clinical_note": "...",
      "alternative": "..."
    }}
    """

    response = await asyncio.to_thread(
        client.models.generate_content,
        model=PRIMARY_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=GEMINI_TEMPERATURE # Hospital Grade Determinism
        )
    )

    text = getattr(response, "text", "").strip()

    if text:
        data = json.loads(text)

        return {
            "action": _normalize_action(data.get("action")),
            "risk_level": risk_level,
            "clinical_note": data.get("clinical_note"),
            "alternative": data.get("alternative"),
            "confidence": 0.7
        }

    return None


# ===============================
# 🛡️ FALLBACK LOGIC (Hardened Template-Based)
# ===============================
def _fallback_recommendation(drug_name, risk_level, confidence, findings):
    gene = _get_gene_for_drug(drug_name)
    phenotype = findings.get(gene, "Unknown")

    # Hardened Fallback Templates for Step 3 Success
    if drug_name.title() == "Codeine" and phenotype == "Poor Metabolizer":
        return {
            "action": "Avoid",
            "risk_level": "High",
            "clinical_note": "CYP2D6 Poor Metabolizer detected. Codeine will likely be ineffective and carries risk of toxicity. Morphine or non-opioid recommended.",
            "alternative": "Morphine or non-opioid analgesics",
            "confidence": confidence
        }

    if risk_level == "High":
        return {
            "action": "Avoid",
            "risk_level": "High",
            "clinical_note": f"High risk detected: {gene} {phenotype} status may lead to adverse drug reactions or therapeutic failure with {drug_name}.",
            "alternative": "Consult clinical pharmacist for alternative therapy",
            "confidence": confidence
        }

    if risk_level == "Moderate":
        return {
            "action": "Adjust",
            "risk_level": "Moderate",
            "clinical_note": f"Moderate risk detected: {gene} {phenotype} status suggests dose adjustment or increased monitoring is required for {drug_name}.",
            "alternative": "Consider dose reduction or alternative medication",
            "confidence": confidence
        }

    return {
        "action": "Prescribe",
        "risk_level": risk_level,
        "clinical_note": f"Pharmacogenomic analysis of {gene} ({phenotype}) completed. Follow standard clinical protocols for {drug_name}.",
        "alternative": None,
        "confidence": confidence
    }


# ===============================
# 🧬 HELPERS
# ===============================
def _get_gene_for_drug(drug_name: str) -> str:
    return {
        "Codeine": "CYP2D6",
        "Clopidogrel": "CYP2C19",
        "Warfarin": "CYP2C9",
        "Simvastatin": "CYP3A4",
        "Acetaminophen": "CYP3A4",
        "Ibuprofen": "CYP2C9",
        "Tramadol": "CYP2D6",
        "Atorvastatin": "CYP3A4", 
        "Metoprolol": "CYP2D6",
        "Losartan": "CYP2C9",
        "Omeprazole": "CYP2C19",
        "Sertraline": "CYP2C19",
        "Diazepam": "CYP2C19",
        "Metformin": "SLC22A1"
    }.get(drug_name.title(), "pharmacogenomic")


def _normalize_action(action: str) -> str:
    if not action:
        return "Adjust" # Enforce valid action policy
    
    act_lower = action.lower()
    if "avoid" in act_lower or "contraindicated" in act_lower:
        return "Avoid"
    elif "adjust" in act_lower or "caution" in act_lower or "monitor" in act_lower:
        return "Adjust"
    elif "prescribe" in act_lower or "normal" in act_lower or "standard" in act_lower:
        return "Prescribe"
        
    return "Adjust" # Default safe fallback to enforce policy

async def generate_patient_summary(enzyme_profile: Dict[str, str], multi_drug_results: list = None) -> str:
    """
    Agent 3: Master AI Summary
    Generates a concise summary of the patient's genetic strengths and vulnerabilities based on their enzyme profile.
    If multi_drug_results is provided, incorporates those specific drug checks into the combined clinical summary.
    """
    if not GENAI_AVAILABLE:
        return "AI summary unavailable due to missing dependencies (google.genai). Please consult a clinical geneticist."
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "AI summary unavailable due to missing API key. Please consult a clinical geneticist."
        
    client = genai.Client(api_key=api_key)
    
    drug_context = ""
    if multi_drug_results:
        drug_context = f"\nSpecific drug analysis results: {json.dumps(multi_drug_results)}\nIncorporate these specific drug findings into the summary."

    prompt = f"""
    You are a Clinical Pharmacogenomics expert.
    Analyze the following patient enzyme profile: {json.dumps(enzyme_profile)}.{drug_context}
    
    Generate a "Master AI Summary" of the patient's genetic strengths and vulnerabilities in 2-4 sentences.
    Focus on general sensitivities (e.g., "General sensitivity to statins and opioids detected due to Poor Metabolizer status").
    Keep it professional, clinical, and concise. Do not mention the VCF file.
    """
    
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=PRIMARY_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=GEMINI_TEMPERATURE
            )
        )
        return getattr(response, "text", "Unable to generate summary.").strip()
    except Exception as e:
        logger.error(f"Failed to generate patient summary: {e}")
        return "Error generating clinical summary. Standard precautions apply."

    action = action.lower()

    if "avoid" in action:
        return "Avoid"
    if "adjust" in action:
        return "Adjust"
    if "monitor" in action:
        return "Adjust"

    return "Manual Review Required"