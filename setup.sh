#!/bin/bash

# Speech Emotion Recognition System - Linux/macOS Setup Script
# This script sets up the entire project for Linux and macOS

set -e

echo ""
echo "========================================"
echo "Speech Emotion Recognition System Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.13 from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "[OK] Python $PYTHON_VERSION is installed"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[WARNING] Node.js is not installed"
    echo "Frontend setup will be skipped"
    SKIP_FRONTEND=true
else
    NODE_VERSION=$(node --version)
    echo "[OK] Node.js $NODE_VERSION is installed"
fi

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "[WARNING] FFmpeg is not installed"
    echo "Installing FFmpeg is recommended for audio processing"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "On Ubuntu/Debian, run: sudo apt-get install ffmpeg"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "On macOS with Homebrew, run: brew install ffmpeg"
    fi
fi

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt

echo "[OK] Python dependencies installed"

# Install frontend dependencies
if [ "$SKIP_FRONTEND" != true ]; then
    echo ""
    echo "Installing Node.js dependencies for frontend..."
    cd ../frontend
    npm install
    echo "[OK] Frontend dependencies installed"
    cd ../backend
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p models
mkdir -p logs
echo "[OK] Directories created"

# Create .env file
echo ""
echo "Creating .env configuration file..."
cat > .env << EOF
FLASK_ENV=development
FLASK_DEBUG=True
MODEL_PATH=models/best_emotion_model.h5
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
EOF
echo "[OK] .env file created"

# Make setup script executable
chmod +x ../setup.sh

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo ""
echo "1. Open a terminal and navigate to this directory"
echo "2. Activate virtual environment:"
echo "   source backend/venv/bin/activate"
echo ""
echo "3. Start the Flask backend:"
echo "   python app.py"
echo "   (Server will run at http://localhost:5000)"
echo ""
if [ "$SKIP_FRONTEND" != true ]; then
    echo "4. Open another terminal in the frontend folder and run:"
    echo "   npm start"
    echo "   (Frontend will open at http://localhost:3000)"
    echo ""
fi
echo "For more information, see README.md"
echo ""
