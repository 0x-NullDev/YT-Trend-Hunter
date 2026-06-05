#!/usr/bin/env bash
set -e

# ============================================
#    YT Trend Hunter - AI Opportunity Platform
# ============================================

echo ""
echo "============================================"
echo "   YT Trend Hunter - Installation Script"
echo "============================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}[1/5]${NC} Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo -e "${RED}ERROR: Python not found. Please install Python 3.10+ from https://python.org${NC}"
    exit 1
fi
echo -e "  ${GREEN}[OK]${NC} Python found ($($PYTHON --version))"

# Check Node.js
if command -v node &> /dev/null; then
    echo -e "  ${GREEN}[OK]${NC} Node.js found ($(node --version))"
else
    echo -e "${RED}ERROR: Node.js not found. Please install Node.js 18+ from https://nodejs.org${NC}"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    echo -e "  ${GREEN}[OK]${NC} npm found ($(npm --version))"
else
    echo -e "${RED}ERROR: npm not found.${NC}"
    exit 1
fi

# Check Docker (optional)
if command -v docker &> /dev/null; then
    echo -e "  ${GREEN}[OK]${NC} Docker found (optional - for full stack)"
else
    echo -e "  ${YELLOW}[INFO]${NC} Docker not found - will use local setup"
fi

echo ""
echo -e "${CYAN}[2/5]${NC} Setting up Python virtual environment..."

cd "$(dirname "$0")"

if [ ! -d "backend/venv" ]; then
    $PYTHON -m venv backend/venv
    echo -e "  ${GREEN}[OK]${NC} Virtual environment created"
else
    echo -e "  ${YELLOW}[INFO]${NC} Virtual environment already exists"
fi

echo ""
echo -e "${CYAN}[3/5]${NC} Installing Python dependencies..."

source backend/venv/bin/activate
pip install -r backend/requirements.txt -q
echo -e "  ${GREEN}[OK]${NC} Python dependencies installed"

echo ""
echo -e "${CYAN}[4/5]${NC} Installing frontend dependencies..."

cd frontend
npm install --silent 2>/dev/null
cd ..
echo -e "  ${GREEN}[OK]${NC} Frontend dependencies installed"

echo ""
echo -e "${CYAN}[5/5]${NC} Setup complete!"
echo ""
echo "============================================"
echo "   How to Start"
echo "============================================"
echo ""
echo "  Option 1: Full Stack (Docker)"
echo "    docker-compose up -d"
echo ""
echo "  Option 2: Backend only"
echo "    cd backend"
echo "    source ../venv/bin/activate"
echo "    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "  Option 3: Frontend only"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "  Then open http://localhost:3000 in your browser"
echo ""
echo "============================================"
echo ""
echo "  Make sure to:"
echo "    1. Copy .env.example to .env"
echo "    2. Add your YOUTUBE_API_KEY in .env"
echo "    3. (Optional) Add AI provider keys"
echo ""
