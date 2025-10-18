# 🖥️ Building Windows .EXE Files from PDF Splitter

## Quick Start

### Option 1: Automatic Build (Recommended)

Run the automated build script:

```bash
python build_exe.py
```

This will:
- ✅ Check PyInstaller installation
- ✅ Build both versions (Responsive & Original)
- ✅ Create single-file executables (.exe)
- ✅ Place them in `dist/` folder
- ✅ Show completion summary

### Option 2: Manual Build

#### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

#### Step 2: Build Responsive Version
```bash
pyinstaller --onefile --windowed --name PDFSplitter_Responsive SPlitfile_responsive.py
```

#### Step 3: Build Original Version
```bash
pyinstaller --onefile --windowed --name PDFSplitter_Original SPlitfile_fixed.py
```

#### Step 4: Find Your Executables
```bash
# On Linux:
ls -lh dist/PDFSplitter_*.exe

# On Windows:
dir dist\PDFSplitter_*.exe
```

---

## Understanding PyInstaller Options

| Option | Purpose |
|--------|---------|
| `--onefile` | Creates single .exe file (vs folder with many files) |
| `--windowed` | No console window appears (clean user experience) |
| `--name` | Custom name for the executable |
| `--distpath` | Where to save the finished .exe |
| `--buildpath` | Temporary build folder location |
| `--add-data` | Include data files with the executable |

---

## Complete Build Command Explanation

```bash
pyinstaller \
  --onefile \                          # Single file
  --windowed \                         # No console
  --name PDFSplitter_Responsive \      # Output filename
  --distpath ./dist \                  # Output folder
  --buildpath ./build \                # Temp build folder
  --specpath ./build_specs \           # Spec file location
  SPlitfile_responsive.py              # Input Python file
```

---

## What Gets Built

### Single-File Executable
```
dist/
  PDFSplitter_Responsive.exe    (~50-80 MB with all dependencies)
  PDFSplitter_Original.exe      (~50-80 MB with all dependencies)
```

**Features:**
- ✅ Completely self-contained
- ✅ No Python installation needed on target Windows machine
- ✅ No external files required
- ✅ Double-click to run
- ✅ Can be distributed as-is

### Build Artifacts (can be deleted)
```
build/                 # Temporary build files (safe to delete)
build_specs/           # PyInstaller spec files (safe to delete)
__pycache__/          # Python cache files (safe to delete)
```

---

## After Building: Next Steps

### 1. Test on Windows
```bash
# Copy dist/PDFSplitter_Responsive.exe to Windows
# Double-click to run

# Or from command prompt:
PDFSplitter_Responsive.exe
```

### 2. Create Shortcuts (Optional)
- Right-click PDFSplitter_Responsive.exe
- Select "Send to" → "Desktop (create shortcut)"
- Customize shortcut icon if desired

### 3. Create Installer (Optional with NSIS)
```bash
pip install pyinstaller-nsis
# Creates proper Windows installer (.msi or .exe installer)
```

### 4. Distribute
- Upload `dist/PDFSplitter_Responsive.exe` to cloud
- Share via email, GitHub releases, etc.
- Users just download and run

---

## Troubleshooting

### Issue: "PyInstaller not found"
```bash
pip install pyinstaller
```

### Issue: "Module not found" error
Ensure all dependencies are installed:
```bash
pip install PyPDF2 pdf2image Pillow customtkinter
```

### Issue: Large file size (50-80 MB)
This is normal! PyInstaller bundles:
- Python runtime
- All libraries (PyPDF2, Pillow, etc.)
- tkinter GUI framework

To reduce size:
```bash
# Use UPX compression (advanced)
pip install upx
pyinstaller --upx-dir=/path/to/upx --onefile SPlitfile_responsive.py
```

### Issue: Slow startup time (first run)
- First run unpacks and initializes (~2-3 seconds)
- Subsequent runs are faster
- Normal for PyInstaller executables

### Issue: Windows Defender Warning
- PyInstaller executables sometimes trigger false positives
- Solution: Submit executable to Microsoft for whitelist review
- Or: Code sign the .exe with a certificate

---

## Advanced: Custom Build Options

### With Console Window (for debugging)
```bash
pyinstaller --onefile --name PDFSplitter_Responsive SPlitfile_responsive.py
# Remove --windowed to see console output
```

### With Custom Icon
```bash
# First create or get an .ico file
# Then use:
pyinstaller --onefile --windowed --icon=app.ico --name PDFSplitter_Responsive SPlitfile_responsive.py
```

### Split Version (Separate Files)
```bash
# Creates folder with executable + dependencies
# More transparent but less portable
pyinstaller --name PDFSplitter_Responsive SPlitfile_responsive.py
# Result: dist/PDFSplitter_Responsive/ folder with multiple files
```

---

## File Size Breakdown

Typical executable composition:
- Python runtime: ~15 MB
- PyPDF2: ~5 MB
- Pillow: ~10 MB
- pdf2image: ~2 MB
- tkinter: ~3 MB
- Other libraries: ~5 MB
- **Total: ~40-50 MB (normal)**

---

## Deployment Recommendations

### For Internal Use
- Use `--onefile` for simplicity
- Place on network share
- Users run directly

### For Public Distribution
- Create Windows installer (.msi)
- Include readme and system requirements
- Code sign for trust
- Host on GitHub Releases

### For CI/CD Pipeline
- Automate PyInstaller builds on Windows runner
- Store in artifact repository
- Test on multiple Windows versions (7, 10, 11)

---

## System Requirements for Target Machine

After building .exe, users need:
- **OS:** Windows 7, 10, 11 (32-bit or 64-bit)
- **RAM:** Minimum 512 MB (2 GB recommended)
- **Storage:** ~100 MB free space
- **Dependencies:** Automatically included in .exe

**Optional (for enhanced features):**
- ImageMagick (for batch image processing)
- Ghostscript (for better PDF rendering)

---

## Building on Different Operating Systems

### Linux → Windows .exe
```bash
# Works fine (PyInstaller creates Windows compatible executables)
python build_exe.py
# Transfer dist/*.exe to Windows or use in CI/CD
```

### macOS → Windows .exe
```bash
# Same as Linux - works fine
# May need to install PyInstaller for macOS first
pip install pyinstaller
python build_exe.py
```

### Windows → Windows .exe (Best Performance)
```bash
# Native Windows build is slightly more reliable
# Run directly on Windows:
python build_exe.py
```

---

## Version Management

### Keep Track of Builds
```bash
# Rename builds with version numbers
mv dist/PDFSplitter_Responsive.exe dist/PDFSplitter_Responsive_v1.0.exe
mv dist/PDFSplitter_Responsive.exe dist/PDFSplitter_Responsive_v1.1.exe
```

### Automated Versioning
Create a build script that:
1. Reads version from file
2. Builds .exe
3. Tags with version number
4. Stores in version folder

---

## Next Steps

1. **Run the build:**
   ```bash
   python build_exe.py
   ```

2. **Wait for completion** (2-5 minutes depending on system)

3. **Check results:**
   ```bash
   ls -lh dist/
   ```

4. **Test the .exe** by downloading one and running on Windows

5. **Distribute** as needed

---

## Support & Issues

- **PyInstaller Docs:** https://pyinstaller.org
- **FAQ:** Check build output for specific errors
- **Custom Help:** Modify `build_exe.py` for your needs

