#!/bin/bash
# TERMINATOR Biometric Shell Guard - Installation Script
# Installs shell hooks into user's shell configuration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TERMINATOR BIOMETRIC SHELL GUARD INSTALLATION           ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}❌ Error: This guard only works on macOS${NC}"
    exit 1
fi

# Check if Touch ID is available
if ! pgrep -x "biometrickitd" > /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: Touch ID service not detected${NC}"
    echo -e "${YELLOW}   Password authentication will be used as fallback${NC}"
fi

# Paths
PROJECT_DIR="${HOME}/Desktop/Terminator-Project"
GUARD_SCRIPT="${PROJECT_DIR}/core/terminator_biometric_shell_guard.py"
HOOKS_SCRIPT="${PROJECT_DIR}/scripts/shell_guard_hooks.sh"
ZSHRC="${HOME}/.zshrc"
BASHRC="${HOME}/.bashrc"

# Check if guard script exists
if [[ ! -f "$GUARD_SCRIPT" ]]; then
    echo -e "${RED}❌ Error: Guard script not found at: $GUARD_SCRIPT${NC}"
    exit 1
fi

# Make scripts executable
chmod +x "$GUARD_SCRIPT"
chmod +x "$HOOKS_SCRIPT"

echo -e "${GREEN}✓${NC} Found guard scripts"

# Initialize the guard (creates config files)
echo -e "\n${BLUE}Initializing shell guard...${NC}"
python3 "$GUARD_SCRIPT" status

# Configure Touch ID for sudo (required for biometric auth)
echo -e "\n${BLUE}Configuring Touch ID for sudo...${NC}"

SUDO_PAM="/etc/pam.d/sudo"
TOUCHID_LINE="auth       sufficient     pam_tid.so"

if sudo grep -q "pam_tid.so" "$SUDO_PAM" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Touch ID already configured for sudo"
else
    echo -e "${YELLOW}➜${NC} Adding Touch ID support to sudo..."
    echo -e "${YELLOW}   (This requires your password)${NC}"

    # Create backup
    sudo cp "$SUDO_PAM" "${SUDO_PAM}.backup.$(date +%Y%m%d)"

    # Add Touch ID line at the top (after comments)
    sudo sed -i '' "1a\\
$TOUCHID_LINE
" "$SUDO_PAM"

    echo -e "${GREEN}✓${NC} Touch ID configured for sudo"
fi

# Add hooks to .zshrc
echo -e "\n${BLUE}Installing shell hooks to .zshrc...${NC}"

ZSHRC_MARKER="# TERMINATOR Biometric Shell Guard"
ZSHRC_HOOKS="
$ZSHRC_MARKER
if [[ -f \"$HOOKS_SCRIPT\" ]]; then
    source \"$HOOKS_SCRIPT\"
fi
"

if grep -q "$ZSHRC_MARKER" "$ZSHRC" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  Shell Guard hooks already installed in .zshrc"
else
    echo "$ZSHRC_HOOKS" >> "$ZSHRC"
    echo -e "${GREEN}✓${NC} Added shell hooks to .zshrc"
fi

# Optionally add to .bashrc
if [[ -f "$BASHRC" ]]; then
    echo -e "\n${BLUE}Installing shell hooks to .bashrc...${NC}"

    if grep -q "$ZSHRC_MARKER" "$BASHRC" 2>/dev/null; then
        echo -e "${YELLOW}⚠${NC}  Shell Guard hooks already installed in .bashrc"
    else
        echo "$ZSHRC_HOOKS" >> "$BASHRC"
        echo -e "${GREEN}✓${NC} Added shell hooks to .bashrc"
    fi
fi

# Create alias for easy access
echo -e "\n${BLUE}Creating shell guard alias...${NC}"

ALIAS_LINE="alias shell-guard='python3 $GUARD_SCRIPT'"

if ! grep -q "alias shell-guard=" "$ZSHRC" 2>/dev/null; then
    echo "$ALIAS_LINE" >> "$ZSHRC"
    echo -e "${GREEN}✓${NC} Added 'shell-guard' alias to .zshrc"
fi

# Final status
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              INSTALLATION COMPLETE!                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 What was installed:${NC}"
echo -e "   ✓ Biometric Shell Guard Python module"
echo -e "   ✓ Shell command interceptors"
echo -e "   ✓ Touch ID support for sudo"
echo -e "   ✓ Hooks in your shell configuration"
echo ""
echo -e "${BLUE}🎯 Usage:${NC}"
echo -e "   ${GREEN}shell-guard status${NC}       - View guard status"
echo -e "   ${GREEN}shell-guard enable${NC}       - Enable protection"
echo -e "   ${GREEN}shell-guard disable${NC}      - Disable protection (requires auth)"
echo -e "   ${GREEN}shell-guard audit${NC}        - View security audit log"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo -e "   1. Restart your terminal or run: ${GREEN}source ~/.zshrc${NC}"
echo -e "   2. The guard is now ${GREEN}ACTIVE${NC}"
echo -e "   3. Protected operations will require Touch ID"
echo ""
echo -e "${BLUE}🔒 Protected Operations:${NC}"
echo -e "   • brew install/uninstall"
echo -e "   • npm install -g"
echo -e "   • pip/pip3 install"
echo -e "   • chsh (change shell)"
echo -e "   • Starting bash/sh from zsh"
echo ""
echo -e "${BLUE}📊 Security:${NC}"
echo -e "   • Audit log: ${HOME}/.terminator_security/shell_guard_audit.log"
echo -e "   • Config: ${HOME}/.terminator_security/shell_guard_config.json"
echo ""
echo -e "${GREEN}✅ Your shell is now protected!${NC}"
echo ""
