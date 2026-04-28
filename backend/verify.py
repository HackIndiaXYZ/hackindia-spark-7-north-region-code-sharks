import sys
import os
import subprocess
import site
import importlib

def run_command(command):
    """Helper to run shell commands and return output safely."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()
    except FileNotFoundError:
        return "Command not found"

def check_environment():
    print("\n" + "="*40)
    print("        PYTHON ENVIRONMENT INFO         ")
    print("="*40)
    
    print(f"🐍 Executable Path: {sys.executable}")
    print(f"🐍 Version:         {sys.version.split()[0]}")
    print(f"📂 Working Dir:     {os.getcwd()}")
    
    # Virtual Env Check
    is_venv = (hasattr(sys, 'real_prefix') or 
               (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
    print(f"🛡️  Virtual Env:     {'Active ✅' if is_venv else 'Inactive ❌'}")
    
    print("\n📂 Site-Packages Locations:")
    for p in site.getsitepackages():
        print(f"   - {p}")
    if site.getusersitepackages() not in site.getsitepackages():
         print(f"   - {site.getusersitepackages()} (User Site)")

    print("\n🔍 Sys.Path (Where Python looks for modules):")
    for p in sys.path:
        if p: print(f"   - {p}")

def verify_modules():
    print("\n" + "="*40)
    print("             MODULE CHECK               ")
    print("="*40)
    
    modules_to_check = {
        "google.generativeai": "google-generativeai",
        "authlib": "authlib",
        "itsdangerous": "itsdangerous",
        "httpx": "httpx",
        "sqlalchemy": "sqlalchemy",
        "dotenv": "python-dotenv",
        "vcf": "PyVCF3",
        "qrcode": "qrcode",
        "pydantic": "pydantic"
    }
    
    missing_modules = []
    
    for import_name, pip_name in modules_to_check.items():
        try:
            importlib.import_module(import_name)
            print(f"✅ {import_name:<20} -> OK")
        except ImportError:
            print(f"❌ {import_name:<20} -> NOT FOUND (Needs: {pip_name})")
            missing_modules.append(pip_name)
            
    return missing_modules

def detect_issues(missing_modules):
    print("\n" + "="*40)
    print("           ISSUES DETECTED              ")
    print("="*40)
    
    issues_found = False
    
    # Check 1: Pip executable mismatch
    pip_path = run_command([sys.executable, "-m", "pip", "--version"])
    if "from" in pip_path:
        pip_location = pip_path.split("from ")[1].split(" ")[0]
        # Normalize paths for Windows comparison
        sys_prefix_norm = os.path.normpath(sys.prefix).lower()
        pip_loc_norm = os.path.normpath(pip_location).lower()
        
        if sys_prefix_norm not in pip_loc_norm:
            print(f"⚠️  WARNING: Pip mismatch detected!")
            print(f"   Your Python: {sys.executable}")
            print(f"   Pip is installing to: {pip_location}")
            print("   This is the #1 cause of 'ModuleNotFoundError' when packages are 'already installed'.")
            issues_found = True
            
    # Check 2: Multiple pythons in PATH (Windows specific)
    where_python = run_command(["where", "python"])
    if "Command not found" not in where_python and len(where_python.split('\n')) > 1:
        print(f"⚠️  WARNING: Multiple Python installations detected in PATH:")
        for line in where_python.split('\n'):
            print(f"   - {line}")
        print("   Using 'pip install' directly might install to the wrong version.")
        issues_found = True
        
    if missing_modules:
        print(f"⚠️  WARNING: {len(missing_modules)} required modules are missing from current environment.")
        issues_found = True
        
    if not issues_found:
        print("✅ No glaring environment issues detected.")
        
    return missing_modules

def suggest_fixes(missing_modules):
    if not missing_modules:
        return
        
    print("\n" + "="*40)
    print("           SUGGESTED FIXES              ")
    print("="*40)
    
    print("To install the missing packages into THIS specific Python environment, run:")
    
    # Constructing the safest Windows command
    # Assuming py -3.11 is requested based on prompt, but dynamically generating the exact executable is safer.
    # We will provide the exact executable path to guarantee it goes to the right place.
    
    cmd = f'"{sys.executable}" -m pip install {" ".join(missing_modules)}'
    
    print(f"\n{cmd}\n")
    print("Alternatively, if you prefer the py launcher:")
    print(f"py -3.11 -m pip install {' '.join(missing_modules)}\n")

def print_pip_list():
    print("\n" + "="*40)
    print("          BONUS: PIP LIST               ")
    print("="*40)
    
    pip_list = run_command([sys.executable, "-m", "pip", "list"])
    print(pip_list)

if __name__ == "__main__":
    check_environment()
    missing = verify_modules()
    detect_issues(missing)
    suggest_fixes(missing)
    print_pip_list()
