import requests
import time
import json

BASE_URL = "http://127.0.0.1:8003"

def test_test5_timeout():
    print("\n--- Running Test 5: Gemini Timeout Guard ---")
    start_time = time.time()
    try:
        # 'Abacavir' is NOT in the matrix, so it will trigger Agent 3 (AI)
        response = requests.post(
            f"{BASE_URL}/check-prescription",
            data={"drug_name": "Abacavir"}
        )
        duration = time.time() - start_time
        print(f"Request took: {duration:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=2))
            
            # Success criteria
            assert duration < 6.0, "Request took too long!"
            assert data["confidence"] == 0.5, "Wrong confidence for fallback!"
            assert "timeout" in data["clinical_note"].lower(), "Note should mention timeout!"
            print("Test 5 Passed: System returned fallback within timeout.")
        else:
            print(f"Test 5 Failed: Status code {response.status_code}")
    except Exception as e:
        print(f"Test 5 Failed with error: {e}")

def test_test6_crash():
    print("\n--- Running Test 6: Global Safety Net ---")
    try:
        response = requests.post(
            f"{BASE_URL}/check-prescription",
            data={"drug_name": "Codeine"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=2))
            
            # Success criteria
            assert data["confidence"] == 0.0, "Wrong confidence for crash!"
            assert data["risk_level"] == "Unknown", "Risk should be Unknown!"
            print("Test 6 Passed: System caught simulated crash safely.")
        else:
            print(f"Test 6 Failed: Status code {response.status_code}")
    except Exception as e:
        print(f"Test 6 Failed with error: {e}")

if __name__ == "__main__":
    # Ensure server is running on port 8003
    # Both tests are run together. 
    # If ENABLE_FORCE_FAILURE = True, Test 5 will also trigger the crash handler instead of the timeout handler.
    # To test them independently:
    # 1. Set ENABLE_FORCE_FAILURE = False, run -> Test 5 passes (Timeout)
    # 2. Set ENABLE_FORCE_FAILURE = True, run -> Test 6 passes (Crash)
    
    test_test5_timeout()
    test_test6_crash()
