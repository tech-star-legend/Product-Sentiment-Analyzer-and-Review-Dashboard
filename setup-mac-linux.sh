#!/usr/bin/env bash
set -e

echo "============================================================"
echo "  SentimentScope - Product Sentiment Analyzer Setup"
echo "============================================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 not found. Install from https://python.org"
    exit 1
fi

# Check Node
if ! command -v node &>/dev/null; then
    echo "[ERROR] Node.js not found. Install from https://nodejs.org"
    exit 1
fi

echo "[1/4] Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

echo "[2/4] Installing Python dependencies..."
pip install -r requirements.txt

echo "[3/4] Downloading TextBlob corpora..."
python -m textblob.download_corpora 2>/dev/null || true

echo "[4/4] Installing frontend dependencies..."
cd ../frontend
npm install

echo ""
echo "============================================================"
echo "  Setup complete!"
echo ""
echo "  NEXT STEPS:"
echo "  1. Configure your database:"
echo "     cp backend/.env.example backend/.env"
echo "     Edit backend/.env and set MONGO_URI"
echo "     (See DATABASE_SETUP.md for detailed instructions)"
echo ""
echo "  2. Start the app:"
echo "     ./run-mac-linux.sh"
echo "============================================================"
