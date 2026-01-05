# TERMINATOR Biometric Shell Guard

## 🔒 Overview

The Biometric Shell Guard is a security system that prevents unauthorized shell installations and program creation by requiring Touch ID/Face ID or password authentication for dangerous operations.

## 🎯 What It Protects

### Protected Operations (Require Biometric Auth):
- **Package Installations**: `brew install`, `npm install -g`, `pip install`
- **Package Removals**: `brew uninstall`, `npm uninstall -g`, `pip uninstall`
- **Shell Changes**: `chsh` (change default shell)
- **Unauthorized Shells**: Starting `bash` or `sh` when `zsh` is your authorized shell
- **PATH Modifications**: Exporting new PATH variables
- **System Modifications**: `sudo`, file operations in system directories

### Safe Operations (No Auth Required):
- **Read-only commands**: `ls`, `cat`, `grep`, `find`, `which`
- **Version checks**: `brew --version`, `python3 --version`, `node --version`
- **Git operations**: `git status`, `git diff`, `git log`
- **Local package operations**: `npm install` (without -g), local pip installs

## 📦 Installation

### Quick Install (Recommended)

```bash
cd ~/Desktop/Terminator-Project
./scripts/install_shell_guard.sh
```

This will:
1. ✅ Configure Touch ID for sudo
2. ✅ Install shell command interceptors
3. ✅ Add hooks to `.zshrc` (and `.bashrc` if present)
4. ✅ Create security audit logging
5. ✅ Enable the guard automatically

### Manual Install

If you prefer to install manually:

1. **Make scripts executable:**
   ```bash
   chmod +x core/terminator_biometric_shell_guard.py
   chmod +x scripts/shell_guard_hooks.sh
   ```

2. **Add to your `.zshrc`:**
   ```bash
   # TERMINATOR Biometric Shell Guard
   if [[ -f "$HOME/Desktop/Terminator-Project/scripts/shell_guard_hooks.sh" ]]; then
       source "$HOME/Desktop/Terminator-Project/scripts/shell_guard_hooks.sh"
   fi
   ```

3. **Configure Touch ID (one-time):**
   ```bash
   sudo nano /etc/pam.d/sudo
   # Add this line at the top:
   # auth       sufficient     pam_tid.so
   ```

4. **Reload shell:**
   ```bash
   source ~/.zshrc
   ```

## 🚀 Usage

### Command Line Interface

```bash
# View status and configuration
shell-guard status

# Enable protection
shell-guard enable

# Disable protection (requires biometric auth)
shell-guard disable

# Test if a command would be blocked
shell-guard test "brew install wget"

# View security audit log
shell-guard audit
```

### Direct Python Usage

```bash
# View status
python3 core/terminator_biometric_shell_guard.py status

# Check current shell authorization
python3 core/terminator_biometric_shell_guard.py check-shell

# View audit log
python3 core/terminator_biometric_shell_guard.py audit
```

## 🔐 How It Works

### 1. Command Interception

When you run a dangerous command:
```bash
$ brew install wget
🔒 Biometric authorization required for: brew install wget
[Touch ID prompt appears]
✅ Authorized - executing: brew install wget
```

### 2. Shell Detection

When you try to start an unauthorized shell:
```bash
$ bash
⚠️  Starting bash shell - checking authorization...
[Touch ID prompt appears]
✅ Bash shell authorized
[bash starts]
```

Or if denied:
```bash
$ bash
⚠️  Starting bash shell - checking authorization...
❌ BLOCKED: Unauthorized shell - bash
   Your authorized shell is: /bin/zsh
```

### 3. Biometric Authentication

The system uses macOS's native Touch ID via the PAM (Pluggable Authentication Module) system:

1. **Touch ID First**: Prompts for fingerprint
2. **Password Fallback**: If Touch ID fails or is unavailable
3. **Timeout**: 30-second authentication window
4. **Caching**: sudo credentials cached for 5 minutes (macOS default)

### 4. Audit Logging

All security events are logged to `~/.terminator_security/shell_guard_audit.log`:

```
[2025-12-26T10:30:15] [CHALLENGE] [reeazmahmud@/bin/zsh] Dangerous command detected: brew install wget
[2025-12-26T10:30:18] [SUCCESS] [reeazmahmud@/bin/zsh] Biometric authentication successful: Authorize command: brew install wget
[2025-12-26T10:30:18] [AUTHORIZED] [reeazmahmud@/bin/zsh] Command authorized: brew install wget
```

## ⚙️ Configuration

Configuration file: `~/.terminator_security/shell_guard_config.json`

```json
{
  "enabled": true,
  "require_biometric": true,
  "allow_password_fallback": true,
  "authorized_user": "reeazmahmud",
  "authorized_shells": ["/bin/zsh"],
  "created_at": "2025-12-26T10:00:00",
  "biometric_provider": "touchid"
}
```

### Configuration Options

- **`enabled`**: Master switch for the guard (true/false)
- **`require_biometric`**: Require Touch ID (vs just password) (true/false)
- **`allow_password_fallback`**: Allow password if Touch ID fails (true/false)
- **`authorized_user`**: Username that owns this configuration
- **`authorized_shells`**: List of shells that don't require challenge
- **`biometric_provider`**: Always "touchid" on macOS

## 🛡️ Security Features

### Multi-Layer Protection

1. **Command-Level**: Intercepts dangerous commands before execution
2. **Shell-Level**: Detects and challenges unauthorized shell switching
3. **Install-Level**: Blocks package installations without auth
4. **Audit-Level**: Logs all security events for review

### Threat Protection

| Threat | Protection | How |
|--------|-----------|-----|
| Accidental wrong shell | ✅ Blocked | Detects shell switch, requires auth |
| Malicious script install | ✅ Blocked | Intercepts `brew/npm/pip install` |
| Shell configuration hijack | ✅ Logged | Monitors PATH changes |
| Unauthorized user access | ✅ Blocked | Biometric auth per user |
| Privilege escalation | ✅ Logged | All sudo usage audited |

### Privacy & Security

- **Local Only**: All data stays on your Mac
- **Encrypted Logs**: Audit logs protected with file permissions (0600)
- **No Network**: Never transmits biometric data
- **User-Controlled**: Can be disabled (with auth)

## 📊 Monitoring & Auditing

### View Recent Activity

```bash
shell-guard audit
```

Example output:
```
📋 Recent Audit Log Entries:
============================================================
[2025-12-26T10:30:15] [CHALLENGE] [reeazmahmud@/bin/zsh] Dangerous command detected: brew install wget
[2025-12-26T10:30:18] [SUCCESS] [reeazmahmud@/bin/zsh] Biometric authentication successful
[2025-12-26T10:30:18] [AUTHORIZED] [reeazmahmud@/bin/zsh] Command authorized: brew install wget
[2025-12-26T10:35:22] [CHALLENGE] [reeazmahmud@/bin/zsh] Dangerous command detected: chsh -s /bin/bash
[2025-12-26T10:35:24] [FAILURE] [reeazmahmud@/bin/zsh] Biometric authentication failed
[2025-12-26T10:35:24] [BLOCKED] [reeazmahmud@/bin/zsh] Command blocked: chsh -s /bin/bash
============================================================
```

### Log Levels

- **CHALLENGE**: Dangerous operation detected
- **SUCCESS**: Authentication successful
- **FAILURE**: Authentication failed
- **AUTHORIZED**: Command allowed to proceed
- **BLOCKED**: Command prevented
- **AUTHORIZATION**: New shell/tool authorized
- **DENIAL**: Authorization denied
- **CONFIG**: Configuration change
- **ERROR**: System error

## 🔧 Troubleshooting

### Touch ID Not Working

**Problem**: Authentication falls back to password every time

**Solutions**:
1. Check if Touch ID is enabled:
   ```bash
   System Settings → Touch ID & Password
   ```

2. Verify PAM configuration:
   ```bash
   grep pam_tid.so /etc/pam.d/sudo
   ```
   Should show: `auth       sufficient     pam_tid.so`

3. Restart terminal after PAM changes

### Commands Still Not Protected

**Problem**: Can run `brew install` without authentication

**Solutions**:
1. Check if guard is enabled:
   ```bash
   shell-guard status
   ```

2. Verify hooks are loaded:
   ```bash
   type brew
   # Should show: brew is a function
   ```

3. Reload shell:
   ```bash
   source ~/.zshrc
   ```

### False Positives

**Problem**: Safe commands being blocked

**Solutions**:
1. Check the audit log:
   ```bash
   shell-guard audit
   ```

2. Whitelist the command in `terminator_biometric_shell_guard.py`:
   ```python
   SAFE_COMMANDS = {
       'your-safe-command',
       # ... other safe commands
   }
   ```

### Permission Denied Errors

**Problem**: "Permission denied" when running guard

**Solutions**:
1. Make scripts executable:
   ```bash
   chmod +x core/terminator_biometric_shell_guard.py
   chmod +x scripts/shell_guard_hooks.sh
   ```

2. Check file ownership:
   ```bash
   ls -l ~/.terminator_security/
   ```
   Should be owned by your user

## 🎓 Advanced Usage

### Adding Custom Authorized Shells

```bash
# Edit config manually
nano ~/.terminator_security/shell_guard_config.json

# Add to authorized_shells array:
"authorized_shells": [
    "/bin/zsh",
    "/bin/bash",          # Add this
    "/usr/local/bin/fish"  # Or this
]
```

Or authorize interactively:
```bash
# Start the new shell - will prompt for auth and add to list
bash
[Touch ID prompt]
✅ Bash shell authorized
```

### Customizing Protected Commands

Edit `core/terminator_biometric_shell_guard.py`:

```python
# Add to DANGEROUS_COMMANDS:
DANGEROUS_COMMANDS = {
    'brew install',
    'your-custom-command',  # Add this
    # ... other commands
}

# Add to SAFE_COMMANDS:
SAFE_COMMANDS = {
    'ls',
    'your-safe-command',  # Add this
    # ... other commands
}
```

### Temporary Disable

```bash
# Disable (requires auth)
shell-guard disable

# Do unprotected work...
brew install wget
npm install -g typescript

# Re-enable
shell-guard enable
```

### Integration with Scripts

```python
#!/usr/bin/env python3
from core.terminator_biometric_shell_guard import BiometricShellGuard

guard = BiometricShellGuard()

# Check if command is safe
allowed, message = guard.check_command("brew install wget")
if allowed:
    # Execute command
    pass
else:
    print(f"Blocked: {message}")
```

## 📈 Best Practices

### 1. Regular Audit Reviews
```bash
# Weekly audit review
shell-guard audit | grep BLOCKED
```

### 2. Keep Authorized Shells Minimal
- Only authorize shells you actually use
- Remove unused shells from config

### 3. Enable for All Users (Optional)
```bash
# System-wide installation (admin only)
sudo cp scripts/shell_guard_hooks.sh /etc/profile.d/
```

### 4. Backup Configuration
```bash
# Backup security config
cp -r ~/.terminator_security ~/.terminator_security.backup
```

### 5. Monitor for Anomalies
```bash
# Check for unusual activity
shell-guard audit | grep -E "BLOCKED|FAILURE"
```

## 🔄 Uninstallation

If you need to remove the shell guard:

```bash
# 1. Disable the guard
shell-guard disable

# 2. Remove from .zshrc
nano ~/.zshrc
# Delete lines between "# TERMINATOR Biometric Shell Guard" markers

# 3. Remove from .bashrc (if present)
nano ~/.bashrc

# 4. Remove configuration (optional)
rm -rf ~/.terminator_security

# 5. Reload shell
source ~/.zshrc
```

## 🆘 Support

- **Audit Logs**: `~/.terminator_security/shell_guard_audit.log`
- **Configuration**: `~/.terminator_security/shell_guard_config.json`
- **Issues**: Check TERMINATOR project documentation

## 📄 License

Part of the TERMINATOR project. See main project README for license information.

---

**Security Notice**: This guard is designed to protect against accidental or automated unauthorized installations. It is not a replacement for proper system security practices. Always keep your system updated and use strong authentication.
