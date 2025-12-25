#!/bin/bash

echo ""
echo "================================================================================"
echo " Neonatal Screening Report Analyzer"
echo " Vijayrekha Life Sciences"
echo "================================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/3] Checking Python installation... OK"
echo ""

# Check if Streamlit is installed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "[2/3] Streamlit not found. Installing dependencies..."
    echo "This may take a few minutes on first run..."
    echo ""
    python3 -m pip install --upgrade pip --quiet
    python3 -m pip install -r requirements.txt --quiet
    echo "Dependencies installed successfully!"
    echo ""
else
    echo "[2/3] Dependencies already installed... OK"
    echo ""
fi

echo "[3/3] Starting application..."
echo "Browser will open automatically in 3 seconds..."
echo ""
echo "Press Ctrl+C to stop the application"
echo "================================================================================"
echo ""

# Wait 3 seconds
sleep 3

# Open browser (works on Mac and Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8501
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8501 2>/dev/null || echo "Please open http://localhost:8501 in your browser"
fi

# Start Streamlit
python3 -m streamlit run app.py

# If the app crashes, pause
if [ $? -ne 0 ]; then
    echo ""
    echo "================================================================================"
    echo "Application stopped with an error."
    echo "================================================================================"
    read -p "Press Enter to exit..."
fi
