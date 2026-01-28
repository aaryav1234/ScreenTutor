#!/bin/bash

# Create a macOS .app bundle for ScreenTutor
echo "📦 Building ScreenTutor.app..."

# 1. Ensure dependencies are installed
./venv/bin/pip install pyinstaller python-dotenv PyQt5 Pillow pytesseract requests

# 2. Build the app using PyInstaller
# --paths . tells PyInstaller to look in the current directory for modules (like 'app')
# --add-data ".env:." includes the environment file
# --hidden-import "PIL._tkinter_finder" is needed for Pillow on Mac
./venv/bin/pyinstaller --noconfirm --windowed \
    --name "ScreenTutor" \
    --paths "." \
    --add-data ".env:." \
    --hidden-import "PIL._tkinter_finder" \
    --collect-all PyQt5 \
    dev/run.py

# 3. Ad-hoc sign the app to help with macOS permissions
echo "🔒 Ad-hoc signing ScreenTutor.app..."
codesign --force --deep --sign - dist/ScreenTutor.app

echo "✨ Build complete! You can find 'ScreenTutor.app' in the 'dist' folder."
echo "👉 Move it to your Applications folder to use it like any other app."

