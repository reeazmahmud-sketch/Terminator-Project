#!/bin/bash

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

# sign_module.sh - Automate LKM Signing for Secure AI Agents
# Usage: ./sign_module.sh <module_name.ko>

MODULE=$1

if [ -z "$MODULE" ]; then
    echo "Usage: $0 <module.ko>"
    exit 1
fi

KERNEL_BUILD="/lib/modules/$(uname -r)/build"
SIGN_FILE="$KERNEL_BUILD/scripts/sign-file"
KEY_DIR="./keys"

# 1. Check for signing utility
if [ ! -f "$SIGN_FILE" ]; then
    echo "❌ Error: scripts/sign-file not found in $KERNEL_BUILD."
    echo "   Ensure kernel headers are installed: sudo apt install linux-headers-$(uname -r)"
    exit 1
fi

# 2. Generate Keys if missing (Self-signed for dev/test)
mkdir -p "$KEY_DIR"
PRIV_KEY="$KEY_DIR/signing_key.pem"
PUB_KEY="$KEY_DIR/signing_key.x509"

if [ ! -f "$PRIV_KEY" ] || [ ! -f "$PUB_KEY" ]; then
    echo "🔐 Generating new signing keys..."
    openssl req -new -nodes -utf8 -sha512 -days 36500 -batch -x509 \
       -config x509.genkey -outform DER -out "$PUB_KEY" -keyout "$PRIV_KEY"
    echo "   ✅ Keys generated in $KEY_DIR"
else
    echo "ℹ️  Using existing keys from $KEY_DIR"
fi

# 3. Sign the Module
echo "✍️  Signing $MODULE..."
"$SIGN_FILE" sha512 "$PRIV_KEY" "$PUB_KEY" "$MODULE"

if [ $? -eq 0 ]; then
    echo "✅ Successfully signed $MODULE"
    echo "   Verify with: modinfo $MODULE | grep signer"
else
    echo "❌ Signing failed."
    exit 1
fi
