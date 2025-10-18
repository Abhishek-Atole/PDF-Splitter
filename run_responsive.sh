#!/bin/bash
# PDF Master Pro - Responsive Version Launcher

cd "$(dirname "$0")"

# Deactivate any active virtual environment
if [[ -n "$VIRTUAL_ENV" ]]; then
    deactivate 2>/dev/null || true
fi

# Activate the correct virtual environment
source "./myenv_new/bin/activate"

# Run the responsive version
python SPlitfile_responsive.py
