import sys
import subprocess

def check_and_install_dependencies():
    required = ["google-generativeai", "authlib", "itsdangerous", "httpx", "sqlalchemy", "python-dotenv", "PyVCF3", "qrcode", "pydantic", "fastapi", "uvicorn", "starlette", "python-multipart"]
    for package in required:
        try:
            # Map pip package names to python import names
            import_name = package.replace("-", "_")
            if package == "google-generativeai":
                import_name = "google.generativeai"
            elif package == "python-dotenv":
                import_name = "dotenv"
            elif package == "PyVCF3":
                import_name = "vcf"
            
            __import__(import_name)
        except ImportError:
            print(f"Missing {package}. Attempting auto-install...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Execute pre-flight check
check_and_install_dependencies()

import os
os.environ['CURL_CA_BUNDLE'] = ''

import asyncio
import json
import logging
import tempfile
import uuid
import shutil
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, Request, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

# -----------------------------
# PDF Generation Import
# -----------------------------
from report_generator import generate_clinical_pdf

# -----------------------------
# Database & Auth Integrations
# -----------------------------
from database import get_db, User, VCFFile, DrugCheckHistory
from authlib.integrations.starlette_client import OAuth


# ✅ Test 6: Global SafetyNet Variable
ENABLE_FORCE_FAILURE = False

# ==============================
# 🧾 LOGGING
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("genetic-guardrail")

# ==============================
# 🤖 AGENTS
# ==============================
from agents.agent1 import extract_enzyme_profile
from agents.agent2 import calculate_risk
from agents.agent3 import generate_clinical_recommendation, generate_patient_summary

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# ==============================
# 🚀 APP
# ==============================
app = FastAPI(title="Genetic Guardrail - Clinical Grade")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure Storage & Data Directories Exist
STORAGE_DIR = "./storage"
DATA_DIR = "./data"
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Add SessionMiddleware for OAuth
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("CRITICAL: SECRET_KEY environment variable is missing. Check your .env file.")

app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    session_cookie="genetic_guardrail_session",
    same_site="lax",
    https_only=False,
    max_age=3600
)


# OAuth Setup
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
        "verify": False
    }
)

class AuthException(Exception):
    pass

@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=401,
        content={"error": "Authentication required. Please sign in with Google."}
    )

def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise AuthException()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthException()
    return user

# ==============================
# 📦 RESPONSE MODEL (Phase 3 UI Prep)
# ==============================
class MultiDrugRequest(BaseModel):
    drug_names: List[str]

class UIMetrics(BaseModel):
    risk_gauge: int # 0-100
    metabolic_radar: dict # Radar chart data points
    clinical_timeline: list # Timeline events
    enzyme_profile: dict = {} # Added for dynamic UI display

class ClinicalResponse(BaseModel):
    drug: str
    action: str
    risk_level: str
    clinical_note: str
    alternative: Optional[str] = None
    confidence: float
    toxicity_score: float = 0.0
    radar_data: dict

class MultiDrugResponse(BaseModel):
    user_id: str
    drug_results: List[ClinicalResponse]

class VCFFileResponse(BaseModel):
    id: int
    filename: str
    upload_date: str

class UserInfo(BaseModel):
    name: str
    email: str
    analysis_id: Optional[str] = None

class DrugReportItem(BaseModel):
    drug_name: str
    risk_level: str
    action: str
    clinical_note: str
    alternative: Optional[str] = None
    toxicity_level: float = 0.0

class ReportRequest(BaseModel):
    user_info: UserInfo
    enzyme_profile: dict
    drug_results: List[DrugReportItem]



# ==============================
# 🛡 GLOBAL ERROR HANDLER
# ==============================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"GLOBAL ERROR CAUGHT: {exc}", exc_info=True)
    return JSONResponse(
        status_code=200,
        content={
            "user_id": "Unknown",
            "drug_results": [{
                "drug": "Unknown",
                "action": "Manual Review Required",
                "risk_level": "Unknown",
                "clinical_note": f"A technical error occurred during genomic analysis. Detail: {str(exc)}",
                "alternative": "Manual Pharmacogenomic Review",
                "confidence": 0.0,
                "toxicity_score": 0.0,
                "radar_data": {"Metabolism": 0.0, "Binding": 0.0, "Toxicity": 0.0, "Confidence": 0.0}
            }]
        }
    )


# ==============================
# ❤️ HEALTH CHECK
# ==============================
@app.get("/")
def health_check():
    return {"status": "Clinical Guardrail Active"}

# ==============================
# 🔐 AUTH & PERSISTENCE
# ==============================
@app.get("/auth/login")
async def login(request: Request):
    """Initiates Google OAuth Flow"""
    print("🔐 Starting OAuth flow")
    print(f"DEBUG: Session content before redirect: {request.session}")
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, str(redirect_uri))

@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handles Google OAuth Callback and User Persistence"""
    try:
        print("🔁 Callback received")
        print(f"DEBUG: Session content in callback: {request.session}")
        token = await oauth.google.authorize_access_token(request)
        print("✅ TOKEN:", token)
        
        user_info = token.get("userinfo")
        print("✅ USER:", user_info)
        
        if not user_info:
            return JSONResponse(status_code=400, content={"error": "User info not found in token"})

        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")
        
        # Save or fetch user from DB
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name=name, profile_pic=picture)
            db.add(user)
            db.commit()
            db.refresh(user)
            
        # Store user in session
        request.session['user_id'] = user.id

        # Redirect to frontend dashboard
        return RedirectResponse(url="http://127.0.0.1:5173/dashboard")
        
    except Exception as e:
        print("❌ OAuth Error:", str(e))
        logger.error(f"OAuth Callback Error: {e}", exc_info=True)
        return {"error": "Authentication failed"}

@app.get("/files", response_model=List[VCFFileResponse])
async def get_files(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    files = db.query(VCFFile).filter(VCFFile.user_id == user.id).order_by(VCFFile.id.desc()).all()
    return [
        VCFFileResponse(
            id=f.id, 
            filename=f.filename, 
            upload_date=f.upload_date.isoformat() if f.upload_date else ""
        ) for f in files
    ]

@app.post("/upload-vcf")
async def upload_vcf(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        from datetime import datetime
        import time
        
        # 1. Physical Save: Save the file using a unique name in storage/
        # Use os.path.join for Windows compatibility
        timestamp = int(time.time())
        safe_filename = f"{timestamp}_{file.filename}"
        saved_path = os.path.join(STORAGE_DIR, safe_filename)
        
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Database Registration
        new_vcf = VCFFile(
            user_id=user.id,
            filename=file.filename,
            file_path=saved_path,
            upload_date=datetime.now()
        )
        db.add(new_vcf)
        db.commit()
        db.refresh(new_vcf)
        
        return {"message": "File uploaded successfully", "file_id": new_vcf.id}
    except Exception as e:
        logger.error(f"Error uploading VCF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@app.delete("/files/{file_id}")
async def delete_file(file_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Verify the file belongs to the logged-in user
    vcf_record = db.query(VCFFile).filter(VCFFile.id == file_id, VCFFile.user_id == user.id).first()
    if not vcf_record:
        raise HTTPException(status_code=404, detail="File not found or unauthorized")

    # 2. Delete the file from the physical storage/ folder
    try:
        if os.path.exists(vcf_record.file_path):
            os.remove(vcf_record.file_path)
    except Exception as e:
        logger.error(f"Error deleting physical file {vcf_record.file_path}: {e}")
        # Continue to delete DB record even if physical file is missing or locked

    # 3. Delete the record from the VCF_Files database table
    db.delete(vcf_record)
    db.commit()

    return {"message": "File successfully deleted"}

@app.get("/auth/me")
async def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "profile_pic": user.profile_pic,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

# ==============================
# 🧠 MAIN PIPELINE
# ==============================
@app.post("/check-prescription", response_model=MultiDrugResponse)
async def check_prescription(
    request_data: MultiDrugRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    # Generate unique Request ID
    request_id = str(uuid.uuid4())[:8]

    # Identify User
    user_id = request.session.get("user_id")
    if not user_id:
        # If session is lost, return a clear 401 instead of "Unknown"
        raise HTTPException(status_code=401, detail="Session expired. Please login again.")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    drugs_to_check = list(set([d.strip() for d in request_data.drug_names if d.strip()]))

    # ---------------------------
    # 🧾 Validate Input
    # ---------------------------
    if not drugs_to_check:
        raise HTTPException(status_code=400, detail="drug_names cannot be empty")

    logger.info(f"[{request_id}] Incoming request for user {user.email} | Drugs: {drugs_to_check}")

    try:
        # ✅ Test 6: Simulated failure for testing
        if ENABLE_FORCE_FAILURE:
            logger.warning(f"[{request_id}] Test 6 Triggered: Simulated crash")
            raise Exception("Simulated System Crash")

        # ---------------------------
        # 🧬 Agent 1: Parser (Fetch VCF)
        # ---------------------------
        latest_vcf = db.query(VCFFile).filter(VCFFile.user_id == user.id).order_by(VCFFile.id.desc()).first()
        if not latest_vcf or not os.path.exists(latest_vcf.file_path):
            logger.warning(f"[{request_id}] Security Guardrail: No VCF found for user {user.email}")
            raise HTTPException(status_code=404, detail="Please upload a VCF file before running an analysis.")

        logger.info(f"[{request_id}] Found VCF for user. Beginning scan...")
        try:
            enzyme_profile = await extract_enzyme_profile(latest_vcf.file_path)
        except Exception as e:
            logger.error(f"[{request_id}] Agent 1 Failure: {e}")
            raise HTTPException(status_code=500, detail="Failed to process genomic data.")

        # ---------------------------
        # 🧪 Agent 2 & 📝 Agent 3: Parallel Processing
        # ---------------------------
        async def analyze_single_drug(drug_name: str, file_path: str, enzyme_prof: dict):
            try:
                risk_data = await calculate_risk(enzyme_prof, drug_name)
                
                # --- Guardrail: Pass through Invalid Drugs ---
                if risk_data.get("invalid_drug", False):
                    return ClinicalResponse(
                        drug=drug_name,
                        action=risk_data.get("action", "Invalid Drug"),
                        risk_level=risk_data.get("risk_level", "Unknown"),
                        clinical_note=risk_data.get("clinical_note", f"The drug name '{drug_name}' was not recognized."),
                        alternative=None,
                        confidence=0.0,
                        toxicity_score=0.0,
                        radar_data=risk_data.get("radar_data", {"Metabolism": 0.0, "Binding": 0.0, "Toxicity": 0.0, "Confidence": 0.0})
                    )
                
                drug_key = drug_name.title()
                primary_gene = {
                    "Codeine": "CYP2D6",
                    "Clopidogrel": "CYP2C19",
                    "Warfarin": "CYP2C9",
                    "Simvastatin": "CYP3A4"
                }.get(drug_key, "pharmacogenomic")
                
                minimal_findings = {primary_gene: enzyme_prof.get(primary_gene, "Unknown")}

                recommendation = await generate_clinical_recommendation(
                    findings=minimal_findings,
                    risk_level=risk_data["risk_level"],
                    drug_name=drug_name,
                    confidence=risk_data["confidence"],
                    insufficient_data=risk_data.get("insufficient_data", False),
                    request_id=request_id,
                    clinical_note_override=risk_data.get("clinical_note_override")
                )
                
                clinical_note = recommendation.get("clinical_note", "No note available.")
                
                # Toxicity Logic
                toxicity = risk_data.get("toxicity_level", 0.0)
                if risk_data.get("risk_level") == "Unknown" and toxicity == 0.0:
                    toxicity = 0.1 # Default low score for unknown drugs
                    
                radar_data = risk_data.get("radar_data", {
                    "Metabolism": 0.2 if risk_data.get("risk_level") == "High" else 0.8,
                    "Binding": 0.9 if toxicity > 0.5 else 0.4,
                    "Toxicity": toxicity,
                    "Confidence": risk_data.get("confidence", 0.0)
                })
                
                # Save history if user exists
                try:
                    if 'user' in locals() and user:
                        history_record = DrugCheckHistory(
                            user_id=user.id,
                            drug_name=drug_name,
                            risk_level=risk_data["risk_level"],
                            toxicity_score=toxicity
                        )
                        db.add(history_record)
                except Exception as e:
                    logger.error(f"[{request_id}] Failed to save drug history: {e}")

                return ClinicalResponse(
                    drug=drug_name,
                    action=recommendation.get("action", "Unknown"),
                    risk_level=risk_data.get("risk_level", "Unknown"),
                    clinical_note=clinical_note,
                    alternative=recommendation.get("alternative"),
                    confidence=risk_data.get("confidence", 0.0),
                    toxicity_score=toxicity,
                    radar_data=radar_data
                )
            except Exception as e:
                logger.error(f"[{request_id}] Error processing drug {drug_name}: {e}")
                # Return a safe fallback for the failed drug so others can continue
                return ClinicalResponse(
                    drug=drug_name,
                    action="Error",
                    risk_level="Unknown",
                    clinical_note=f"Analysis failed for {drug_name}.",
                    alternative=None,
                    confidence=0.0,
                    toxicity_score=0.1,
                    radar_data={
                        "Metabolism": 0.0,
                        "Binding": 0.0,
                        "Toxicity": 0.1,
                        "Confidence": 0.0
                    }
                )

        results = await asyncio.gather(*(analyze_single_drug(d, latest_vcf.file_path, enzyme_profile) for d in drugs_to_check))
        
        # Commit all history records
        try:
            db.commit()
        except Exception as e:
            logger.error(f"[{request_id}] Error committing history records: {e}")
            db.rollback()

        # Prepare MultiDrugResponse
        multi_response = MultiDrugResponse(
            user_id=str(user.id),
            drug_results=list(results)
        )

        return multi_response

    except Exception as e:
        logger.error(f"[{request_id}] PIPELINE CRASH: {e}", exc_info=True)
        # Re-raise to trigger global exception handler
        raise e
    
    finally:
        pass

# ==============================
# 👤 PATIENT INTELLIGENCE
# ==============================

@app.get("/patient/summary")
async def get_patient_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get the latest VCF file for the user
    latest_vcf = db.query(VCFFile).filter(VCFFile.user_id == user.id).order_by(VCFFile.upload_date.desc()).first()
    
    if not latest_vcf or not os.path.exists(latest_vcf.file_path):
        return {"summary": "No genomic data available. Please upload a VCF file to generate a clinical summary."}
        
    try:
        # Agent 1 parses entire VCF for known pharmacogenes
        enzyme_profile = await extract_enzyme_profile(latest_vcf.file_path)
        
        # Agent 3 generates "Master AI Summary"
        master_summary = await generate_patient_summary(enzyme_profile)
        
        return {"summary": master_summary, "enzyme_profile": enzyme_profile}
    except Exception as e:
        logger.error(f"Failed to generate patient summary: {e}")
        return {"summary": "Error generating summary. Please try again later."}

@app.get("/patient/history")
async def get_patient_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Return a sorted list of every drug ever checked for this user with its final risk level
    history = db.query(DrugCheckHistory).filter(DrugCheckHistory.user_id == user.id).order_by(DrugCheckHistory.created_at.desc()).all()
    
    results = []
    for record in history:
        results.append({
            "id": record.id,
            "drug_name": record.drug_name,
            "risk_level": record.risk_level,
            "toxicity_score": record.toxicity_score,
            "checked_at": record.created_at.isoformat() if record.created_at else None
        })
        
    return {"history": results}

@app.get("/passport/{user_id}")
async def get_patient_passport(
    user_id: int,
    db: Session = Depends(get_db)
):
    # Return Patient Summary and History in a lightweight JSON format
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    # Get History
    history = db.query(DrugCheckHistory).filter(DrugCheckHistory.user_id == user_id).order_by(DrugCheckHistory.created_at.desc()).all()
    history_data = [{"drug": h.drug_name, "risk": h.risk_level, "toxicity": h.toxicity_score, "date": h.created_at.isoformat() if h.created_at else None} for h in history]
    
    # Get Summary (if VCF exists)
    summary_text = "No genomic data available."
    latest_vcf = db.query(VCFFile).filter(VCFFile.user_id == user_id).order_by(VCFFile.upload_date.desc()).first()
    if latest_vcf and os.path.exists(latest_vcf.file_path):
        try:
            enzyme_profile = await extract_enzyme_profile(latest_vcf.file_path)
            summary_text = await generate_patient_summary(enzyme_profile)
        except Exception as e:
            logger.error(f"Passport summary error: {e}")
            summary_text = "Error generating summary."
            
    return {
        "patient_id": user_id,
        "name": user.name,
        "summary": summary_text,
        "history": history_data
    }

# ==============================
# 📄 CLINICAL PDF REPORT
# ==============================
@app.post("/generate-report")
async def generate_report(req: ReportRequest):
    try:
        # Generate the PDF using model_dump() instead of deprecated dict()
        pdf_bytes = generate_clinical_pdf(
            user_info=req.user_info.model_dump(),
            enzyme_profile=req.enzyme_profile,
            drug_results=[d.model_dump() for d in req.drug_results]
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Genetic_Guardrail_Report.pdf"}
        )
    except Exception as e:
        logger.error(f"Failed to generate clinical PDF report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate report")

# ==============================
# ENTRY POINT
# ==============================

