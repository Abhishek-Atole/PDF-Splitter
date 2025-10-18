# 🖥️ WINDOWS .EXE BUILD - Complete Instructions

## ⚠️ Important Note

PyInstaller built on **Linux creates Linux executables**, not Windows .exe files.

To create **actual Windows .exe files**, you have several options:

---

## 🏆 Option 1: Build on Windows (Recommended - Best Results)

### Step 1: Transfer Files to Windows
1. Copy your entire project folder to Windows
2. Include all Python files

### Step 2: On Windows Command Prompt or PowerShell

```bash
# Navigate to your project
cd "Path\To\PDF Splitter"

# Install Python 3.12+ if not already installed
# Download from https://python.org/

# Create virtual environment
python -m venv myenv_windows

# Activate it
myenv_windows\Scripts\activate

# Install dependencies
pip install PyPDF2 pdf2image Pillow customtkinter pyinstaller

# Build Responsive Version
pyinstaller --onefile --windowed --name PDFSplitter_Responsive SPlitfile_responsive.py

# Build Original Version
pyinstaller --onefile --windowed --name PDFSplitter_Original SPlitfile_fixed.py

# Find your .exe files in: dist/
# - dist\PDFSplitter_Responsive.exe
# - dist\PDFSplitter_Original.exe
```

**Advantages:**
- ✅ Native Windows .exe files
- ✅ Best compatibility
- ✅ Windows-specific features work
- ✅ No compatibility issues

---

## 🐧 Option 2: Use GitHub Actions (Automated on Windows)

### Create Workflow File

Create `.github/workflows/build-windows-exe.yml`:

```yaml
name: Build Windows .exe

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install PyPDF2 pdf2image Pillow customtkinter pyinstaller
    
    - name: Build Responsive Version
      run: |
        pyinstaller --onefile --windowed --name PDFSplitter_Responsive SPlitfile_responsive.py
    
    - name: Build Original Version
      run: |
        pyinstaller --onefile --windowed --name PDFSplitter_Original SPlitfile_fixed.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: windows-executables
        path: dist/
        retention-days: 30
```

**How to use:**
1. Push this file to GitHub
2. Workflow runs automatically
3. Download .exe files from "Artifacts"
4. Files ready to distribute!

**Advantages:**
- ✅ Automated builds
- ✅ Free (GitHub provides Windows runners)
- ✅ Runs on actual Windows
- ✅ Perfect for CI/CD

---

## 💻 Option 3: Use Docker (Advanced)

For building Windows executables on Linux using Wine:

```dockerfile
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Install Python and dependencies
# Build executables
# Extract to volume
```

**⚠️ Complex - Not recommended unless you're already using Docker**

---

## 📦 Option 4: Pre-built Cross-Compiler

Use pre-compiled PyInstaller for Windows:

```bash
# On Linux, download Windows Python runtime
# Then use wine + PyInstaller
# Very complex and unreliable
```

**⚠️ Not recommended - Too complex**

---

## 🎯 QUICKEST SOLUTION

### **Best for You Right Now:**

1. **On Linux (current setup):**
   ```bash
   cd "/media/abhishek-atole/Data Folder/Developed Application/PDF Splitter"
   
   # Create Windows-ready folder
   mkdir -p Windows_Release
   cp SPlitfile_responsive.py Windows_Release/
   cp SPlitfile_fixed.py Windows_Release/
   cp requirements.txt Windows_Release/
   ```

2. **Copy `Windows_Release/` to Windows machine**

3. **On Windows, run:**
   ```cmd
   cd Windows_Release
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install pyinstaller
   pyinstaller --onefile --windowed --name PDFSplitter_Responsive SPlitfile_responsive.py
   pyinstaller --onefile --windowed --name PDFSplitter_Original SPlitfile_fixed.py
   
   # Find .exe files in dist/
   ```

---

## 📋 Requirements File for Windows

Let me create a requirements.txt file for easy installation on Windows:

```
PyPDF2==3.0.1
pdf2image==1.17.0
Pillow==11.3.0
customtkinter==5.2.2
pyinstaller==6.1.0
```

---

## What About the Linux Files?

The files built on Linux (`dist/PDFSplitter_Responsive` and `dist/PDFSplitter_Original`) are:

- ❌ **Cannot run on Windows** (Linux executables)
- ✅ **Can run on Linux** (for testing)
- ✅ **Can be used in Docker** (on Windows via WSL)

To test on Linux:
```bash
./dist/PDFSplitter_Responsive
./dist/PDFSplitter_Original
```

---

## 🚀 Summary - What to Do

### **For Windows Users:**

| Goal | Steps | Time |
|------|-------|------|
| Get Windows .exe | Move files to Windows PC → Run build script | 5 min |
| Automated builds | Set up GitHub Actions → Auto-build | 10 min |
| Use on Windows now | Use Linux version in WSL2 | N/A |

### **Recommended Path:**
1. ✅ Keep Linux version for Linux testing
2. ⏭️ Transfer project to Windows machine
3. ⏭️ Run PyInstaller on Windows
4. ⏭️ Get native Windows .exe files
5. ⏭️ Distribute to users

---

## Troubleshooting

### Q: Why not .exe on Linux?
**A:** PyInstaller matches the OS it runs on. Linux → Linux binaries, Windows → Windows binaries.

### Q: Can I convert the Linux binary to .exe?
**A:** No, they're completely different formats (ELF vs PE).

### Q: Will the code work on Windows without changes?
**A:** Yes! Python code is cross-platform. Only the executable format differs.

### Q: How large will the .exe be?
**A:** ~50-80 MB for each executable (includes Python + all libraries)

### Q: Do users need Python installed?
**A:** No! The .exe is self-contained. No Python needed on user's machine.

---

## Create requirements.txt

For easy installation on Windows, here's what to save:
```
PyPDF2==3.0.1
pdf2image==1.17.0
Pillow==11.3.0
customtkinter==5.2.2
pyinstaller==6.1.0
```

---

## Next Steps

### **Now:**
1. Keep the Linux files for testing on Linux
2. Transfer to Windows machine OR use GitHub Actions
3. Build Windows .exe files

### **File Transfer:**
- Upload to cloud (Google Drive, OneDrive, etc.)
- Email to yourself
- Use GitHub (if public is okay)
- USB drive

### **Or - Ask for Help:**
If you need me to help set up GitHub Actions, I can create the workflow file!

---

## Contact & Support

**Questions?** The best approach is:
1. **Best:** Transfer to Windows, build locally (30 seconds)
2. **Good:** Use GitHub Actions (automatic)
3. **Alternative:** Keep Linux version for testing

You're very close! Just need Windows for the final build step.

