#!/bin/bash
# TERMINATOR Universal CLI - One-Command Installation
# Run this once to set up the 'terminator' command globally

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║      🤖 TERMINATOR Universal CLI - Installation 🤖             ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📍 Installation directory: $SCRIPT_DIR"
echo ""

# Make terminator launcher executable
echo "1️⃣  Making 'terminator' executable..."
chmod +x "$SCRIPT_DIR/terminator"
chmod +x "$SCRIPT_DIR/terminator_universal_cli.py"
echo "   ✅ Done"
echo ""

# Add to PATH
echo "2️⃣  Adding to PATH..."

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
   SHELL_RC="$HOME/.zshrc"
   SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
   SHELL_RC="$HOME/.bashrc"
   SHELL_NAME="bash"
else
   SHELL_RC="$HOME/.profile"
   SHELL_NAME="shell"
fi

echo "   Detected $SHELL_NAME"

# Check if already in PATH
if grep -q "Terminator-Project" "$SHELL_RC" 2>/dev/null; then
    echo "   ⚠️  Already in PATH, skipping..."
else
    echo "" >> "$SHELL_RC"
    echo "# TERMINATOR Universal CLI" >> "$SHELL_RC"
    echo "export PATH=\"\$PATH:$SCRIPT_DIR\"" >> "$SHELL_RC"
    echo "   ✅ Added to $SHELL_RC"
fi
echo ""

# Install Python dependencies
echo "3️⃣  Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install rich httpx -q
    echo "   ✅ Dependencies installed"
else
    echo "   ⚠️  pip3 not found, install manually: pip3 install rich httpx"
fi
echo ""

# Create settings directory
echo "4️⃣  Creating settings directory..."
mkdir -p "$HOME/.terminator_monitor"
echo "   ✅ Created ~/.terminator_monitor/"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              ✅ INSTALLATION COMPLETE! ✅                       ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 To start using TERMINATOR CLI:"
echo ""
echo "   1. Reload your shell:"
echo "      source $SHELL_RC"
echo ""
echo "   2. Launch TERMINATOR:"
echo "      terminator"
echo ""
echo "   3. Or run directly:"
echo "      cd $SCRIPT_DIR"
echo "      ./terminator"
echo ""
echo "📚 Read the guide:"
echo "   cat $SCRIPT_DIR/UNIVERSAL_CLI_GUIDE.md"
echo ""
echo "💡 Quick commands to try:"
echo "   /help          - Show all commands"
echo "   /healthCheck   - Run system diagnostics"
echo "   /status        - Check TERMINATOR status"
echo "   /connectWeb    - Connect to web interface"
echo ""
echo "🎉 Enjoy your Universal TERMINATOR CLI!"
echo ""
