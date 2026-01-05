import sys
import os
from pathlib import Path

# Add current dir to path
sys.path.insert(0, os.getcwd())

print("--- 🌍 Portability Verification ---")

try:
    from terminator_universal_cli import UniversalTerminatorCLI
    cli = UniversalTerminatorCLI()
    
    root = cli.terminator_root
    cwd = Path(os.getcwd()).resolve()
    
    print(f"Current Working Dir: {cwd}")
    print(f"CLI Detected Root:   {root}")
    
    # Check for hardcoded user path (simple heuristic)
    if "/Users/reeazmahmud/Desktop/Terminator-Project" in str(root) and str(root) != str(cwd):
        print("❌ FAILED: Path seems hardcoded to a specific location different from CWD")
    elif str(root) == str(cwd):
        print("✅ SUCCESS: Root matches current directory (Relative Resolution Works)")
    else:
        # If we run this script from the root, they should match
        print(f"⚠️  NOTE: Root is {root}, CWD is {cwd}. As long as Root is not hardcoded to an old path, this is fine.")

    # Check for modules
    if (root / "modules").exists():
        print("✅ SUCCESS: Found /modules directory relative to root")
    else:
        print("❌ FAILED: Could not find /modules using relative path")

except Exception as e:
    print(f"❌ ERROR: {e}")
