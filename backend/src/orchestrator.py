import os
import json
import shutil
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import firebase_admin
from firebase_admin import auth, credentials
from src.agents.bio_sequencer import BioSequencer
from src.agents.chemist import Chemist
from src.agents.explainer import Explainer
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin
# In production, you'd use credentials.Certificate("path/to/serviceAccountKey.json")
# For this task, we assume the environment is set up.
try:
    firebase_admin.initialize_app()
except ValueError:
    # App already initialized
    pass

app = FastAPI(title="The Genetic Guardrail API")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GeneticGuardrail:
    """Production Orchestrator for Genetic Guardrail."""
    
    def __init__(self):
        self.chemist = Chemist()
        self.explainer = Explainer()

    def run_guardrail(self, vcf_path: str, drug_name: str):
        """Runs the full pipeline: Agent 1 -> Agent 2 -> Agent 3."""
        
        # 1. Bio-Sequencer
        bio_sequencer = BioSequencer(vcf_path)
        enzyme_profile = bio_sequencer.generate_enzyme_profile()
        
        # 2. Chemist
        simulation_result = self.chemist.simulate_binding(drug_name, enzyme_profile)
        
        if "error" in simulation_result:
            return {
                "status": "error",
                "message": simulation_result["error"]
            }

        # 3. Final Safety Check
        if simulation_result.get("confidence", 0) < 0.7:
            return {
                "status": "warning",
                "message": "Low simulation confidence. Manual review required.",
                "data": simulation_result
            }

        # 4. Explainer (Gemini)
        recommendation = self.explainer.generate_recommendation(
            drug_name, 
            enzyme_profile, 
            simulation_result
        )
        
        return {
            "status": "success",
            "patient_profile": enzyme_profile,
            "simulation": simulation_result,
            "recommendation": recommendation
        }

# Auth Dependency
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split("Bearer ")[1]
    try:
        # In a real setup, this verifies the Firebase ID Token
        # decoded_token = auth.verify_id_token(token)
        # return decoded_token
        return {"uid": "mock_user"} # Mock for now
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/analyze")
async def analyze(
    drug_name: str, 
    vcf_file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    # Save uploaded VCF temporarily
    temp_dir = "data/uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"{user['uid']}_{vcf_file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(vcf_file.file, buffer)
    
    try:
        orchestrator = GeneticGuardrail()
        result = orchestrator.run_guardrail(file_path, drug_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
