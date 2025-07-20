#!/bin/bash
# Run Sage with 8q-is integration

echo "🌊 Starting M8-Enhanced Sage..."
echo "================================"
echo

# Check if 8q-is server is running
if ! curl -s http://localhost:8420 > /dev/null; then
    echo "⚠️  8q-is server not detected at http://localhost:8420"
    echo "Starting 8q-is server in background..."
    
    # Navigate to 8q-is directory and start server
    cd .. && cargo run &
    SERVER_PID=$!
    
    echo "Waiting for server to start..."
    sleep 5
    
    # Return to f8t directory
    cd f8t
else
    echo "✅ 8q-is server is running"
fi

echo
echo "🎪 Auctioneer live feed available at: http://localhost:8420/static/auctioneer.html"
echo

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the M8-enhanced sage
python sage_m8.py "$@"