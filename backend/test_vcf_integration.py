import requests
import os

# Configuration
URL = "http://127.0.0.1:8001/check-prescription"
VCF_PATH = os.path.abspath("data/mock_variants.vcf")

def test_vcf_request(drug_name):
    payload = {
        "drug_name": drug_name,
        "vcf_data": VCF_PATH
    }
    headers = {"Content-Type": "application/json"}
    
    print(f"\n--- Testing Drug: {drug_name} with VCF: {VCF_PATH} ---")
    try:
        response = requests.post(URL, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test cases based on clinical rules
    test_vcf_request("Codeine")
    test_vcf_request("Clopidogrel")
    test_vcf_request("Aspirin") # Should be low risk
