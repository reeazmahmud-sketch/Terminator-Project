#!/usr/bin/env zsh
# ============================================================================
# 05-auto-suggestions-enhanced.zsh
# Smart command suggestions with auto-trigger on "s" and other single letters
# ============================================================================

# Command history database
typeset -g COMMAND_HISTORY_DB="${HOME}/.zsh_command_history.db"
typeset -g COMMAND_FREQ_CACHE="${HOME}/.zsh_command_freq_cache"
typeset -g AUTO_SUGGEST_TRIGGER_LETTERS=(s g c d l p r)  # Letters that auto-trigger

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
    
    # Get suggestions from frequency cache and recent history
    local -a suggestions
    local -A seen
    
    # From frequency cache (most common commands)
    while IFS= read -r line; do
        local cmd=$(echo "$line" | awk '{$1=""; print $0}' | sed 's/^ //')
        if [[ "$cmd" == "$prefix"* ]] && [[ -z "${seen[$cmd]}" ]]; then
            suggestions+=("$cmd")
            seen[$cmd]=1
        fi
        [[ ${#suggestions[@]} -ge $max_results ]] && break
    done < "$COMMAND_FREQ_CACHE"
    
    # From recent history if we need more
    if [[ ${#suggestions[@]} -lt $max_results ]]; then
        tail -500 "$COMMAND_HISTORY_DB" 2>/dev/null | \
            cut -d'|' -f2 | \
            tac | \
            while read -r cmd; do
                if [[ "$cmd" == "$prefix"* ]] && [[ -z "${seen[$cmd]}" ]]; then
                    suggestions+=("$cmd")
                    seen[$cmd]=1
                    [[ ${#suggestions[@]} -ge $max_results ]] && break
                fi
            done
    fi
    
    # Print unique suggestions
    printf '%s\n' "${suggestions[@]}"
}

# Show suggestions in a compact format
function _show_suggestions_inline() {
    local current_buffer="$BUFFER"
    local first_word="${current_buffer%% *}"
    
    # Get suggestions
    local suggestions=($(_get_suggestions "$first_word" 5))
    
    if [[ ${#suggestions[@]} -gt 0 ]]; then
        # Save cursor position
        local cursor_pos=$CURSOR
        
        # Show suggestions below prompt
        echo ""
        echo -e "\033[90m💡 Suggestions (Tab to cycle, Enter to execute):\033[0m"
        local i=1
        for suggestion in "${suggestions[@]}"; do
            echo -e "\033[36m  $i)\033[0m $suggestion"
            ((i++))
        done
        
        # Restore buffer
        zle reset-prompt
        CURSOR=$cursor_pos
    fi
}

# Auto-trigger suggestions when typing certain letters
function _auto_suggest_check() {
    local current_buffer="$BUFFER"
    local first_char="${current_buffer:0:1}"
    
    # Check if buffer is a single letter that should trigger suggestions
    if [[ ${#current_buffer} -eq 1 ]] && [[ " ${AUTO_SUGGEST_TRIGGER_LETTERS[@]} " =~ " ${first_char} " ]]; then
        # Small delay to avoid showing on every keystroke
        sleep 0.1
        _show_suggestions_inline
    fi
}

# Show suggestions widget
function _show_suggestions_widget() {
    local current_buffer="$BUFFER"
    local first_word="${current_buffer%% *}"
    
    # Only show suggestions for single letter prefixes or specific patterns
    if [[ ${#first_word} -ge 1 ]]; then
        local suggestions=($(_get_suggestions "$first_word" 8))
        
        if [[ ${#suggestions[@]} -gt 0 ]]; then
            echo ""
            echo -e "\033[1m\033[36m💡 Command Suggestions:\033[0m"
            local i=1
            for suggestion in "${suggestions[@]}"; do
                # Highlight the matching prefix
                local highlighted=$(echo "$suggestion" | sed "s/^$first_word/\x1b[1m\x1b[33m$first_word\x1b[0m/")
                echo -e "  \033[36m$i)\033[0m $highlighted"
                ((i++))
            done
            echo ""
            echo -e "\033[90m(Press number key to use, or continue typing)\033[0m"
            zle reset-prompt
        else
            echo ""
            echo -e "\033[90m💡 No suggestions found for '$first_word'\033[0m"
            zle reset-prompt
        fi
    fi
}

# Accept suggestion by number
function _accept_suggestion_num() {
    local current_buffer="$BUFFER"
    local first_word="${current_buffer%% *}"
    local num="${KEYS: -1}"  # Get last pressed key
    
    if [[ "$num" =~ ^[1-9]$ ]]; then
        local suggestions=($(_get_suggestions "$first_word" 9))
        
        if [[ $num -le ${#suggestions[@]} ]]; then
            BUFFER="${suggestions[$num]}"
            zle end-of-line
        fi
    fi
}

# Accept first suggestion
function _accept_first_suggestion() {
    local current_buffer="$BUFFER"
    local first_word="${current_buffer%% *}"
    local suggestions=($(_get_suggestions "$first_word" 1))
    
    if [[ ${#suggestions[@]} -gt 0 ]]; then
        BUFFER="${suggestions[1]}"
        zle end-of-line
    fi
}

# Tab completion integration
function _suggest_tab_completion() {
    local current_buffer="$BUFFER"
    local first_word="${current_buffer%% *}"
    
    # If buffer is just one word, try suggestions first
    if [[ ! "$current_buffer" =~ [[:space:]] ]]; then
        local suggestions=($(_get_suggestions "$first_word" 1))
        if [[ ${#suggestions[@]} -gt 0 ]]; then
            BUFFER="${suggestions[1]}"
            zle end-of-line
            return 0
        fi
    fi
    
    # Fall back to normal completion
    zle expand-or-complete
}

# ZLE widgets
zle -N _show_suggestions_widget
zle -N _accept_first_suggestion
zle -N _accept_suggestion_num
zle -N _suggest_tab_completion

# Key bindings
bindkey '^[s' _show_suggestions_widget      # Alt+s to show suggestions
bindkey '^[a' _accept_first_suggestion      # Alt+a to accept first suggestion
bindkey -s '^[1' '1'                        # Number keys to select
bindkey -s '^[2' '2'
bindkey -s '^[3' '3'
bindkey -s '^[4' '4'
bindkey -s '^[5' '5'

# Override Tab to try suggestions first
# bindkey '^I' _suggest_tab_completion       # Uncomment to enable Tab suggestion

# Hook to track commands after execution
autoload -U add-zsh-hook
add-zsh-hook preexec _track_command

# Initialize on module load
_init_command_tracking

# Create initial frequency cache if empty
if [[ ! -s "$COMMAND_FREQ_CACHE" ]]; then
    _update_frequency_cache &!
fi

# Aliases
alias suggestions='_show_suggestions_widget'
alias rebuild-suggestions='_update_frequency_cache && echo "✅ Suggestions cache rebuilt"'
alias show-suggest-stats='echo "Total commands tracked: $(wc -l < $COMMAND_HISTORY_DB)" && echo "Top 10 commands:" && head -10 $COMMAND_FREQ_CACHE'

# Auto-suggest function that can be called manually
function suggest() {
    local prefix="${1:-$BUFFER}"
    _get_suggestions "$prefix" 10
}

echo "✅ Enhanced auto-suggestions loaded"
echo "   Alt+s - Show suggestions | Alt+a - Accept first"
echo "   Type single letter (s, g, c, etc.) and wait ~0.1s for auto-suggestions"
