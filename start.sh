#!/bin/bash

# PDF Master Pro - Complete Setup & Run Guide

echo "╔══════════════════════════════════════╗"
echo "║   PDF Master Pro - Setup Assistant   ║"
echo "╚══════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")" 2>/dev/null || cd "/media/abhishek-atole/Data Folder/Developed Application/PDF Splitter"

echo "📁 Current directory:"
pwd
echo ""

echo "🔍 Checking environment..."
echo ""

# Check if myenv_new exists
if [ -d "myenv_new" ]; then
    echo "✅ myenv_new virtual environment found"
else
    echo "❌ myenv_new not found!"
    echo "   Please create it: python3.12 -m venv myenv_new"
    exit 1
fi

# Check if required packages are installed
echo ""
echo "📦 Checking installed packages..."
./myenv_new/bin/python -c "
import sys
packages = ['PyPDF2', 'pdf2image', 'Pillow', 'tkinter']
all_good = True
for pkg in packages:
    try:
        __import__(pkg)
        print(f'  ✅ {pkg}')
    except ImportError:
        print(f'  ❌ {pkg} missing')
        all_good = False

if not all_good:
    print()
    print('Install missing packages with:')
    print('  ./myenv_new/bin/pip install PyPDF2 pdf2image Pillow')
    sys.exit(1)
" || exit 1

echo ""
echo "🖼️  Checking ImageMagick..."
if command -v convert &> /dev/null; then
    echo "✅ ImageMagick installed"
else
    echo "⚠️  ImageMagick not found (optional for image processing)"
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║  ✅ All checks passed!              ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "🚀 Starting application..."
echo ""

# Run the app
source ./myenv_new/bin/activate
python SPlitfile_fixed.py
