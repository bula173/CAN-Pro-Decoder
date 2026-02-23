#!/bin/bash

# Define environment name
ENV_NAME="can_env"

echo "--- 1. Creating Virtual Environment: $ENV_NAME ---"
python3 -m venv $ENV_NAME

echo "--- 2. Activating Environment ---"
# Check if we are on Windows/Mingw or Linux/Mac
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source $ENV_NAME/Scripts/activate
else
    source $ENV_NAME/bin/activate
fi

echo "--- 3. Installing Dependencies ---"
python3 -m pip install --upgrade pip
python3 -m pip install cantools pyinstaller

echo "--- 4. Verification ---"
python3 -c "import cantools; print('✅ Success: Environment is ready!')"


# Check if we are on Windows/Mingw or Linux/Mac
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Setup complete. To start working, type: source $ENV_NAME/Scripts/activate"
else
    echo "Setup complete. To start working, type: source $ENV_NAME/bin/activate"
fi
