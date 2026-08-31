#!/usr/bin/env bash
# ==============================================================================
# Robot Continuity Network (RCN) • Master Control & Demo Launcher
# Identity, memory and skills that can survive the robot body
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Color styles
CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

clear
echo -e "${BOLD}${CYAN}========================================================================${RESET}"
echo -e "${BOLD}${CYAN}   ROBOT CONTINUITY NETWORK (RCN) • MASTER DEMO LAUNCHER${RESET}"
echo -e "${DIM}   Specification RCN-01 (Passport) & RCN-02 (Memory Vault)${RESET}"
echo -e "${BOLD}${CYAN}========================================================================${RESET}"
echo ""
echo -e "${BOLD}Select an action:${RESET}"
echo -e "  ${BOLD}${GREEN}1)${RESET} Launch Interactive Web Demo (Browser + Voiceover + Live Subtitles)"
echo -e "  ${BOLD}${GREEN}2)${RESET} Play 1080p Full HD Presentation Video (QuickTime MP4 with Audio)"
echo -e "  ${BOLD}${GREEN}3)${RESET} Run Terminal CLI Simulation (Step-by-step cryptographic transfer)"
echo -e "  ${BOLD}${GREEN}4)${RESET} Re-render 1080p Video (Frame-by-frame broadcast generator)"
echo -e "  ${BOLD}${GREEN}5)${RESET} Run Automated Protocol Test Suite (Unit tests for schemas & seals)"
echo -e "  ${BOLD}${GREEN}6)${RESET} Open Project Folder in Finder"
echo -e "  ${BOLD}${GREEN}7)${RESET} Push Latest Changes to GitHub"
echo -e "  ${DIM}q) Quit${RESET}"
echo ""
read -p "Enter choice [1-7] (default: 1): " choice
choice=${choice:-1}

case "$choice" in
  1)
    echo ""
    echo -e "${CYAN}Starting local HTTP server on port 8080...${RESET}"
    if ! lsof -i :8080 >/dev/null 2>&1; then
      python3 -m http.server 8080 >/dev/null 2>&1 &
      SERVER_PID=$!
      sleep 1
    fi
    echo -e "${GREEN}Opening http://localhost:8080/demo/ in your browser...${RESET}"
    open "http://localhost:8080/demo/"
    echo ""
    echo -e "${BOLD}Web demo is live!${RESET}"
    echo -e "• Click ${BOLD}'Play with Voiceover (MP3)'${RESET} for the voice-synced walkthrough."
    echo -e "• Click ${BOLD}'Record Video'${RESET} to export a video straight from the browser."
    echo -e "Press ${YELLOW}Ctrl+C${RESET} in this terminal when finished."
    if [ ! -z "$SERVER_PID" ]; then
      wait $SERVER_PID
    fi
    ;;

  2)
    VIDEO_FILE="$DIR/Robot_Continuity_Protocol_Presentation_1080p.mp4"
    if [ -f "$VIDEO_FILE" ]; then
      echo ""
      echo -e "${GREEN}Opening 1080p Full HD Presentation Video...${RESET}"
      open "$VIDEO_FILE"
    else
      echo -e "${YELLOW}Video file not found. Running renderer now...${RESET}"
      python3 "$DIR/render_1080p_video.py"
      open "$VIDEO_FILE"
    fi
    ;;

  3)
    echo ""
    echo -e "${CYAN}Running Terminal CLI Simulation...${RESET}"
    python3 -m rcn.demo
    echo ""
    read -p "Press Enter to return to terminal..."
    ;;

  4)
    echo ""
    echo -e "${CYAN}Re-rendering 1080p Full HD Video via Python & FFmpeg...${RESET}"
    python3 "$DIR/render_1080p_video.py"
    echo -e "${GREEN}Render complete! Opening video...${RESET}"
    open "$DIR/Robot_Continuity_Protocol_Presentation_1080p.mp4"
    ;;

  5)
    echo ""
    echo -e "${CYAN}Running Automated Protocol Test Suite...${RESET}"
    python3 -m unittest discover tests -v
    echo ""
    read -p "Press Enter to return to terminal..."
    ;;

  6)
    echo ""
    echo -e "${GREEN}Opening project folder in Finder...${RESET}"
    open "$DIR"
    ;;

  7)
    echo ""
    echo -e "${CYAN}Syncing and pushing to GitHub...${RESET}"
    git add -A
    git -c user.name="Aztecbird" -c user.email="pablo@aztecbird.com" commit -m "update: sync latest demo scripts and assets" || true
    git push origin main
    echo -e "${GREEN}Successfully pushed to https://github.com/Aztecbird/robot-continuity-network${RESET}"
    echo ""
    read -p "Press Enter to return to terminal..."
    ;;

  q|Q)
    echo "Exiting."
    exit 0
    ;;

  *)
    echo "Invalid option."
    exit 1
    ;;
esac
