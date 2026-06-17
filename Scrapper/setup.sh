#!/bin/bash
# setup.sh - One-command setup script (optional)
# Run from Scrapper with: bash setup.sh

set -e

cd "$(dirname "$0")"

echo "🚀 Job Offers Scraper - Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python version
echo "✓ Checking Python version..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "✓ Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install -q -r ../requirements.txt

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "✓ Creating .env from template..."
    cp .env.example .env
else
    echo "✓ .env already exists"
fi

# Initialize database
echo "✓ Initializing database..."
python -c "from app.database import init_db; init_db(); print('✓ Database initialized')"

# Run tests
echo ""
echo "✓ Running tests..."
pytest -q

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate venv: source .venv/bin/activate"
echo "  2. Start API:     uvicorn app.main:app --reload"
echo "  3. View docs:     http://localhost:8000/docs"
echo "  4. Run CLI:       python scripts/run_scraper.py --help"
echo ""
echo "See README.md or QUICKSTART.md for more info."
