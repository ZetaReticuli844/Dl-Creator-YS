#!/bin/bash

# Exit on any error
set -e

echo "🚗 Starting Driving License Management Chatbot..."

# Function to handle graceful shutdown
cleanup() {
    echo "🛑 Shutting down gracefully..."
    kill $RASA_PID $ACTION_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Check if model exists, if not train it
if [ ! -f "/app/models/latest.tar.gz" ]; then
    echo "🤖 Training new model..."
    rasa train
fi

# Start action server in background
echo "🔧 Starting action server..."
rasa run actions --port 5055 --cors "*" &
ACTION_PID=$!

# Wait a moment for action server to start
sleep 5

# Start Rasa server
echo "🤖 Starting Rasa server..."
rasa run --port 5005 --cors "*" --enable-api &
RASA_PID=$!

# Wait for both processes
wait $RASA_PID $ACTION_PID
