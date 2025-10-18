#!/bin/bash
# PDF Master Pro Launcher
# This script activates the virtual environment and runs the application

cd "$(dirname "$0")"

# Deactivate any active virtual environment first
if [[ -n "$VIRTUAL_ENV" ]]; then
    deactivate 2>/dev/null || true
fi

# Activate the correct virtual environment
source "./myenv_new/bin/activate"

# Run the application
python SPlitfile_fixed.py
