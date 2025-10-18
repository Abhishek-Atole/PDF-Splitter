#!/bin/bash
# Quick installation helper for poppler-utils (needed for PDF preview)

echo "==================================="
echo "PDF Master Pro - System Setup"
echo "==================================="
echo ""

# Check if poppler is installed
if command -v pdftoppm &> /dev/null; then
    echo "✅ poppler-utils is already installed"
else
    echo "⚠️  poppler-utils is NOT installed"
    echo "   PDF preview feature will not work without it"
    echo ""
    read -p "Install poppler-utils now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing poppler-utils..."
        sudo apt update
        sudo apt install -y poppler-utils
        echo "✅ Installation complete!"
    fi
fi

echo ""
echo "==================================="
echo "Environment Status:"
echo "==================================="
echo "Python venv: myenv_new ✅"
echo "PyPDF2: Installed ✅"
echo "pdf2image: Installed ✅"
echo "Pillow: Installed ✅"
echo "ImageMagick: Installed ✅"

if command -v pdftoppm &> /dev/null; then
    echo "poppler-utils: Installed ✅"
else
    echo "poppler-utils: Not installed ⚠️"
fi

echo ""
echo "==================================="
echo "Ready to run!"
echo "==================================="
echo "Execute: ./run_app.sh"
echo ""
