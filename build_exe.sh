#!/bin/bash
# Build Windows .exe files for PDF Splitter
# This script runs PyInstaller to create standalone executables

set -e  # Exit on error

WORKSPACE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$WORKSPACE"

echo ""
echo "════════════════════════════════════════════════════════"
echo "📦 PDF SPLITTER - WINDOWS EXE BUILDER"
echo "════════════════════════════════════════════════════════"
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python found: $(python --version)"

# Check PyInstaller
echo ""
echo "🔍 Checking PyInstaller..."
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "📥 Installing PyInstaller..."
    python -m pip install pyinstaller -q
    echo "✅ PyInstaller installed"
else
    echo "✅ PyInstaller already installed"
fi

# Create output directories
mkdir -p dist build build_specs
echo "✅ Output directories ready"

# Build configurations
echo ""
echo "════════════════════════════════════════════════════════"
echo "🏗️  BUILDING EXECUTABLES"
echo "════════════════════════════════════════════════════════"

# Build 1: Responsive Version
echo ""
echo "📌 Building: PDF Splitter Responsive (Modern UI)"
echo "─────────────────────────────────────────────────────────"
pyinstaller \
    --onefile \
    --windowed \
    --name PDFSplitter_Responsive \
    --distpath ./dist \
    --buildpath ./build \
    --specpath ./build_specs \
    SPlitfile_responsive.py

if [ -f "dist/PDFSplitter_Responsive.exe" ]; then
    SIZE=$(du -h "dist/PDFSplitter_Responsive.exe" | cut -f1)
    echo "✅ Success! File size: $SIZE"
else
    echo "❌ Build failed"
    exit 1
fi

# Build 2: Original Version
echo ""
echo "📌 Building: PDF Splitter Original (Stable Version)"
echo "─────────────────────────────────────────────────────────"
pyinstaller \
    --onefile \
    --windowed \
    --name PDFSplitter_Original \
    --distpath ./dist \
    --buildpath ./build \
    --specpath ./build_specs \
    SPlitfile_fixed.py

if [ -f "dist/PDFSplitter_Original.exe" ]; then
    SIZE=$(du -h "dist/PDFSplitter_Original.exe" | cut -f1)
    echo "✅ Success! File size: $SIZE"
else
    echo "❌ Build failed"
    exit 1
fi

# Summary
echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ BUILD COMPLETE!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📁 Executables created in: dist/"
ls -lh dist/*.exe
echo ""
echo "📌 Files ready:"
echo "   • dist/PDFSplitter_Responsive.exe  (Modern UI with Windows 11 styling)"
echo "   • dist/PDFSplitter_Original.exe    (Stable original version)"
echo ""
echo "🚀 Next Steps:"
echo "   1. Copy .exe files to Windows machine"
echo "   2. Double-click to run"
echo "   3. No installation needed!"
echo ""
echo "📊 Build artifacts (safe to delete):"
echo "   • build/          - Temporary files"
echo "   • build_specs/    - PyInstaller specs"
echo ""
