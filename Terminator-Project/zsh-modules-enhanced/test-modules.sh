#!/usr/bin/env zsh
# ============================================================================
# test-modules.sh
# Test script to verify all modules are working correctly
# ============================================================================

# Colors
C_RESET="\033[0m"
C_GREEN="\033[32m"
C_RED="\033[31m"
C_YELLOW="\033[33m"
C_BOLD="\033[1m"

echo -e "${C_BOLD}Testing Enhanced ZSH Modules...${C_RESET}"
echo ""

MODULES_DIR="${HOME}/.zsh/modules"
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
test_module() {
    local module_name="$1"
    local module_file="${MODULES_DIR}/${module_name}"
    
    echo -n "Testing $module_name... "
    
    if [[ ! -f "$module_file" ]]; then
        echo -e "${C_RED}FAILED${C_RESET} (file not found)"
        ((TESTS_FAILED++))
        return 1
    fi
    
    if [[ ! -r "$module_file" ]]; then
        echo -e "${C_RED}FAILED${C_RESET} (not readable)"
        ((TESTS_FAILED++))
        return 1
    fi
    
    # Try to source the module in a subshell
    if ( source "$module_file" ) &>/dev/null; then
        echo -e "${C_GREEN}PASSED${C_RESET}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${C_RED}FAILED${C_RESET} (source error)"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test each module
echo -e "${C_BOLD}Module Tests:${C_RESET}"
test_module "05-auto-suggestions.zsh"
test_module "15-terminal-voice.zsh"
test_module "25-enhanced-dashboard.zsh"
test_module "35-kill-all-processes.zsh"

echo ""
echo -e "${C_BOLD}Function Tests:${C_RESET}"

# Test if functions are defined
test_function() {
    local func_name="$1"
    echo -n "Testing function $func_name... "
    
    if type "$func_name" &>/dev/null; then
        echo -e "${C_GREEN}PASSED${C_RESET}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${C_RED}FAILED${C_RESET} (not defined)"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Source modules for testing
for module in ${MODULES_DIR}/[0-9]*.zsh; do
    [[ -f "$module" ]] && source "$module" 2>/dev/null
done

# Test key functions
test_function "dashboard"
test_function "kill-all-ai"
test_function "voice-listen"
test_function "_get_suggestions"

echo ""
echo -e "${C_BOLD}Dependency Tests:${C_RESET}"

# Test Python
echo -n "Testing Python 3... "
if command -v python3 &>/dev/null; then
    echo -e "${C_GREEN}PASSED${C_RESET} ($(python3 --version))"
    ((TESTS_PASSED++))
else
    echo -e "${C_YELLOW}WARNING${C_RESET} (not found, voice features will be disabled)"
fi

# Test voice dependencies
echo -n "Testing SpeechRecognition... "
if python3 -c "import speech_recognition" 2>/dev/null; then
    echo -e "${C_GREEN}PASSED${C_RESET}"
    ((TESTS_PASSED++))
else
    echo -e "${C_YELLOW}WARNING${C_RESET} (not installed)"
fi

echo -n "Testing gTTS... "
if python3 -c "import gtts" 2>/dev/null; then
    echo -e "${C_GREEN}PASSED${C_RESET}"
    ((TESTS_PASSED++))
else
    echo -e "${C_YELLOW}WARNING${C_RESET} (not installed)"
fi

# Test Ollama
echo -n "Testing Ollama... "
if command -v ollama &>/dev/null; then
    echo -e "${C_GREEN}PASSED${C_RESET}"
    ((TESTS_PASSED++))
else
    echo -e "${C_YELLOW}WARNING${C_RESET} (not installed, voice chat will be disabled)"
fi

echo ""
echo -e "${C_BOLD}File Tests:${C_RESET}"

# Test required directories
echo -n "Testing ~/.zsh/modules directory... "
if [[ -d "${HOME}/.zsh/modules" ]]; then
    echo -e "${C_GREEN}PASSED${C_RESET}"
    ((TESTS_PASSED++))
else
    echo -e "${C_RED}FAILED${C_RESET}"
    ((TESTS_FAILED++))
fi

# Test .zshrc exists
echo -n "Testing ~/.zshrc exists... "
if [[ -f "${HOME}/.zshrc" ]]; then
    echo -e "${C_GREEN}PASSED${C_RESET}"
    ((TESTS_PASSED++))
else
    echo -e "${C_RED}FAILED${C_RESET}"
    ((TESTS_FAILED++))
fi

# Test .zshrc contains module loader
echo -n "Testing ~/.zshrc contains module loader... "
if grep -q "Enhanced ZSH Modules" "${HOME}/.zshrc" 2>/dev/null; then
    echo -e "${C_GREEN}PASSED${C_RESET}"
    ((TESTS_PASSED++))
else
    echo -e "${C_YELLOW}WARNING${C_RESET} (module loader not found)"
fi

echo ""
echo -e "${C_BOLD}═══════════════════════════════════════════════${C_RESET}"
echo -e "${C_BOLD}Test Results:${C_RESET}"
echo -e "  ${C_GREEN}Passed: $TESTS_PASSED${C_RESET}"
echo -e "  ${C_RED}Failed: $TESTS_FAILED${C_RESET}"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${C_GREEN}${C_BOLD}✓ All tests passed!${C_RESET}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: source ~/.zshrc"
    echo "  2. Try: dashboard"
    echo "  3. Try: Alt+s for suggestions"
    exit 0
else
    echo -e "${C_RED}${C_BOLD}✗ Some tests failed${C_RESET}"
    echo ""
    echo "Please review the errors above and:"
    echo "  1. Make sure modules are installed correctly"
    echo "  2. Check that ~/.zshrc loads the modules"
    echo "  3. Install missing dependencies"
    exit 1
fi
