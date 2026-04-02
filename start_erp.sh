#!/bin/bash
echo "=========================================="
echo "Starting Spoorthy ERP with DeepSeek R1"
echo "=========================================="

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Check if DeepSeek model is loaded
if command -v ollama &> /dev/null; then
    if ! ollama list | grep -q "deepseek-r1"; then
        echo "Pulling DeepSeek R1 model (this may take a few minutes)..."
        ollama pull deepseek-r1:7b
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Start the server
echo ""
echo "🚀 Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🤖 DeepSeek AI: http://localhost:8000/api/v1/ai/analyze"
echo "🔐 Login: admin / admin123"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
