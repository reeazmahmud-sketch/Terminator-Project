#!/bin/bash

# Block 1: Terminating AI processes
echo "Step 1: Terminating all AI processes..."
pkill -9 "Ollama" 2>/dev/null
pkill -9 "ollama" 2>/dev/null
sudo pkill -9 -x com.apple.SpeechRecognitionCore.brokerd 2>/dev/null

# Block 2: Clear Corrupt macOS Metadata
echo "Step 2: Removing corrupt .DS_Store files from models..."
find /Users/reeazmahmud/.ollama/models -name ".DS_Store" -type f -delete 2>/dev/null

# Block 3: Clear temporary state
echo "Step 3: Cleaning temporary lock files..."
rm -rf /Users/reeazmahmud/.ollama/models/blobs/*tmp* 2>/dev/null

# Block 4: System health check
echo "Step 4: Checking memory status..."
sysctl -n hw.memsize
echo "--- Cleanup Complete. Your system should be stable now. ---"
