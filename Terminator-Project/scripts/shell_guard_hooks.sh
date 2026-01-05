#!/bin/bash
# TERMINATOR Biometric Shell Guard - Shell Hooks
# This file provides command interception for dangerous operations

# Path to the guard Python script
GUARD_SCRIPT="${HOME}/Desktop/Terminator-Project/core/terminator_biometric_shell_guard.py"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check command authorization
check_command_authorization() {
    local cmd="$*"

    # Call the Python guard to check the command
    if python3 "$GUARD_SCRIPT" test "$cmd" 2>/dev/null; then
        return 0  # Authorized
    else
        return 1  # Blocked
    fi
}

# Intercept brew command
brew() {
    local subcmd="$1"

    # Check if it's an installation command
    if [[ "$subcmd" == "install" || "$subcmd" == "uninstall" || "$subcmd" == "remove" ]]; then
        echo -e "${YELLOW}🔒 Biometric authorization required for: brew $*${NC}"

        if check_command_authorization "brew $*"; then
            echo -e "${GREEN}✅ Authorized - executing: brew $*${NC}"
            command brew "$@"
        else
            echo -e "${RED}❌ BLOCKED: brew $* - Authorization failed${NC}"
            return 1
        fi
    else
        # Safe brew commands - pass through
        command brew "$@"
    fi
}

# Intercept npm global install
npm() {
    local has_global_install=0

    # Check for global install flag
    for arg in "$@"; do
        if [[ "$arg" == "-g" || "$arg" == "--global" ]]; then
            has_global_install=1
            break
        fi
    done

    if [[ $has_global_install -eq 1 ]]; then
        echo -e "${YELLOW}🔒 Biometric authorization required for: npm $*${NC}"

        if check_command_authorization "npm $*"; then
            echo -e "${GREEN}✅ Authorized - executing: npm $*${NC}"
            command npm "$@"
        else
            echo -e "${RED}❌ BLOCKED: npm $* - Authorization failed${NC}"
            return 1
        fi
    else
        # Local npm operations - pass through
        command npm "$@"
    fi
}

# Intercept pip/pip3 install
pip() {
    if [[ "$1" == "install" ]]; then
        echo -e "${YELLOW}🔒 Biometric authorization required for: pip $*${NC}"

        if check_command_authorization "pip $*"; then
            echo -e "${GREEN}✅ Authorized - executing: pip $*${NC}"
            command pip "$@"
        else
            echo -e "${RED}❌ BLOCKED: pip $* - Authorization failed${NC}"
            return 1
        fi
    else
        command pip "$@"
    fi
}

pip3() {
    if [[ "$1" == "install" ]]; then
        echo -e "${YELLOW}🔒 Biometric authorization required for: pip3 $*${NC}"

        if check_command_authorization "pip3 $*"; then
            echo -e "${GREEN}✅ Authorized - executing: pip3 $*${NC}"
            command pip3 "$@"
        else
            echo -e "${RED}❌ BLOCKED: pip3 $* - Authorization failed${NC}"
            return 1
        fi
    else
        command pip3 "$@"
    fi
}

# Intercept shell switching (chsh)
chsh() {
    echo -e "${YELLOW}🔒 Biometric authorization required for: chsh $*${NC}"

    if check_command_authorization "chsh $*"; then
        echo -e "${GREEN}✅ Authorized - executing: chsh $*${NC}"
        command chsh "$@"
    else
        echo -e "${RED}❌ BLOCKED: chsh $* - Authorization failed${NC}"
        return 1
    fi
}

# Monitor when bash is started from zsh (potential unauthorized shell)
bash() {
    echo -e "${YELLOW}⚠️  Starting bash shell - checking authorization...${NC}"

    if check_command_authorization "bash shell"; then
        echo -e "${GREEN}✅ Bash shell authorized${NC}"
        command bash "$@"
    else
        echo -e "${RED}❌ BLOCKED: Unauthorized shell - bash${NC}"
        echo -e "${RED}   Your authorized shell is: $SHELL${NC}"
        return 1
    fi
}

# Monitor when sh is started
sh() {
    echo -e "${YELLOW}⚠️  Starting sh shell - checking authorization...${NC}"

    if check_command_authorization "sh shell"; then
        echo -e "${GREEN}✅ sh shell authorized${NC}"
        command sh "$@"
    else
        echo -e "${RED}❌ BLOCKED: Unauthorized shell - sh${NC}"
        echo -e "${RED}   Your authorized shell is: $SHELL${NC}"
        return 1
    fi
}

# Check current shell authorization on startup
check_shell_on_startup() {
    if python3 "$GUARD_SCRIPT" check-shell 2>/dev/null; then
        echo -e "${GREEN}🔒 Shell Guard: Current shell authorized${NC}"
    else
        echo -e "${RED}⚠️  Shell Guard: WARNING - Unauthorized shell detected!${NC}"
        echo -e "${RED}   This shell is not in your authorized list.${NC}"
        echo -e "${RED}   Some operations may be blocked.${NC}"
    fi
}

# Export functions so they're available in the shell
#export -f check_command_authorization
#export -f brew
#export -f npm
#export -f pip
#export -f pip3
#export -f chsh
#export -f bash
#export -f sh
#export -f check_shell_on_startup

# Run shell check on startup (optional, comment out if too intrusive)
# check_shell_on_startup
