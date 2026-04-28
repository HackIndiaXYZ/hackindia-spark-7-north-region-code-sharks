"""
Local test script for The Genetic Guardrail backend modules.
"""

import sys
import os

# Add the current directory to path so we can import agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.agent1 import extract_enzyme_profile
from agents.agent2 import simulate_metabolism
from agents.agent3 import generate_clinical_recommendation

def test_pipeline():
    print("--- Starting Local Pipeline Test ---")
    
    # 1. Test Agent 1
    print("\n[Testing Agent 1]")
    profile = extract_enzyme_profile("mock_vcf_path")
    print(f"Enzyme Profile: {profile}")
    
    # 2. Test Agent 2
    print("\n[Testing Agent 2]")
    drug = "Codeine"
    risk = simulate_metabolism(profile, drug)
    print(f"Drug: {drug}, Risk: {risk}")
    
    # 3. Test Agent 3 (should trigger fallback if no API key)
    print("\n[Testing Agent 3]")
    recommendation = generate_clinical_recommendation(profile, risk, drug)
    print(f"Recommendation: {recommendation}")
    
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_pipeline()
