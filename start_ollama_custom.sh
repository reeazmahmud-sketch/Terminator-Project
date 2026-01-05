#!/bin/bash
# Ollama Launch Script with Custom Models Directory
# Created: 2025-12-30
# Purpose: Start Ollama server with custom models path

export OLLAMA_MODELS="/Users/reeazmahmud/Desktop/Ollama Models"

echo "🚀 Starting Ollama with custom models directory..."
echo "📁 Models location: $OLLAMA_MODELS"

# Start Ollama server
/Applications/Ollama.app/Contents/Resources/ollama serve

# Note: This will run in foreground. To run in background, use:
# nohup /Applications/Ollama.app/Contents/Resources/ollama serve > /tmp/ollama.log 2>&1 &
