#!/usr/bin/env python3
"""
PyInstaller Build Script for PDF Splitter Application
This script creates Windows .exe files from the Python application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Error: {description} failed")
        return False
    print(f"✅ Success: {description} completed")
    return True

def main():
    """Main build process"""
    print("\n" + "="*60)
    print("📦 PDF SPLITTER - WINDOWS EXE BUILDER")
    print("="*60)
    
    workspace = Path(__file__).parent
    os.chdir(workspace)
    
    # Check if PyInstaller is installed
    print("\n📋 Checking PyInstaller installation...")
    try:
        import PyInstaller
        print(f"✅ PyInstaller found (version: {PyInstaller.__version__})")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Build configurations
    configs = [
        {
            "name": "PDF Splitter Responsive",
            "file": "SPlitfile_responsive.py",
            "output": "PDFSplitter_Responsive",
            "icon": None,
        },
        {
            "name": "PDF Splitter Original",
            "file": "SPlitfile_fixed.py",
            "output": "PDFSplitter_Original",
            "icon": None,
        }
    ]
    
    failed = []
    
    for config in configs:
        print(f"\n{'='*60}")
        print(f"🏗️  Building: {config['name']}")
        print(f"{'='*60}")
        
        # Build command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",  # Single executable
            "--windowed",  # No console window
            "--name", config["output"],
            "--distpath", str(workspace / "dist"),
            "--buildpath", str(workspace / "build"),
            "--specpath", str(workspace / "build_specs"),
            "--add-data", ".:.",
            config["file"]
        ]
        
        # Add icon if available
        if config["icon"] and Path(config["icon"]).exists():
            cmd.extend(["--icon", config["icon"]])
        
        # Run PyInstaller
        print(f"\n📋 Command: {' '.join(cmd[:8])}...")
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            failed.append(config["name"])
            print(f"❌ Build failed: {config['name']}")
        else:
            exe_path = workspace / "dist" / f"{config['output']}.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024*1024)
                print(f"✅ Build successful: {config['name']}")
                print(f"   📁 Location: {exe_path}")
                print(f"   📊 Size: {size_mb:.1f} MB")
            else:
                print(f"❌ Executable not found at {exe_path}")
                failed.append(config["name"])
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 BUILD SUMMARY")
    print(f"{'='*60}")
    
    if failed:
        print(f"❌ {len(failed)} build(s) failed:")
        for name in failed:
            print(f"   • {name}")
        print(f"\n⚠️  Please review the errors above")
        return False
    else:
        print("✅ All builds completed successfully!")
        print(f"\n📁 Executables location: {workspace / 'dist'}")
        print("\n📌 Next steps:")
        print("   1. Test the .exe files on Windows")
        print("   2. Copy to Windows machine if needed")
        print("   3. Run directly: PDFSplitter_Responsive.exe or PDFSplitter_Original.exe")
        print("\n💡 Note: Ensure all dependencies are installed:")
        print("   • PyPDF2")
        print("   • pdf2image")
        print("   • Pillow")
        print("   • customtkinter (optional)")
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
