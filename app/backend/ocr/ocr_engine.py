import pytesseract
import os
import shutil

# --- TESSERACT PATH CONFIGURATION ---
# Common macOS locations for tesseract
TESS_PATHS = [
    "/usr/local/bin/tesseract",      # Homebrew (Intel)
    "/opt/homebrew/bin/tesseract",   # Homebrew (Apple Silicon)
    "/usr/bin/tesseract",            # System
]

def find_tesseract():
    # 1. Check if it's already in the PATH
    path = shutil.which("tesseract")
    if path:
        return path
    
    # 2. Check common manual install paths
    for p in TESS_PATHS:
        if os.path.exists(p):
            return p
    return None

tess_path = find_tesseract()
if tess_path:
    pytesseract.pytesseract.tesseract_cmd = tess_path
# --- END CONFIGURATION ---

def extract_text(image) -> str:
    # Use config to improve OCR accuracy
    custom_config = r'--oem 3 --psm 6'
    raw_text = pytesseract.image_to_string(image, config=custom_config)

    if not raw_text.strip():
        return ""

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    return "\n".join(lines)
