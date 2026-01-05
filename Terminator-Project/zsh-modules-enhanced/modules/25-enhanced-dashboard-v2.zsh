#!/usr/bin/env zsh
# ============================================================================
# 25-enhanced-dashboard-v2.zsh
# Enhanced dashboard with file change tracking and guaranteed display
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
typeset -g DASHBOARD_SESSION_ID="${HOME}/.zsh_dashboard_session_$$"

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
typeset -g C_GRAY="\033[90m"

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
    
    # Mark this session
    touch "$DASHBOARD_SESSION_ID"
}

# Check for file changes
function _check_file_changes() {
    local last_check=$(cat "$DASHBOARD_LAST_CHECK" 2>/dev/null || echo 0)
    local changes_found=false
    local -a changes_list
    
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
            local newest=$(find "$file" -type f -newer "$DASHBOARD_LAST_CHECK" 2>/dev/null | head -n 1)
            if [[ -n "$newest" ]]; then
                changes_found=true
                local relative_path="${file/#$HOME/~}"
                local newest_file=$(basename "$newest")
                changes_list+=("$relative_path/$newest_file|$(date '+%Y-%m-%d %H:%M:%S')")
            fi
        fi
    done
    
    # Update last check timestamp
    date +%s > "$DASHBOARD_LAST_CHECK"
    
    if [[ "$changes_found" == "true" ]]; then
        printf '%s\n' "${changes_list[@]}"
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
    local hostname=$(hostname -s 2>/dev/null || hostname)
    echo -e "${C_BOLD}💻 System:${C_RESET} $os_type on $hostname"
    echo -e "${C_BOLD}👤 User:${C_RESET} $USER"
    echo -e "${C_BOLD}📁 PWD:${C_RESET} ${PWD/#$HOME/~}"
    
    # Shell info
    echo -e "${C_BOLD}🐚 Shell:${C_RESET} $SHELL ($ZSH_VERSION)"
    echo ""
}

# Show recent file changes
function _dashboard_recent_changes() {
    local -a changes
    changes=("${(@f)$(_check_file_changes)}")
    
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
            echo -e "  ${C_BLUE}•${C_RESET} $file ${C_GRAY}($date_str)${C_RESET}"
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
    if pgrep -f "ollama" > /dev/null 2>&1; then
        processes_found=true
        local count=$(pgrep -f "ollama" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${C_GREEN}●${C_RESET} Ollama ${C_GRAY}($count processes)${C_RESET}"
    fi
    
    # Check for python AI scripts
    if pgrep -f "ollama_cli.py\|gui_mcp.py\|alaina" > /dev/null 2>&1; then
        processes_found=true
        local count=$(pgrep -f "ollama_cli.py\|gui_mcp.py\|alaina" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${C_GREEN}●${C_RESET} Python AI Agents ${C_GRAY}($count processes)${C_RESET}"
    fi
    
    # Check for MCP servers
    if pgrep -f "mcp" > /dev/null 2>&1; then
        processes_found=true
        local count=$(pgrep -f "mcp" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${C_GREEN}●${C_RESET} MCP Servers ${C_GRAY}($count processes)${C_RESET}"
    fi
    
    # Check for voice processes
    if pgrep -f "speech_recognition\|gtts" > /dev/null 2>&1; then
        processes_found=true
        echo -e "  ${C_GREEN}●${C_RESET} Voice Services ${C_GRAY}(active)${C_RESET}"
    fi
    
    if [[ "$processes_found" == "false" ]]; then
        echo -e "  ${C_GRAY}○ No AI/LLM processes running${C_RESET}"
    fi
    
    echo ""
}

# Show quick stats
function _dashboard_stats() {
    echo -e "${C_BOLD}📊 Session Stats:${C_RESET}"
    echo ""
    
    # Command count this session
    local cmd_count=$(fc -l 1 2>/dev/null | wc -l | tr -d ' ')
    echo -e "  ${C_BLUE}Commands this session:${C_RESET} $cmd_count"
    
    # Shell session time
    if [[ -n "$SHELL_START_TIME" ]]; then
        local duration=$(($(date +%s) - $SHELL_START_TIME))
        local hours=$((duration / 3600))
        local minutes=$(((duration % 3600) / 60))
        if [[ $hours -gt 0 ]]; then
            echo -e "  ${C_BLUE}Session uptime:${C_RESET} ${hours}h ${minutes}m"
        else
            echo -e "  ${C_BLUE}Session uptime:${C_RESET} ${minutes}m"
        fi
    fi
    
    # Voice status
    if [[ "$VOICE_ENABLED" == "true" ]]; then
        echo -e "  ${C_GREEN}Voice:${C_RESET} Enabled ✓"
    else
        echo -e "  ${C_GRAY}Voice:${C_RESET} Disabled"
    fi
    
    # Auto-suggestions status
    if [[ -f "$COMMAND_FREQ_CACHE" ]]; then
        local suggestions_count=$(wc -l < "$COMMAND_FREQ_CACHE" 2>/dev/null | tr -d ' ')
        echo -e "  ${C_GREEN}Auto-suggestions:${C_RESET} $suggestions_count commands cached"
    fi
    
    echo ""
}

# Show available commands
function _dashboard_quick_commands() {
    echo -e "${C_BOLD}⚡ Quick Commands:${C_RESET}"
    echo ""
    echo -e "  ${C_CYAN}dashboard${C_RESET}          - Show this dashboard"
    echo -e "  ${C_CYAN}kill-all-ai${C_RESET} / ${C_CYAN}ka${C_RESET} - Kill all AI/LLM processes"
    echo -e "  ${C_CYAN}vl${C_RESET}                 - Voice listen"
    echo -e "  ${C_CYAN}vs <text>${C_RESET}          - Voice speak"
    echo -e "  ${C_CYAN}vchat${C_RESET}              - Voice chat with AI"
    echo -e "  ${C_CYAN}suggestions${C_RESET}        - Show command suggestions (Alt+s)"
    echo ""
}

# Show tips
function _dashboard_tips() {
    local -a tips=(
        "Press ${C_CYAN}Alt+s${C_RESET} to show command suggestions for what you're typing"
        "Type ${C_CYAN}Ctrl+V${C_RESET} to use voice input in your command"
        "Use ${C_CYAN}kill-all-ai${C_RESET} or ${C_CYAN}ka${C_RESET} to stop all AI processes at once"
        "Run ${C_CYAN}vchat${C_RESET} to have a voice conversation with your AI"
        "Type ${C_CYAN}dashboard${C_RESET} anytime to see this screen"
    )
    
    # Pick a random tip
    local tip_index=$(( RANDOM % ${#tips[@]} + 1 ))
    echo -e "${C_BOLD}💡 Tip:${C_RESET} ${tips[$tip_index]}"
    echo ""
}

# Main dashboard display function
function dashboard() {
    # Clear screen for clean display
    clear
    
    _dashboard_system_info
    _dashboard_recent_changes
    _dashboard_running_processes
    _dashboard_stats
    _dashboard_quick_commands
    _dashboard_tips
    
    echo -e "${C_BOLD}${C_CYAN}════════════════════════════════════════════════════════════${C_RESET}"
    echo ""
}

# Compact dashboard (no clear, less spacing)
function dashboard-compact() {
    echo ""
    echo -e "${C_BOLD}${C_CYAN}═══ 🖥️  Terminal Dashboard ═══${C_RESET}"
    echo ""
    
    # Just the essentials
    local -a changes
    changes=("${(@f)$(_check_file_changes)}")
    
    if [[ ${#changes[@]} -gt 0 ]]; then
        echo -e "${C_YELLOW}⚠️  ${#changes[@]} configuration file(s) changed${C_RESET}"
    fi
    
    # Running processes
    local ai_running=false
    if pgrep -f "ollama\|gui_mcp\|alaina" > /dev/null 2>&1; then
        ai_running=true
        echo -e "${C_GREEN}🤖 AI/LLM processes running${C_RESET}"
    fi
    
    if [[ "$ai_running" == "false" ]] && [[ ${#changes[@]} -eq 0 ]]; then
        echo -e "${C_GRAY}All quiet - no changes, no processes${C_RESET}"
    fi
    
    echo ""
}

# Auto-show dashboard on startup or source
function _auto_show_dashboard() {
    # Check if we should show the dashboard
    if [[ "$DASHBOARD_AUTO_SHOW" != "true" ]]; then
        return
    fi
    
    # Check if already shown in this session
    # We use a combination of PID and a marker to track
    local marker="${HOME}/.zsh_dashboard_shown_$$"
    
    if [[ ! -f "$marker" ]]; then
        # Mark as shown
        touch "$marker"
        
        # Clean up old markers
        find "${HOME}" -maxdepth 1 -name ".zsh_dashboard_shown_*" -mtime +1 -delete 2>/dev/null
        
        # Small delay to let prompt render
        sleep 0.05
        
        # Show dashboard
        dashboard
    fi
}

# Detect if this is a reload (source ~/.zshrc)
function _detect_reload() {
    # If DASHBOARD_RELOAD_DETECTED is set, we know it's a reload
    if [[ "$DASHBOARD_RELOAD_DETECTED" == "1" ]]; then
        # Show compact dashboard for reloads
        dashboard-compact
    fi
}

# Track shell start time for session duration
if [[ -z "$SHELL_START_TIME" ]]; then
    export SHELL_START_TIME=$(date +%s)
fi

# Mark that we're loading (used to detect reloads)
export DASHBOARD_RELOAD_DETECTED=1

# Initialize
_init_dashboard

# Hook to show dashboard
if [[ -n "$ZSH_VERSION" ]]; then
    autoload -U add-zsh-hook
    
    # Show on first prompt
    add-zsh-hook precmd _auto_show_dashboard
    
    # Also trigger on reload detection
    _detect_reload
fi

echo "✅ Enhanced dashboard loaded (type 'dashboard' to show)"
