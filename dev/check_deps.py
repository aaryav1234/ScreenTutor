import sys
import subprocess

def check_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name} is installed.")
        return True
    except ImportError:
        print(f"❌ {module_name} is MISSING.")
        return False

def check_tesseract():
    try:
        # Pytesseract check
        import pytesseract
        # Try to call tesseract version
        version = subprocess.check_output(['tesseract', '--version'], stderr=subprocess.STDOUT).decode()
        print(f"✅ tesseract binary found: {version.splitlines()[0]}")
        return True
    except (ImportError, FileNotFoundError, subprocess.CalledProcessError):
        print("❌ tesseract binary is MISSING. Install with: brew install tesseract")
        return False

print("--- ScreenTutor Dependency Check ---")
print(f"Python version: {sys.version}")
print("-" * 35)

critical_modules = [
    "PyQt5",
    "PIL", # Pillow
    "pytesseract",
    "openai",
    "requests"
]

all_passed = True
for mod in critical_modules:
    if not check_import(mod):
        all_passed = False

if not check_tesseract():
    all_passed = False

print("-" * 35)
if all_passed:
    print("🚀 All critical dependencies found! You are ready to go.")
else:
    print("⚠️ Some dependencies are missing. Run: pip install -r requirements.txt")
