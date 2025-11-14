#!/usr/bin/env bash
set -euo pipefail

# Creates a virtual environment in .venv and installs requirements
if [ -d ".venv" ]; then
  echo ".venv already exists; activating and upgrading pip"
else
  echo "Creating virtual environment at .venv..."
  python3 -m venv .venv
fi

echo "Activating .venv and installing requirements..."
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Done. Virtual environment created at .venv and packages installed."
