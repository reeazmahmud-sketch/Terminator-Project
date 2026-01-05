#!/usr/bin/env zsh
# ============================================================================
# 25-enhanced-dashboard.zsh
# Enhanced dashboard with file change tracking and auto-display
# ============================================================================

# Dashboard configuration
typeset -g DASHBOARD_ENABLED=true
typeset -g DASHBOARD_AUTO_SHOW=true
typeset -g DASHBOARD_WATCH_FILES=(
    "${HOME}/.zshrc"
    "${HOME}/.zsh"
    "${HOME}/.zprofile"
    "${HOME}/.zshenv"
)
typeset -g DASHBOARD_CHANGES_LOG="${HOME}/.zsh_dashboard_changes.log"
typeset -g DASHBOARD_LAST_CHECK="${HOME}/.zsh_dashboard_lastcheck"

# Colors
typeset -g C_RESET="\033[0m"
typeset -g C_BOLD="\033[1m"
typeset -g C_RED="\033[31m"
typeset -g C_GREEN="\033[32m"
typeset -g C_YELLOW="\033[33m"
typeset -g C_BLUE="\033[34m"
typeset -g C_MAGENTA="\033[35m"
typeset -g C_CYAN="\033[36m"
typeset -g C_WHITE="\033[37m"

# Initialize dashboard
function _init_dashboard() {
    # Create changes log if it doesn't exist
    if [[ ! -f "$DASHBOARD_CHANGES_LOG" ]]; then
        touch "$DASHBOARD_CHANGES_LOG"
    fi
    
    # Create last check timestamp
    if [[ ! -f "$DASHBOARD_LAST_CHECK" ]]; then
        date +%s > "$DASHBOARD_LAST_CHECK"
    fi
}

# Check for file changes
function _check_file_changes() {
    local last_check=$(cat "$DASHBOARD_LAST_CHECK" 2>/dev/null || echo 0)
    local changes_found=false
    local changes_list=()
    
    for file in "${DASHBOARD_WATCH_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            local file_mtime=$(stat -f %m "$file" 2>/dev/null || stat -c %Y "$file" 2>/dev/null)
            
            if [[ $file_mtime -gt $last_check ]]; then
                changes_found=true
                local relative_path="${file/#$HOME/~}"
                local mod_time=$(date -r "$file" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -d "@$file_mtime" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
                changes_list+=("$relative_path|$mod_time")
                
                # Log the change
                echo "$(date +%s)|$relative_path|$mod_time" >> "$DASHBOARD_CHANGES_LOG"
            fi
        elif [[ -d "$file" ]]; then
            # Check directory for changes
            if [[ -n $(find "$file" -type f -newer "$DASHBOARD_LAST_CHECK" 2>/dev/null | head -n 1) ]]; then
                changes_found=true
                local relative_path="${file/#$HOME/~}"
                changes_list+=("$relative_path|$(date '+%Y-%m-%d %H:%M:%S')")
            fi
        fi
    done
    
    # Update last check timestamp
    date +%s > "$DASHBOARD_LAST_CHECK"
    
    if [[ "$changes_found" == "true" ]]; then
        echo "${changes_list[@]}"
    fi
}

# Show system info section
function _dashboard_system_info() {
    echo -e "${C_BOLD}${C_CYAN}╔════════════════════════════════════════════════════════════╗${C_RESET}"
    echo -e "${C_BOLD}${C_CYAN}║               🖥️  TERMINAL DASHBOARD                       ║${C_RESET}"
    echo -e "${C_BOLD}${C_CYAN}╚════════════════════════════════════════════════════════════╝${C_RESET}"
    echo ""
    
    # Date and time
    echo -e "${C_BOLD}📅 Date:${C_RESET} $(date '+%A, %B %d, %Y')"
    echo -e "${C_BOLD}⏰ Time:${C_RESET} $(date '+%H:%M:%S %Z')"
    echo ""
    
    # System info
    local os_type=$(uname -s)
    local hostname=$(hostname)
    echo -e "${C_BOLD}💻 System:${C_RESET} $os_type on $hostname"
    echo -e "${C_BOLD}👤 User:${C_RESET} $USER"
    echo -e "${C_BOLD}📁 PWD:${C_RESET} ${PWD/#$HOME/~}"
    echo ""
}

# Show recent file changes
function _dashboard_recent_changes() {
    local changes=($(_check_file_changes))
    
    if [[ ${#changes[@]} -gt 0 ]]; then
        echo -e "${C_BOLD}${C_YELLOW}⚠️  Recent Changes Detected:${C_RESET}"
        echo ""
        for change in "${changes[@]}"; do
            local file=$(echo "$change" | cut -d'|' -f1)
            local time=$(echo "$change" | cut -d'|' -f2)
            echo -e "  ${C_GREEN}✓${C_RESET} $file"
            echo -e "    ${C_CYAN}Modified:${C_RESET} $time"
        done
        echo ""
    fi
    
    # Show last 5 changes from log
    if [[ -s "$DASHBOARD_CHANGES_LOG" ]]; then
        echo -e "${C_BOLD}📝 Recent Configuration Changes:${C_RESET}"
        echo ""
        tail -5 "$DASHBOARD_CHANGES_LOG" | while IFS='|' read -r timestamp file time; do
            local date_str=$(date -r "$timestamp" "+%b %d %H:%M" 2>/dev/null || date -d "@$timestamp" "+%b %d %H:%M" 2>/dev/null)
            echo -e "  ${C_BLUE}•${C_RESET} $file ${C_CYAN}($date_str)${C_RESET}"
        done
        echo ""
    fi
}

# Show running processes (AI, LLM, agents)
function _dashboard_running_processes() {
    local processes_found=false
    
    echo -e "${C_BOLD}🤖 Running AI/LLM Processes:${C_RESET}"
    echo ""
    
    # Check for ollama
    if pgrep -f "ollama" > /dev/null; then
        processes_found=true
        local count=$(pgrep -f "ollama" | wc -l | tr -d ' ')
        echo -e "  ${C_GREEN}●${C_RESET} Ollama (${count} processes)"
    fi
    
    # Check for python AI scripts
    if pgrep -f "ollama_cli.py\|gui_mcp.py\|alaina" > /dev/null; then
        processes_found=true
        local count=$(pgrep -f "ollama_cli.py\|gui_mcp.py\|alaina" | wc -l | tr -d ' ')
        echo -e "  ${C_GREEN}●${C_RESET} Python AI Agents (${count} processes)"
    fi
    
    # Check for MCP servers
    if pgrep -f "mcp" > /dev/null; then
        processes_found=true
        local count=$(pgrep -f "mcp" | wc -l | tr -d ' ')
        echo -e "  ${C_GREEN}●${C_RESET} MCP Servers (${count} processes)"
    fi
    
    if [[ "$processes_found" == "false" ]]; then
        echo -e "  ${C_YELLOW}○${C_RESET} No AI/LLM processes running"
    fi
    
    echo ""
}

# Show quick stats
function _dashboard_stats() {
    echo -e "${C_BOLD}📊 Quick Stats:${C_RESET}"
    echo ""
    
    # Command count today
    local today=$(date '+%Y-%m-%d')
    local cmd_count=$(fc -l -1 | wc -l | tr -d ' ')
    echo -e "  ${C_BLUE}Commands run:${C_RESET} $cmd_count"
    
    # Shell session time
    if [[ -n "$SHELL_START_TIME" ]]; then
        local duration=$(($(date +%s) - $SHELL_START_TIME))
        local hours=$((duration / 3600))
        local minutes=$(((duration % 3600) / 60))
        echo -e "  ${C_BLUE}Session time:${C_RESET} ${hours}h ${minutes}m"
    fi
    
    # Voice status
    if [[ "$VOICE_ENABLED" == "true" ]]; then
        echo -e "  ${C_GREEN}Voice:${C_RESET} Enabled ✓"
    else
        echo -e "  ${C_YELLOW}Voice:${C_RESET} Disabled"
    fi
    
    echo ""
}

# Show available commands
function _dashboard_quick_commands() {
    echo -e "${C_BOLD}⚡ Quick Commands:${C_RESET}"
    echo ""
    echo -e "  ${C_CYAN}dashboard${C_RESET}        - Show this dashboard"
    echo -e "  ${C_CYAN}kill-all-ai${C_RESET}     - Kill all AI/LLM processes"
    echo -e "  ${C_CYAN}vl${C_RESET}               - Voice listen"
    echo -e "  ${C_CYAN}vs <text>${C_RESET}        - Voice speak"
    echo -e "  ${C_CYAN}vchat${C_RESET}            - Voice chat with AI"
    echo -e "  ${C_CYAN}ollama-llama3${C_RESET}   - Chat with Llama3"
    echo ""
}

# Main dashboard display function
function dashboard() {
    clear
    _dashboard_system_info
    _dashboard_recent_changes
    _dashboard_running_processes
    _dashboard_stats
    _dashboard_quick_commands
    
    echo -e "${C_BOLD}${C_CYAN}════════════════════════════════════════════════════════════${C_RESET}"
    echo ""
}

# Auto-show dashboard on startup
function _auto_show_dashboard() {
    if [[ "$DASHBOARD_AUTO_SHOW" == "true" && -z "$DASHBOARD_SHOWN" ]]; then
        # Mark as shown for this session
        export DASHBOARD_SHOWN=1
        
        # Small delay to let other modules load
        sleep 0.1
        
        dashboard
    fi
}

# Track shell start time for session duration
export SHELL_START_TIME=$(date +%s)

# Initialize
_init_dashboard

# Hook to show dashboard after zshrc loads
if [[ -n "$ZSH_VERSION" ]]; then
    # Use precmd hook to show dashboard once
    autoload -U add-zsh-hook
    add-zsh-hook precmd _auto_show_dashboard
fi

echo "✅ Enhanced dashboard module loaded (type 'dashboard' to show)"
