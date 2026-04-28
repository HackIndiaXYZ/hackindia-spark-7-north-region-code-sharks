import requests
import os

API_URL = "http://127.0.0.1:8002/check-prescription"
VCF_PATH = "data/mock_variants.vcf"

def test_request(drug_name=None, file_path=None):
    print(f"\n--- Testing Drug: {drug_name if drug_name else 'MISSING'} | File: {file_path if file_path else 'MISSING'} ---")
    
    data = {}
    if drug_name:
        data["drug_name"] = drug_name
        
    files = {}
    if file_path and os.path.exists(file_path):
        files["file"] = open(file_path, "rb")
    
    try:
        response = requests.post(API_URL, data=data, files=files if files else None)
        if response.status_code == 200:
            print("Success!")
            print(response.json())
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        if "file" in files:
            files["file"].close()

if __name__ == "__main__":
    # Test Step 1: Corrected Logic (Codeine)
    # Expected: CYP2D6 Poor -> Moderate (from 0.95 confidence)
    test_request("Codeine", VCF_PATH)
    
    # Test Step 2: Low Risk -> Alternative = null
    # Note: Clopidogrel with normal profile (not in mock VCF) would be Low
    test_request("Aspirin", VCF_PATH) # Should be Low or Moderate depending on heuristic
    
    # Test Step 3: Zero-Fail (Missing drug)
    test_request(drug_name=None, file_path=VCF_PATH)
    
    # Test Step 4: Zero-Fail (Missing file)
    test_request(drug_name="Warfarin", file_path=None)
    
    # Test Step 5: Zero-Fail (Missing EVERYTHING)
    test_request(drug_name=None, file_path=None)

