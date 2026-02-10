#!/bin/bash

# MedVault Application Startup Script

# Navigate to app directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the Flask application
python3 app.py
