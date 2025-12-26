#!/usr/bin/env python3
"""
TERMINATOR Claude Config Guardian Agent

Automatically detects and fixes Claude Code configuration errors
before they cause startup failures.

Run manually: python3 core/terminator_claude_config_guardian.py
Auto-run: Add to shell profile or pre-launch hook
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class ClaudeConfigGuardian:
    """Validates and auto-fixes Claude Code configuration files."""

    # Known permission pattern fixes
    PERMISSION_FIXES = {
        # Wrong pattern -> Correct pattern
        r'Bash\(([^:)]+)\s+\*\)': r'Bash(\1:*)',  # "Bash(git push *)" -> "Bash(git push:*)"
        r'Bash\(([^:)]+)\*\)': r'Bash(\1:*)',     # "Bash(git push*)" -> "Bash(git push:*)"
    }

    # Valid permission pattern examples
    VALID_PATTERNS = [
        "Bash(git status)",           # Exact command
        "Bash(git:*)",                # Prefix match with colon
        "Bash(npm run:*)",            # Prefix match
        "Read",                       # Tool without args
        "Read(*)",                    # Tool with wildcard
        "Read(./src/**)",             # Tool with glob
        "Glob(*)",                    # Glob tool
        "Grep(*)",                    # Grep tool
        "WebFetch(domain:github.com)" # Domain filter
    ]

    def __init__(self, project_path: Optional[str] = None):
        """Initialize with project path or auto-detect."""
        if project_path:
            self.project_path = Path(project_path)
        else:
            # Try current directory, then common locations
            self.project_path = self._find_project_path()

        self.settings_path = self.project_path / ".claude" / "settings.json"
        self.errors_found: List[str] = []
        self.fixes_applied: List[str] = []

    def _find_project_path(self) -> Path:
        """Find project path by looking for .claude directory."""
        # Check current directory
        cwd = Path.cwd()
        if (cwd / ".claude").exists():
            return cwd

        # Check parent directories
        for parent in cwd.parents:
            if (parent / ".claude").exists():
                return parent

        # Default to current directory
        return cwd

    def validate_settings(self) -> Tuple[bool, List[str]]:
        """Validate settings.json and return (is_valid, errors)."""
        errors = []

        if not self.settings_path.exists():
            return True, []  # No settings file is valid

        try:
            with open(self.settings_path, 'r') as f:
                content = f.read()
                settings = json.loads(content)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return False, errors

        # Check permissions
        permissions = settings.get("permissions", {})
        allow_list = permissions.get("allow", [])
        deny_list = permissions.get("deny", [])

        for perm in allow_list + deny_list:
            if not self._is_valid_permission(perm):
                error = self._get_permission_error(perm)
                if error:
                    errors.append(error)

        self.errors_found = errors
        return len(errors) == 0, errors

    def _is_valid_permission(self, perm: str) -> bool:
        """Check if a permission pattern is valid."""
        # Check for common invalid patterns

        # Pattern: "Bash(command *)" should be "Bash(command:*)"
        if re.match(r'Bash\([^:)]+\s+\*\)', perm):
            return False

        # Pattern: "Bash(command*)" without colon
        if re.match(r'Bash\([^:)]+\*\)$', perm) and ':*' not in perm:
            return False

        return True

    def _get_permission_error(self, perm: str) -> Optional[str]:
        """Get specific error message for invalid permission."""
        if re.match(r'Bash\(([^:)]+)\s+\*\)', perm):
            match = re.match(r'Bash\(([^:)]+)\s+\*\)', perm)
            cmd = match.group(1) if match else "command"
            return f'"{perm}": Use ":*" for prefix matching. Change to "Bash({cmd}:*)"'

        if re.match(r'Bash\(([^:)]+)\*\)$', perm) and ':*' not in perm:
            match = re.match(r'Bash\(([^:)]+)\*\)', perm)
            cmd = match.group(1) if match else "command"
            return f'"{perm}": Missing colon before *. Change to "Bash({cmd}:*)"'

        return None

    def fix_settings(self, dry_run: bool = False) -> Tuple[bool, List[str]]:
        """Fix known issues in settings.json. Returns (success, fixes_applied)."""
        fixes = []

        if not self.settings_path.exists():
            return True, []

        try:
            with open(self.settings_path, 'r') as f:
                content = f.read()
                original_content = content
        except Exception as e:
            return False, [f"Failed to read file: {e}"]

        # Apply regex fixes
        for pattern, replacement in self.PERMISSION_FIXES.items():
            matches = re.findall(pattern, content)
            if matches:
                for match in matches:
                    old = re.search(pattern, content).group(0)
                    new = re.sub(pattern, replacement, old)
                    fixes.append(f'Fixed: "{old}" -> "{new}"')
                content = re.sub(pattern, replacement, content)

        # Validate the fixed JSON
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            return False, [f"Fix resulted in invalid JSON: {e}"]

        if content != original_content and not dry_run:
            # Backup original
            backup_path = self.settings_path.with_suffix('.json.backup')
            with open(backup_path, 'w') as f:
                f.write(original_content)

            # Write fixed content
            with open(self.settings_path, 'w') as f:
                f.write(content)

            fixes.append(f"Backup saved to: {backup_path}")

        self.fixes_applied = fixes
        return True, fixes

    def run_guardian(self, auto_fix: bool = True) -> Dict:
        """Run full validation and optional auto-fix."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "settings_path": str(self.settings_path),
            "valid": False,
            "errors": [],
            "fixes_applied": [],
            "status": "unknown"
        }

        # First validation
        is_valid, errors = self.validate_settings()

        if is_valid:
            result["valid"] = True
            result["status"] = "healthy"
            return result

        result["errors"] = errors

        if auto_fix:
            success, fixes = self.fix_settings()
            result["fixes_applied"] = fixes

            if success and fixes:
                # Re-validate after fix
                is_valid, remaining_errors = self.validate_settings()
                result["valid"] = is_valid
                result["errors"] = remaining_errors
                result["status"] = "fixed" if is_valid else "partially_fixed"
            else:
                result["status"] = "fix_failed"
        else:
            result["status"] = "errors_found"

        return result

    def print_report(self, result: Dict) -> None:
        """Print a human-readable report."""
        print("\n" + "=" * 60)
        print("   CLAUDE CONFIG GUARDIAN REPORT")
        print("=" * 60)
        print(f"\nSettings: {result['settings_path']}")
        print(f"Status:   {result['status'].upper()}")

        if result['errors']:
            print(f"\n{'⚠️  ERRORS FOUND:' if result['status'] != 'fixed' else '📋 ERRORS FIXED:'}")
            for error in result['errors']:
                print(f"  • {error}")

        if result['fixes_applied']:
            print(f"\n✅ FIXES APPLIED:")
            for fix in result['fixes_applied']:
                print(f"  • {fix}")

        if result['valid']:
            print("\n✅ Configuration is valid - Claude Code should start normally")
        else:
            print("\n❌ Configuration has issues - manual review may be needed")
            print("\nValid permission pattern examples:")
            for pattern in self.VALID_PATTERNS[:5]:
                print(f"  • {pattern}")

        print("\n" + "=" * 60 + "\n")


def scan_all_projects(base_path: str = None) -> List[Dict]:
    """Scan all projects in Desktop for Claude config issues."""
    if base_path is None:
        base_path = os.path.expanduser("~/Desktop")

    results = []
    base = Path(base_path)

    for project_dir in base.iterdir():
        if project_dir.is_dir():
            claude_dir = project_dir / ".claude"
            if claude_dir.exists():
                guardian = ClaudeConfigGuardian(str(project_dir))
                result = guardian.run_guardian(auto_fix=True)
                result["project"] = project_dir.name
                results.append(result)

    return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude Config Guardian - Validate and fix Claude Code settings"
    )
    parser.add_argument(
        "--path", "-p",
        help="Project path (default: auto-detect)"
    )
    parser.add_argument(
        "--scan-all", "-a",
        action="store_true",
        help="Scan all projects in ~/Desktop"
    )
    parser.add_argument(
        "--no-fix",
        action="store_true",
        help="Only report errors, don't auto-fix"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output if errors found"
    )

    args = parser.parse_args()

    if args.scan_all:
        print("\n🔍 Scanning all projects for Claude config issues...\n")
        results = scan_all_projects()

        issues_found = False
        for result in results:
            if not result["valid"] or result["fixes_applied"]:
                issues_found = True
                print(f"📁 {result['project']}: {result['status']}")
                if result["fixes_applied"]:
                    for fix in result["fixes_applied"]:
                        print(f"   ✅ {fix}")

        if not issues_found:
            print("✅ All projects have valid Claude configurations!")
    else:
        guardian = ClaudeConfigGuardian(args.path)
        result = guardian.run_guardian(auto_fix=not args.no_fix)

        if not args.quiet or not result["valid"]:
            guardian.print_report(result)

        # Exit with error code if invalid
        exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
