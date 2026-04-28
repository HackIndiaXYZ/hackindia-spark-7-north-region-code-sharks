import sys

REQUIRED_PACKAGES = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "sqlalchemy",
    "itsdangerous",      # Required by starlette SessionMiddleware
    "python-multipart",  # Required by fastapi for Form and File uploads
    "authlib",           # Required for OAuth
    "httpx",             # Required by agent2 for BioNeMo API and authlib
    "google-genai"       # Required by agent3 for Gemini API
]

def check_environment():
    print("="*40)
    print("GENETIC GUARDRAIL - ENV AUDIT")
    print("="*40)
    
    all_ready = True
    for package in REQUIRED_PACKAGES:
        try:
            # Map package names to import names where they differ
            import_name = package
            if package == "python-multipart":
                import_name = "multipart"
            elif package == "google-genai":
                import_name = "google.genai"
                
            __import__(import_name)
            print(f"[READY]   {package:<18}")
        except ImportError:
            print(f"[MISSING] {package:<18}")
            all_ready = False

    print("="*40)
    if all_ready:
        print("ENVIRONMENT IS 100% READY. NO MISSING MODULES.")
    else:
        print("CRITICAL: Missing packages detected.")
        print("Run the following command to fix:")
        print(f"pip install {' '.join(REQUIRED_PACKAGES)}")
        sys.exit(1)

if __name__ == "__main__":
    check_environment()
