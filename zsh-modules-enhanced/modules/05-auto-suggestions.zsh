#!/usr/bin/env zsh
# ============================================================================
# 05-auto-suggestions.zsh
# Smart command suggestions based on usage frequency and context
# ============================================================================

# Command history database
typeset -g COMMAND_HISTORY_DB="${HOME}/.zsh_command_history.db"
typeset -g COMMAND_FREQ_CACHE="${HOME}/.zsh_command_freq_cache"

# Initialize command frequency tracking
function _init_command_tracking() {
    # Create history database if it doesn't exist
    if [[ ! -f "$COMMAND_HISTORY_DB" ]]; then
        touch "$COMMAND_HISTORY_DB"
    fi
    
    # Create frequency cache
    if [[ ! -f "$COMMAND_FREQ_CACHE" ]]; then
        touch "$COMMAND_FREQ_CACHE"
    fi
}

# Track command usage
function _track_command() {
    local cmd="$1"
    [[ -z "$cmd" ]] && return
    
    # Append to history with timestamp
    echo "$(date +%s)|$cmd" >> "$COMMAND_HISTORY_DB"
    
    # Update frequency cache asynchronously
    _update_frequency_cache &!
}

# Update frequency cache
function _update_frequency_cache() {
    # Count command frequencies from last 1000 commands
    tail -1000 "$COMMAND_HISTORY_DB" 2>/dev/null | \
        cut -d'|' -f2 | \
        sort | uniq -c | sort -rn | \
        head -100 > "$COMMAND_FREQ_CACHE"
}

# Get suggestions for a given prefix
function _get_suggestions() {
    local prefix="$1"
    local max_results="${2:-10}"
    
    if [[ -z "$prefix" ]]; then
        return
    fi
    
    # Get suggestions from frequency cache
    local suggestions=()
    
    # From frequency cache
    while IFS= read -r line; do
        local cmd=$(echo "$line" | awk '{$1=""; print $0}' | sed 's/^ //')
        if [[ "$cmd" == "$prefix"* ]]; then
            suggestions+=("$cmd")
        fi
    done < "$COMMAND_FREQ_CACHE"
    
    # From recent history
    tail -500 "$COMMAND_HISTORY_DB" 2>/dev/null | \
        cut -d'|' -f2 | \
        grep "^$prefix" | \
        while read -r cmd; do
            if [[ ! " ${suggestions[@]} " =~ " ${cmd} " ]]; then
                suggestions+=("$cmd")
            fi
        done
    
    # Print unique suggestions
    printf '%s\n' "${suggestions[@]}" | head -n "$max_results"
}

# Show suggestions widget
function _show_suggestions_widget() {
    local current_buffer="$BUFFER"
    local first_word="${current_buffer%% *}"
    
    # Only show suggestions for single letter prefixes or specific patterns
    if [[ ${#first_word} -eq 1 ]] || [[ "$first_word" =~ ^(cd|ls|git|python|node|npm) ]]; then
        local suggestions=($(_get_suggestions "$first_word" 5))
        
        if [[ ${#suggestions[@]} -gt 0 ]]; then
            echo ""
            echo "💡 Suggestions:"
            local i=1
            for suggestion in "${suggestions[@]}"; do
                echo "  $i) $suggestion"
                ((i++))
            done
            zle reset-prompt
        fi
    fi
}

# Auto-complete from suggestions
function _accept_suggestion() {
    local current_buffer="$BUFFER"
    local first_word="${current_buffer%% *}"
    local suggestions=($(_get_suggestions "$first_word" 5))
    
    if [[ ${#suggestions[@]} -gt 0 ]]; then
        # Use the first suggestion
        BUFFER="${suggestions[1]}"
        zle end-of-line
    fi
}

# ZLE widgets
zle -N _show_suggestions_widget
zle -N _accept_suggestion

# Key bindings
bindkey '^[s' _show_suggestions_widget  # Alt+s to show suggestions
bindkey '^[a' _accept_suggestion         # Alt+a to accept first suggestion

# Hook to track commands after execution
autoload -U add-zsh-hook
add-zsh-hook preexec _track_command

# Initialize on module load
_init_command_tracking

# Create initial frequency cache if empty
if [[ ! -s "$COMMAND_FREQ_CACHE" ]]; then
    _update_frequency_cache &!
fi

# Alias to manually show suggestions
alias suggestions='_show_suggestions_widget'

# Alias to rebuild cache
alias rebuild-suggestions='_update_frequency_cache && echo "✅ Suggestions cache rebuilt"'

echo "✅ Auto-suggestions module loaded (Alt+s to show, Alt+a to accept)"
