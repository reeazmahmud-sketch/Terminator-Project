#!/bin/bash

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

# Universal Terminator Launcher
# Detects OS and launches the appropriate subsystem

echo "🤖 TERMINATOR UNIVERSAL FRAMEWORK"
echo "================================"

# 1. Setup Environment
if [ ! -d "venv" ]; then
    echo "Creating Python Virtual Environment..."
    python3 -m venv venv
fi
source venv/bin/activate

# 2. Install Dependencies
echo "Checking dependencies..."
pip install -r config/requirements.txt -q

# 3. Detect Platform
OS="$(uname -s)"
case "${OS}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGW;;
    *)          machine="UNKNOWN:${OS}"
esac

echo "Detected Platform: ${machine}"

# 4. Launch Core
echo "🚀 Launching Terminator Core..."
python3 terminator.py
