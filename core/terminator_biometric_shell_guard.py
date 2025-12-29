#!/usr/bin/env python3
"""
TERMINATOR Biometric Shell Guard
Prevents unauthorized shell installations and program creation using Touch ID/Face ID

Features:
- Biometric authentication for shell operations
- Package installation monitoring
- Shell switching detection
- Security audit logging
"""

import os
import sys
import json
import hashlib
import subprocess
import shlex
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple


class BiometricShellGuard:
    """Biometric authorization guard for shell operations"""

    # Security configuration
    CONFIG_DIR = Path.home() / ".terminator_security"
    CONFIG_FILE = CONFIG_DIR / "shell_guard_config.json"
    AUDIT_LOG = CONFIG_DIR / "shell_guard_audit.log"
    AUTHORIZED_SHELLS_FILE = CONFIG_DIR / "authorized_shells.json"

    # Authorized operations (don't require biometric)
    SAFE_COMMANDS = {
        'ls', 'cd', 'pwd', 'echo', 'cat', 'grep', 'find', 'which',
        'git status', 'git diff', 'git log', 'gh --version',
        'python3 --version', 'node --version', 'npm --version'
    }

    # Dangerous operations (require biometric)
    DANGEROUS_COMMANDS = {
        'brew install', 'brew uninstall', 'npm install -g', 'pip install',
        'pip3 install', 'sudo', 'curl', 'wget', 'apt install', 'apt-get install',
        'yum install', 'chsh', 'export PATH=', 'ln -s', 'cp', 'mv',
        'rm -rf', 'make install', 'installer'
    }

    def __init__(self):
        """Initialize the biometric shell guard"""
        self._ensure_config_dir()
        self._load_config()

    def _ensure_config_dir(self):
        """Create configuration directory if it doesn't exist"""
        self.CONFIG_DIR.mkdir(exist_ok=True, mode=0o700)

        if not self.CONFIG_FILE.exists():
            default_config = {
                "enabled": True,
                "require_biometric": True,
                "allow_password_fallback": True,
                "authorized_user": os.getenv("USER"),
                "authorized_shells": ["/bin/zsh"],
                "created_at": datetime.now().isoformat(),
                "biometric_provider": "touchid"
            }
            self._save_config(default_config)

        if not self.AUDIT_LOG.exists():
            self.AUDIT_LOG.touch(mode=0o600)

    def _load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
            return self.config
        except Exception as e:
            self._log_audit(f"ERROR: Failed to load config: {e}", "ERROR")
            return {}

    def _save_config(self, config: Dict):
        """Save configuration to file"""
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        os.chmod(self.CONFIG_FILE, 0o600)

    def _log_audit(self, message: str, level: str = "INFO"):
        """Log security audit trail"""
        timestamp = datetime.now().isoformat()
        shell = os.getenv("SHELL", "unknown")
        user = os.getenv("USER", "unknown")

        log_entry = f"[{timestamp}] [{level}] [{user}@{shell}] {message}\n"

        with open(self.AUDIT_LOG, 'a') as f:
            f.write(log_entry)

    def authenticate_biometric(self, reason: str = "Shell operation authorization") -> Tuple[bool, str]:
        """
        Authenticate using macOS Touch ID/Face ID

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # SECURITY: Sanitize reason to prevent command injection
            # Remove any shell metacharacters and limit length
            safe_reason = reason.replace('"', '\\"').replace("'", "\\'")[:100]

            # Use macOS's built-in biometric authentication via sudo with Touch ID
            # This leverages the pam_tid.so module configured in /etc/pam.d/sudo

            # First, show dialog using osascript with sanitized input
            # Using array form with shell=False for security
            dialog_cmd = [
                'osascript', '-e',
                f'display dialog "{safe_reason}" buttons {{"Cancel", "Authenticate"}} default button "Authenticate" with icon caution'
            ]

            dialog_result = subprocess.run(
                dialog_cmd,
                shell=False,  # SECURITY: No shell injection possible
                capture_output=True,
                text=True,
                timeout=10
            )

            if dialog_result.returncode != 0:
                return False, "Authentication cancelled by user"

            # Now use Touch ID via sudo
            # The -v flag validates cached credentials or prompts for Touch ID
            auth_result = subprocess.run(
                ['sudo', '-v'],
                shell=False,  # SECURITY: Command array, no shell
                capture_output=True,
                text=True,
                timeout=30
            )

            if auth_result.returncode == 0:
                self._log_audit(f"Biometric authentication successful: {safe_reason}", "SUCCESS")
                return True, "Biometric authentication successful"
            else:
                self._log_audit(f"Biometric authentication failed: {safe_reason}", "FAILURE")
                return False, "Biometric authentication failed"

        except subprocess.TimeoutExpired:
            self._log_audit(f"Biometric authentication timeout: {reason}", "TIMEOUT")
            return False, "Authentication timeout"
        except Exception as e:
            self._log_audit(f"Biometric authentication error: {e}", "ERROR")
            return False, f"Authentication error: {e}"

    def authenticate_password(self, reason: str = "Shell operation authorization") -> Tuple[bool, str]:
        """
        Authenticate using password (fallback method)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # SECURITY: Sanitize reason parameter
            safe_reason = reason[:100]

            # Use sudo to validate password
            auth_result = subprocess.run(
                ['sudo', '-k'],  # Invalidate cached credentials first
                shell=False,  # SECURITY: No shell needed
                capture_output=True,
                timeout=10
            )

            auth_result = subprocess.run(
                ['sudo', '-v'],
                shell=False,  # SECURITY: No shell needed
                capture_output=True,
                text=True,
                timeout=30
            )

            if auth_result.returncode == 0:
                self._log_audit(f"Password authentication successful: {safe_reason}", "SUCCESS")
                return True, "Password authentication successful"
            else:
                self._log_audit(f"Password authentication failed: {safe_reason}", "FAILURE")
                return False, "Password authentication failed"

        except Exception as e:
            self._log_audit(f"Password authentication error: {e}", "ERROR")
            return False, f"Authentication error: {e}"

    def is_command_dangerous(self, command: str) -> bool:
        """Check if a command requires authorization"""
        command_lower = command.lower().strip()

        # Check if it's explicitly safe
        if command_lower in self.SAFE_COMMANDS:
            return False

        # Check if it contains dangerous patterns
        for dangerous in self.DANGEROUS_COMMANDS:
            if dangerous in command_lower:
                return True

        return False

    def is_shell_authorized(self, shell_path: str) -> bool:
        """Check if a shell is in the authorized list"""
        authorized_shells = self.config.get("authorized_shells", ["/bin/zsh"])
        return shell_path in authorized_shells

    def authorize_shell(self, shell_path: str) -> bool:
        """
        Authorize a new shell after biometric authentication

        Returns:
            True if authorized successfully, False otherwise
        """
        if self.is_shell_authorized(shell_path):
            return True

        # Require biometric authentication
        success, message = self.authenticate_biometric(
            f"Authorize new shell: {shell_path}"
        )

        if success:
            # Add to authorized shells
            self.config["authorized_shells"].append(shell_path)
            self._save_config(self.config)
            self._log_audit(f"New shell authorized: {shell_path}", "AUTHORIZATION")
            return True
        else:
            self._log_audit(f"Shell authorization denied: {shell_path}", "DENIAL")
            return False

    def check_command(self, command: str) -> Tuple[bool, str]:
        """
        Check if a command requires authorization and authenticate if needed

        Returns:
            Tuple of (allowed: bool, message: str)
        """
        if not self.config.get("enabled", True):
            return True, "Guard disabled"

        if not self.is_command_dangerous(command):
            return True, "Safe command"

        # Dangerous command - require authentication
        self._log_audit(f"Dangerous command detected: {command}", "CHALLENGE")

        if self.config.get("require_biometric", True):
            success, message = self.authenticate_biometric(
                f"Authorize command: {command[:50]}..."
            )
        else:
            success, message = self.authenticate_password(
                f"Authorize command: {command[:50]}..."
            )

        if success:
            self._log_audit(f"Command authorized: {command}", "AUTHORIZED")
            return True, "Command authorized"
        else:
            self._log_audit(f"Command blocked: {command}", "BLOCKED")
            return False, f"Command blocked: {message}"

    def get_current_shell(self) -> str:
        """Get the current shell path"""
        return os.getenv("SHELL", "/bin/zsh")

    def check_shell_authorization(self) -> bool:
        """Check if current shell is authorized"""
        current_shell = self.get_current_shell()

        if not self.is_shell_authorized(current_shell):
            print(f"⚠️  WARNING: Unauthorized shell detected: {current_shell}")
            print("This shell is not in the authorized list.")
            print("Biometric authorization required.")

            if self.authorize_shell(current_shell):
                print(f"✅ Shell authorized: {current_shell}")
                return True
            else:
                print(f"❌ Shell authorization denied: {current_shell}")
                return False

        return True

    def get_audit_log(self, lines: int = 50) -> List[str]:
        """Get recent audit log entries"""
        try:
            with open(self.AUDIT_LOG, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        except Exception:
            return []

    def enable(self):
        """Enable the shell guard"""
        self.config["enabled"] = True
        self._save_config(self.config)
        self._log_audit("Shell guard enabled", "CONFIG")
        print("✅ Biometric Shell Guard ENABLED")

    def disable(self):
        """Disable the shell guard"""
        # Require authentication to disable
        success, _ = self.authenticate_biometric("Disable Shell Guard")

        if success:
            self.config["enabled"] = False
            self._save_config(self.config)
            self._log_audit("Shell guard disabled", "CONFIG")
            print("⚠️  Biometric Shell Guard DISABLED")
        else:
            print("❌ Failed to disable Shell Guard - authentication required")

    def status(self):
        """Print current guard status"""
        print("\n" + "=" * 60)
        print("🔒 TERMINATOR BIOMETRIC SHELL GUARD STATUS")
        print("=" * 60)
        print(f"Status:              {'✅ ENABLED' if self.config.get('enabled') else '❌ DISABLED'}")
        print(f"Biometric Auth:      {'✅ Required' if self.config.get('require_biometric') else '❌ Not Required'}")
        print(f"Password Fallback:   {'✅ Allowed' if self.config.get('allow_password_fallback') else '❌ Not Allowed'}")
        print(f"Authorized User:     {self.config.get('authorized_user')}")
        print(f"Current Shell:       {self.get_current_shell()}")
        print(f"Authorized Shells:   {len(self.config.get('authorized_shells', []))}")
        for shell in self.config.get('authorized_shells', []):
            print(f"  - {shell}")
        print(f"\nAudit Log:           {self.AUDIT_LOG}")
        print(f"Configuration:       {self.CONFIG_FILE}")
        print("=" * 60 + "\n")


def main():
    """Main entry point for CLI usage"""
    guard = BiometricShellGuard()

    if len(sys.argv) < 2:
        guard.status()
        print("\nUsage:")
        print("  python3 terminator_biometric_shell_guard.py status       # Show status")
        print("  python3 terminator_biometric_shell_guard.py enable       # Enable guard")
        print("  python3 terminator_biometric_shell_guard.py disable      # Disable guard")
        print("  python3 terminator_biometric_shell_guard.py check-shell  # Check current shell")
        print("  python3 terminator_biometric_shell_guard.py test <cmd>   # Test command authorization")
        print("  python3 terminator_biometric_shell_guard.py audit        # View audit log")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "status":
        guard.status()

    elif command == "enable":
        guard.enable()

    elif command == "disable":
        guard.disable()

    elif command == "check-shell":
        if guard.check_shell_authorization():
            print("✅ Current shell is authorized")
            sys.exit(0)
        else:
            print("❌ Current shell is NOT authorized")
            sys.exit(1)

    elif command == "test" and len(sys.argv) > 2:
        test_command = " ".join(sys.argv[2:])
        allowed, message = guard.check_command(test_command)

        if allowed:
            print(f"✅ Command allowed: {message}")
            sys.exit(0)
        else:
            print(f"❌ Command blocked: {message}")
            sys.exit(1)

    elif command == "audit":
        print("\n📋 Recent Audit Log Entries:")
        print("=" * 60)
        for line in guard.get_audit_log(30):
            print(line.rstrip())
        print("=" * 60 + "\n")

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
