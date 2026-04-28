import requests

def test_test6_global_error_handler():
    print("Starting Test 6 Verification: Global Error Handler")
    API_URL = "http://127.0.0.1:8002/check-prescription"
    
    # Send a request - since ENABLE_TEST_ERROR is True, it should trigger the exception
    response = requests.post(API_URL, data={"drug_name": "Codeine"})
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    expected_response = {
        "action": "Manual Review Required",
        "risk_level": "Unknown",
        "clinical_note": "A technical error occurred during genomic analysis. Please consult a pharmacist.",
        "alternative": "Manual Pharmacogenomic Review",
        "confidence": 0.0
    }
    
    for key, value in expected_response.items():
        assert data[key] == value, f"Mismatch in {key}: expected {value}, got {data[key]}"
    
    print("✅ Test 6 Passed: System returned safe fallback JSON on simulated failure.")

if __name__ == "__main__":
    test_test6_global_error_handler()
