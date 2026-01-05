#!/usr/bin/env zsh
# ============================================================================
# 35-kill-all-processes.zsh
# Comprehensive kill commands for all AI, LLM, and agent processes
# ============================================================================

# Colors for output
typeset -g KC_RESET="\033[0m"
typeset -g KC_RED="\033[31m"
typeset -g KC_GREEN="\033[32m"
typeset -g KC_YELLOW="\033[33m"
typeset -g KC_BOLD="\033[1m"

# Kill ollama processes
function kill-ollama() {
    echo -e "${KC_BOLD}🔫 Killing Ollama processes...${KC_RESET}"
    
    local pids=$(pgrep -f "ollama")
    if [[ -n "$pids" ]]; then
        echo "$pids" | while read pid; do
            echo -e "  ${KC_YELLOW}Killing PID $pid${KC_RESET}"
            kill -9 "$pid" 2>/dev/null
        done
        echo -e "${KC_GREEN}✓ Ollama processes killed${KC_RESET}"
    else
        echo -e "${KC_YELLOW}○ No Ollama processes found${KC_RESET}"
    fi
}

# Kill Python AI agents
function kill-python-agents() {
    echo -e "${KC_BOLD}🔫 Killing Python AI agents...${KC_RESET}"
    
    # Kill specific AI scripts
    local patterns=(
        "ollama_cli.py"
        "gui_mcp.py"
        "alaina"
        "mcp_server"
        "agent"
    )
    
    local killed=0
    for pattern in "${patterns[@]}"; do
        local pids=$(pgrep -f "$pattern")
        if [[ -n "$pids" ]]; then
            echo "$pids" | while read pid; do
                local cmd=$(ps -p "$pid" -o command= 2>/dev/null)
                echo -e "  ${KC_YELLOW}Killing: $cmd${KC_RESET}"
                kill -9 "$pid" 2>/dev/null
                ((killed++))
            done
        fi
    done
    
    if [[ $killed -gt 0 ]]; then
        echo -e "${KC_GREEN}✓ Killed $killed Python AI agent(s)${KC_RESET}"
    else
        echo -e "${KC_YELLOW}○ No Python AI agents found${KC_RESET}"
    fi
}

# Kill MCP servers
function kill-mcp() {
    echo -e "${KC_BOLD}🔫 Killing MCP servers...${KC_RESET}"
    
    local pids=$(pgrep -f "mcp|model-context-protocol")
    if [[ -n "$pids" ]]; then
        echo "$pids" | while read pid; do
            local cmd=$(ps -p "$pid" -o command= 2>/dev/null)
            echo -e "  ${KC_YELLOW}Killing: $cmd${KC_RESET}"
            kill -9 "$pid" 2>/dev/null
        done
        echo -e "${KC_GREEN}✓ MCP servers killed${KC_RESET}"
    else
        echo -e "${KC_YELLOW}○ No MCP servers found${KC_RESET}"
    fi
}

# Kill local LLM servers (LM Studio, LocalAI, etc.)
function kill-llm-servers() {
    echo -e "${KC_BOLD}🔫 Killing LLM servers...${KC_RESET}"
    
    local patterns=(
        "lmstudio"
        "localai"
        "llama.cpp"
        "llama-server"
        "oobabooga"
        "text-generation-webui"
    )
    
    local killed=0
    for pattern in "${patterns[@]}"; do
        local pids=$(pgrep -fi "$pattern")
        if [[ -n "$pids" ]]; then
            echo "$pids" | while read pid; do
                local cmd=$(ps -p "$pid" -o command= 2>/dev/null)
                echo -e "  ${KC_YELLOW}Killing: $cmd${KC_RESET}"
                kill -9 "$pid" 2>/dev/null
                ((killed++))
            done
        fi
    done
    
    if [[ $killed -gt 0 ]]; then
        echo -e "${KC_GREEN}✓ Killed $killed LLM server(s)${KC_RESET}"
    else
        echo -e "${KC_YELLOW}○ No LLM servers found${KC_RESET}"
    fi
}

# Kill voice processes
function kill-voice() {
    echo -e "${KC_BOLD}🔫 Killing voice processes...${KC_RESET}"
    
    local pids=$(pgrep -f "speech_recognition|gtts|voice|pyttsx")
    if [[ -n "$pids" ]]; then
        echo "$pids" | while read pid; do
            echo -e "  ${KC_YELLOW}Killing PID $pid${KC_RESET}"
            kill -9 "$pid" 2>/dev/null
        done
        echo -e "${KC_GREEN}✓ Voice processes killed${KC_RESET}"
    else
        echo -e "${KC_YELLOW}○ No voice processes found${KC_RESET}"
    fi
}

# Kill Node.js AI agents
function kill-node-agents() {
    echo -e "${KC_BOLD}🔫 Killing Node.js AI agents...${KC_RESET}"
    
    local patterns=(
        "langchain"
        "openai"
        "anthropic"
        "agent"
    )
    
    local killed=0
    for pattern in "${patterns[@]}"; do
        local pids=$(pgrep -f "node.*$pattern")
        if [[ -n "$pids" ]]; then
            echo "$pids" | while read pid; do
                local cmd=$(ps -p "$pid" -o command= 2>/dev/null)
                echo -e "  ${KC_YELLOW}Killing: $cmd${KC_RESET}"
                kill -9 "$pid" 2>/dev/null
                ((killed++))
            done
        fi
    done
    
    if [[ $killed -gt 0 ]]; then
        echo -e "${KC_GREEN}✓ Killed $killed Node.js agent(s)${KC_RESET}"
    else
        echo -e "${KC_YELLOW}○ No Node.js agents found${KC_RESET}"
    fi
}

# Kill GPU processes (if running AI on GPU)
function kill-gpu-processes() {
    echo -e "${KC_BOLD}🔫 Killing GPU AI processes...${KC_RESET}"
    
    # Check for nvidia-smi (NVIDIA GPUs)
    if command -v nvidia-smi &> /dev/null; then
        local gpu_pids=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null)
        if [[ -n "$gpu_pids" ]]; then
            echo "$gpu_pids" | while read pid; do
                local cmd=$(ps -p "$pid" -o command= 2>/dev/null)
                echo -e "  ${KC_YELLOW}Killing GPU process: $cmd${KC_RESET}"
                kill -9 "$pid" 2>/dev/null
            done
            echo -e "${KC_GREEN}✓ GPU processes killed${KC_RESET}"
        else
            echo -e "${KC_YELLOW}○ No GPU processes found${KC_RESET}"
        fi
    fi
}

# Kill ALL AI/LLM/Agent processes
function kill-all-ai() {
    echo -e "${KC_BOLD}${KC_RED}╔═══════════════════════════════════════════════════════╗${KC_RESET}"
    echo -e "${KC_BOLD}${KC_RED}║  🛑 KILLING ALL AI/LLM/AGENT PROCESSES               ║${KC_RESET}"
    echo -e "${KC_BOLD}${KC_RED}╚═══════════════════════════════════════════════════════╝${KC_RESET}"
    echo ""
    
    # Confirmation
    echo -e "${KC_YELLOW}⚠️  This will terminate ALL AI-related processes.${KC_RESET}"
    echo -n "Are you sure? (y/N): "
    read -r confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo -e "${KC_YELLOW}Cancelled.${KC_RESET}"
        return 0
    fi
    
    echo ""
    
    # Kill everything
    kill-ollama
    kill-python-agents
    kill-mcp
    kill-llm-servers
    kill-voice
    kill-node-agents
    kill-gpu-processes
    
    echo ""
    echo -e "${KC_BOLD}${KC_GREEN}✅ All AI/LLM/Agent processes terminated${KC_RESET}"
    echo ""
    
    # Show remaining processes
    local remaining=$(pgrep -f "ollama|llama|mcp|agent|openai|anthropic" | wc -l | tr -d ' ')
    if [[ $remaining -gt 0 ]]; then
        echo -e "${KC_YELLOW}⚠️  Warning: $remaining related processes still running${KC_RESET}"
        echo -e "   Run 'ps aux | grep -E \"ollama|llama|mcp|agent\"' to check"
    fi
}

# Force kill all (no confirmation)
function kill-all-ai-force() {
    echo -e "${KC_BOLD}${KC_RED}🛑 FORCE KILLING ALL AI PROCESSES (no confirmation)${KC_RESET}"
    echo ""
    
    kill-ollama
    kill-python-agents
    kill-mcp
    kill-llm-servers
    kill-voice
    kill-node-agents
    kill-gpu-processes
    
    echo ""
    echo -e "${KC_BOLD}${KC_GREEN}✅ Force kill complete${KC_RESET}"
}

# List all AI/LLM processes
function list-ai-processes() {
    echo -e "${KC_BOLD}🔍 AI/LLM Processes:${KC_RESET}"
    echo ""
    
    local patterns=(
        "ollama"
        "llama"
        "mcp"
        "ollama_cli.py"
        "gui_mcp.py"
        "alaina"
        "lmstudio"
        "localai"
    )
    
    local found=false
    for pattern in "${patterns[@]}"; do
        local result=$(ps aux | grep -i "$pattern" | grep -v grep)
        if [[ -n "$result" ]]; then
            found=true
            echo -e "${KC_YELLOW}▸ $pattern:${KC_RESET}"
            echo "$result" | awk '{print "  PID " $2 ": " $11 " " $12 " " $13}'
            echo ""
        fi
    done
    
    if [[ "$found" == "false" ]]; then
        echo -e "${KC_GREEN}○ No AI/LLM processes running${KC_RESET}"
    fi
}

# Emergency kill - kills everything immediately
function emergency-kill() {
    echo -e "${KC_BOLD}${KC_RED}🚨 EMERGENCY KILL - TERMINATING EVERYTHING NOW${KC_RESET}"
    
    pkill -9 -f "ollama" 2>/dev/null
    pkill -9 -f "llama" 2>/dev/null
    pkill -9 -f "mcp" 2>/dev/null
    pkill -9 -f "ollama_cli" 2>/dev/null
    pkill -9 -f "gui_mcp" 2>/dev/null
    pkill -9 -f "alaina" 2>/dev/null
    pkill -9 -f "agent" 2>/dev/null
    
    echo -e "${KC_GREEN}✓ Emergency kill executed${KC_RESET}"
}

# Aliases
alias ka='kill-all-ai'
alias kaf='kill-all-ai-force'
alias ko='kill-ollama'
alias kp='kill-python-agents'
alias km='kill-mcp'
alias kl='kill-llm-servers'
alias kv='kill-voice'
alias ls-ai='list-ai-processes'
alias ekill='emergency-kill'

# Help function
function kill-help() {
    echo -e "${KC_BOLD}🔫 Kill Commands Help:${KC_RESET}"
    echo ""
    echo -e "${KC_YELLOW}Individual Kill Commands:${KC_RESET}"
    echo "  kill-ollama          - Kill Ollama processes"
    echo "  kill-python-agents   - Kill Python AI agents"
    echo "  kill-mcp             - Kill MCP servers"
    echo "  kill-llm-servers     - Kill LLM servers"
    echo "  kill-voice           - Kill voice processes"
    echo "  kill-node-agents     - Kill Node.js agents"
    echo ""
    echo -e "${KC_YELLOW}Bulk Kill Commands:${KC_RESET}"
    echo "  kill-all-ai          - Kill all AI processes (with confirmation)"
    echo "  kill-all-ai-force    - Kill all AI processes (no confirmation)"
    echo "  emergency-kill       - Emergency kill everything NOW"
    echo ""
    echo -e "${KC_YELLOW}Utility Commands:${KC_RESET}"
    echo "  list-ai-processes    - List all running AI processes"
    echo "  kill-help            - Show this help"
    echo ""
    echo -e "${KC_YELLOW}Aliases:${KC_RESET}"
    echo "  ka      → kill-all-ai"
    echo "  kaf     → kill-all-ai-force"
    echo "  ko      → kill-ollama"
    echo "  kp      → kill-python-agents"
    echo "  km      → kill-mcp"
    echo "  kl      → kill-llm-servers"
    echo "  kv      → kill-voice"
    echo "  ls-ai   → list-ai-processes"
    echo "  ekill   → emergency-kill"
}

echo "✅ Kill all processes module loaded (type 'kill-help' for commands)"
