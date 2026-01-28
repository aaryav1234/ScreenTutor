import os
import sys

# Support PyInstaller bundles
if getattr(sys, 'frozen', False):
    root_dir = sys._MEIPASS
else:
    # Go up one level from 'dev/' to reach project root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(root_dir)

# Load .env relative to the root location
from dotenv import load_dotenv
load_dotenv(os.path.join(root_dir, ".env"))

if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("⚠️ Warning: OPENROUTER_API_KEY is not set.")
    
    from app.ui.main_window import main
    main()
