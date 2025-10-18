# PDF Master Pro - Setup & Usage Guide

## ✅ Environment Setup Complete!

A fresh Python virtual environment (`myenv_new`) has been created with all required dependencies installed.

## 📦 Installed Packages

- **PyPDF2** (3.0.1) - PDF manipulation
- **pdf2image** (1.17.0) - PDF to image conversion
- **Pillow** (11.3.0) - Image processing
- **customtkinter** (5.2.2) - Modern UI components
- **tkinter** - GUI framework (system package)

## 🔧 System Requirements

- **ImageMagick** (`convert`) - Already installed at `/usr/bin/convert` ✅
- **poppler-utils** - Required for PDF preview feature
  - Install with: `sudo apt install poppler-utils`

## 🚀 How to Run

### Option 1: Use the launcher script (easiest)
```bash
./run_app.sh
```

### Option 2: Direct Python command
```bash
"./myenv_new/bin/python" SPlitfile_fixed.py
```

### Option 3: Activate venv first
```bash
source myenv_new/bin/activate
python SPlitfile_fixed.py
deactivate  # when done
```

## 📝 Features

- **Split PDF**: Split PDFs by page ranges with rotation support
- **Merge PDFs**: Combine multiple PDFs with options to reverse order/pages and rotate
- **Image Processing**: Batch process images with ImageMagick (remove backgrounds, enhance)
- **PDF Preview**: Live preview of PDF pages (requires poppler-utils)
- **Modern UI**: Dark/light theme toggle

## 🐛 Troubleshooting

### If you see "No module named 'PyPDF2'"
Make sure you're using the correct Python interpreter:
```bash
"./myenv_new/bin/python" SPlitfile_fixed.py
```

### If PDF preview doesn't work
Install poppler-utils:
```bash
sudo apt install poppler-utils
```

### If image processing fails
Verify ImageMagick is installed:
```bash
convert --version
```

## 📂 Old Environment

The original `myenv` folder had corrupted symlinks and has been left intact. You can safely delete it if you want:
```bash
rm -rf myenv
```

## 🔄 Updating Packages

To update packages in the future:
```bash
source myenv_new/bin/activate
pip install --upgrade PyPDF2 pdf2image Pillow customtkinter
deactivate
```

---

**Created:** October 10, 2025  
**Python Version:** 3.12.3  
**Virtual Environment:** myenv_new
# PDF-Splitter
