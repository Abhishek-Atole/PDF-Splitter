# 🚀 PDF Master Pro - Quick Start Guide

## ⚠️ Important: Use the Correct Environment

You have multiple Python virtual environments on this system:
- ❌ `/media/abhishek-atole/Data Folder/Projects/InfizentTech/backend/venv` (different project)
- ✅ `/media/abhishek-atole/Data Folder/Developed Application/PDF Splitter/myenv_new` (correct one for this app)

## ✅ How to Run

### Option 1: Use the launcher (easiest & recommended)
```bash
cd "/media/abhishek-atole/Data Folder/Developed Application/PDF Splitter"
./run_app.sh
```

### Option 2: Manual activation
```bash
cd "/media/abhishek-atole/Data Folder/Developed Application/PDF Splitter"
source myenv_new/bin/activate
python SPlitfile_fixed.py
```

### Option 3: Direct Python (no activation needed)
```bash
cd "/media/abhishek-atole/Data Folder/Developed Application/PDF Splitter"
./myenv_new/bin/python SPlitfile_fixed.py
```

## 🐛 If You Get "ModuleNotFoundError: No module named 'PyPDF2'"

**Root Cause:** You're using the wrong Python environment.

**Fix:** First, deactivate any active environment:
```bash
deactivate  # if you're in another venv
```

Then use one of the methods above to activate the correct `myenv_new`.

## 📦 Installed Packages (myenv_new)
- PyPDF2 (3.0.1)
- pdf2image (1.17.0)
- Pillow (11.3.0)
- customtkinter (5.2.2)
- tkinter (system)

## ✨ Features
- Split PDFs by page ranges
- Merge multiple PDFs
- Batch image processing
- Live PDF preview
- Dark/light theme

## 📂 Project Structure
```
PDF Splitter/
├── myenv_new/              ✅ Correct virtual environment
├── myenv/                  ❌ Old broken venv (can delete)
├── .venv/                  ❌ Alternative venv (not configured)
├── SPlitfile_fixed.py      ✅ Main application
├── run_app.sh              ✅ Launcher script
└── requirements.txt        📋 Packages list
```

---
**Last Updated:** October 19, 2025
