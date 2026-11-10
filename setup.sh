#!/usr/bin/env bash
set -e

echo "Setting up Python Virtual Environment for TradingAgents..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

source "${VENV_DIR}/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -e "$SCRIPT_DIR"

echo ""
echo "Setup complete!"
echo "To configure your API keys, copy .env.example to .env and set your GOOGLE_API_KEY."
