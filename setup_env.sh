#!/bin/bash

ENV_NAME="can_env"

echo "--- 1. Installing Native MSYS2 Dependencies ---"
# This installs pandas/numpy outside the venv but makes them available
pacman -S --needed --noconfirm mingw-w64-x86_64-python-pandas mingw-w64-x86_64-python-numpy mingw-w64-x86_64-python-openpyxl

echo "--- 2. Creating Virtual Environment with System Access ---"
python3 -m venv --system-site-packages $ENV_NAME

echo "--- 3. Activating and Finishing Setup ---"
source $ENV_NAME/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install cantools pyinstaller

echo "--- 4. Verification ---"
python3 -c "import pandas as pd; import numpy as np; print(f'✅ Ready! Pandas version: {pd.__version__}')"

# Check if we are on Windows/Mingw or Linux/Mac
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Setup complete. To start working, type: source $ENV_NAME/Scripts/activate"
else
    echo "Setup complete. To start working, type: source $ENV_NAME/bin/activate"
fi
