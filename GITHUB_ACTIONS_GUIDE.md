# 🚀 GitHub Actions - Automatic Windows .exe Builder

## What is GitHub Actions?

GitHub Actions is a **free CI/CD platform** that automatically builds your project on Windows whenever you push code. It will:

1. ✅ Take your Python code
2. ✅ Install Python & all dependencies  
3. ✅ Run PyInstaller on Windows
4. ✅ Create .exe files
5. ✅ Store them for download

**Cost:** FREE! No credit card needed.

---

## 🎯 Quick Setup (5 Minutes)

### Step 1: Upload to GitHub

If your project isn't on GitHub yet:

```bash
# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: PDF Splitter"

# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/PDF-Splitter.git
git branch -M main
git push -u origin main
```

### Step 2: Enable GitHub Actions

1. Go to: `https://github.com/YOUR_USERNAME/PDF-Splitter`
2. Click **Actions** tab
3. Click **"I understand my workflows, go ahead and enable them"**

### Step 3: Trigger Build

**Option A: Automatic (Every Push)**
```bash
# Just push code
git push origin main
# Actions runs automatically!
```

**Option B: Manual (Click Button)**
1. Go to **Actions** tab
2. Click **"Build Windows .exe Files"**
3. Click **"Run workflow"** button
4. Done! Build starts automatically

---

## 📥 Download Your .exe Files

### After Build Completes:

1. **Go to Actions tab**
2. **Find latest run** (green ✅ = success)
3. **Scroll down to "Artifacts"**
4. **Download:**
   - `PDFSplitter_Responsive` (~50 MB)
   - `PDFSplitter_Original` (~50 MB)

**Time required:** ~3-5 minutes from push to download

---

## 🔍 What's Happening Behind the Scenes

### The Workflow File

File: `.github/workflows/build-windows.yml` (already created for you!)

```yaml
name: Build Windows .exe Files
on: [push, workflow_dispatch]  # Trigger on push or manual click

jobs:
  build-windows-exe:
    runs-on: windows-latest    # Runs on Windows Server 2022
    steps:
      - Check out code
      - Set up Python 3.12
      - Install dependencies (PyPDF2, Pillow, etc.)
      - Run PyInstaller for Responsive version
      - Run PyInstaller for Original version
      - Upload .exe files to Artifacts
```

**Result:** Two native Windows .exe files ready to use!

---

## 🎬 Live Example Workflow

### Scenario: You're updating the app

```bash
# Edit your Python code
nano SPlitfile_responsive.py

# Commit and push
git add SPlitfile_responsive.py
git commit -m "Fix: Better PDF preview"
git push origin main
```

**Automatically:**
1. GitHub detects push
2. Starts workflow on Windows runner
3. Builds executables
4. Stores in Artifacts
5. You get notified ✉️

**All in 5 minutes!**

---

## 📊 Build Status Indicators

| Status | Meaning |
|--------|---------|
| 🟢 ✅ Green | Build successful - download .exe files |
| 🟡 ⏳ Yellow | Build in progress (3-5 mins) |
| 🔴 ❌ Red | Build failed - check logs |

---

## 🔧 Advanced: Trigger Options

### Option 1: On Every Push (Default)
```yaml
on: [push]
# Builds automatically whenever you push code
```

### Option 2: Manual Trigger Only
```yaml
on: [workflow_dispatch]
# Only builds when you click "Run workflow"
```

### Option 3: On Specific File Changes
```yaml
on:
  push:
    paths:
      - 'SPlitfile_*.py'  # Only build if these files change
```

### Option 4: On Schedule
```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday at midnight
```

**Current setup:** Builds on any push + manual trigger ✅

---

## 📋 Artifacts Storage

### How It Works:

```
GitHub Actions Artifacts
├── PDFSplitter_Responsive.exe   (50 MB, 60-day retention)
└── PDFSplitter_Original.exe     (50 MB, 60-day retention)
```

### Download Multiple Builds:

1. **Go to Actions**
2. **See list of all past builds**
3. **Click any build → scroll to Artifacts**
4. **Download from any recent build**

**Storage:** All recent builds kept for 60 days

---

## 🐛 Debugging Failed Builds

### If Build Shows Red ❌:

1. **Click the failed build**
2. **Expand "Build [version] version" section**
3. **See exact error message**

Common issues:
- ❌ Missing dependency → add to pip install
- ❌ Python version issue → already using 3.12
- ❌ File not found → check filename spelling

---

## 🎁 Bonus: Create Releases

### Auto-publish on Git Tags:

```bash
# Tag a version
git tag v1.0.0
git push origin v1.0.0

# GitHub automatically:
# 1. Builds .exe files
# 2. Creates Release page
# 3. Attaches .exe files
# 4. Users can download from "Releases" tab
```

**Result:** Professional release management! 🎉

---

## 📱 Email Notifications

GitHub automatically notifies you:

```
✅ Workflow build-windows.yml completed successfully

Artifacts:
- PDFSplitter_Responsive
- PDFSplitter_Original

View: https://github.com/YOUR_USERNAME/PDF-Splitter/actions/runs/12345
```

---

## 🖥️ What's Installed on the Windows Runner

GitHub provides:
- ✅ Windows Server 2022 (latest)
- ✅ Python 3.12 (latest)
- ✅ Git, Node.js, .NET SDKs
- ✅ Visual C++ Build Tools
- ✅ All common development tools

**No additional setup needed!**

---

## 📊 Build Metrics

### Typical Build Times:

| Step | Time |
|------|------|
| Checkout code | ~5 sec |
| Setup Python | ~15 sec |
| Install dependencies | ~45 sec |
| Build Responsive .exe | ~60 sec |
| Build Original .exe | ~60 sec |
| Upload artifacts | ~30 sec |
| **Total** | **~3-4 mins** |

---

## 🔐 Security Notes

### What's Safe:

✅ Your code stored privately (if repo is private)
✅ Artifacts only accessible to you
✅ No external access to .exe files
✅ GitHub handles all security

### Recommendation:

Keep repo **PRIVATE** if sensitive code:
```
Settings → Private repository
```

---

## 🚀 Next Steps

### Immediate:
1. ✅ Already: Workflow file created (`.github/workflows/build-windows.yml`)
2. ⏭️ Upload to GitHub
3. ⏭️ Trigger build (manual or automatic)
4. ⏭️ Download .exe files
5. ⏭️ Test on Windows
6. ⏭️ Distribute to users

### Optional Enhancements:
- Create GitHub Release with version tags
- Setup automated version numbering
- Create installer (.msi file)
- Build for Python 3.11 + 3.12 versions

---

## 💡 Quick Reference

| Need | How To |
|------|--------|
| Trigger build | Push code or click "Run workflow" |
| Download .exe | Actions → Latest run → Artifacts |
| Check status | Actions tab, see 🟢 or 🔴 |
| See build logs | Click run → Expand step logs |
| Schedule builds | Modify `on:` in workflow file |
| Auto-release | Tag with `git tag v1.0.0` |

---

## 🎓 Learn More

- **GitHub Actions Docs:** https://docs.github.com/actions
- **PyInstaller Docs:** https://pyinstaller.org
- **Python Guide:** https://python.org

---

## 📞 Support

If build fails:
1. Check the error message in logs
2. Verify all Python files are in repo
3. Ensure dependencies are correct
4. Re-run workflow

**Still stuck?** Modify `.github/workflows/build-windows.yml` for your specific needs!

---

## 🎉 Summary

You now have:

✅ Automated Windows .exe building  
✅ Free CI/CD on GitHub  
✅ Professional release management  
✅ One-click .exe generation  
✅ Zero local configuration needed  

**Just push code → Get .exe files!** 🚀

