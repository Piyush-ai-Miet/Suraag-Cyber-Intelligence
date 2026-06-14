#!/bin/bash

# Kill any existing streamlit processes
pkill -f "streamlit run app.py" 2>/dev/null || true

# Wait a moment for processes to die
sleep 1

# Start streamlit in background
cd "$(dirname "$0")"
nohup python -m streamlit run app.py --server.port 8509 --server.headless true > streamlit.log 2>&1 &

# Wait for server to start
sleep 5

# Check if running
if curl -s http://localhost:8509 > /dev/null; then
    echo "✅ IPDR Graph Engine started successfully!"
    echo ""
    echo "🌐 Access your app at:"
    echo "   Local:    http://localhost:8509"
    echo "   Network:  http://$(ipconfig getifaddr en0 2>/dev/null || echo "YOUR_IP"):8509"
    echo ""
    echo "📊 Modern neon theme with glassmorphism enabled"
    echo "🚀 Watchdog installed for better performance"
    echo ""
    echo "To stop: pkill -f 'streamlit run app.py'"
else
    echo "❌ Failed to start. Check streamlit.log for errors"
fi
