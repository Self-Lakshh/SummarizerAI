#!/bin/bash
# Run Backend Locally - Linux/Mac
# Make sure you have activated your virtual environment first

echo -e "\033[32mStarting SummarizerAI Backend...\033[0m"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "\033[33mWarning: Virtual environment not detected!\033[0m"
    echo -e "\033[33mActivate it with: source venv/bin/activate\033[0m"
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "\033[33mWarning: .env file not found!\033[0m"
    echo -e "\033[33mCreating from template...\033[0m"
    cp .env.example .env
    echo -e "\033[33mPlease edit .env with your configuration\033[0m"
    echo ""
fi

# Create necessary directories
echo -e "\033[36mCreating directories...\033[0m"
mkdir -p uploads faiss_indices logs

# Run the server
echo -e "\033[36mStarting FastAPI server...\033[0m"
echo ""
echo -e "\033[32mAPI Docs: http://localhost:8000/docs\033[0m"
echo -e "\033[32mHealth Check: http://localhost:8000/health\033[0m"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
