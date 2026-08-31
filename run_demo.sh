#!/usr/bin/env bash
# ==============================================================================
# Robot Continuity Network (RCN) • Quick Launch Script
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "========================================================================"
echo "   ROBOT CONTINUITY NETWORK (RCN) • LAUNCHER"
echo "========================================================================"
echo ""
echo "Select how you want to run the 3-Minute Proof:"
echo "  1) Launch Interactive Visual Web Demo (Browser)"
echo "  2) Run Terminal CLI Simulation"
echo "  3) Run Automated Test Suite"
echo ""
read -p "Enter choice [1-3] (default: 1): " choice
choice=${choice:-1}

case "$choice" in
  1)
    echo "Starting local HTTP server on port 8080..."
    # Check if port 8080 is already serving
    if ! lsof -i :8080 >/dev/null 2>&1; then
      python3 -m http.server 8080 &
      SERVER_PID=$!
      sleep 1
    fi
    echo "Opening http://localhost:8080/demo/ in your browser..."
    open "http://localhost:8080/demo/"
    echo "Web demo is live! Press Ctrl+C in this terminal when finished."
    if [ ! -z "$SERVER_PID" ]; then
      wait $SERVER_PID
    fi
    ;;
  2)
    echo "Running Terminal CLI Simulation..."
    python3 -m rcn.demo
    ;;
  3)
    echo "Running Unit Tests..."
    python3 -m unittest discover tests -v
    ;;
  *)
    echo "Invalid option."
    exit 1
    ;;
esac
