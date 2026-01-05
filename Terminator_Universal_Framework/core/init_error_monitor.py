#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Error Monitor Initialization Module
Automatically initializes and starts error monitoring when Terminator starts.

Import this in your main agent.py to enable automatic error monitoring.
"""

import os
import sys
import logging
from pathlib import Path

# Setup path
TERMINATOR_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(TERMINATOR_ROOT / "core"))
sys.path.insert(0, str(TERMINATOR_ROOT / "integrations"))

logger = logging.getLogger(__name__)


def initialize_error_monitor(verbose: bool = False) -> bool:
    """
    Initialize and start error monitoring for Terminator.

    Args:
        verbose: Print initialization details

    Returns:
        True if initialization successful, False otherwise
    """
    try:
        from terminator_error_monitor_integration import initialize_error_monitoring

        if verbose:
            print("🛡️  Initializing TERMINATOR Error Monitor Agent...")

        # Start monitoring
        integration = initialize_error_monitoring(auto_start=True)

        if verbose:
            print("✅ Error Monitor Agent initialized and running")
            print("   • Real-time error detection: ENABLED")
            print("   • Automatic remediation: ENABLED")
            print("   • Plugin management: ENABLED")
            print("   • System health monitoring: ENABLED")

        return True

    except ImportError as e:
        if verbose:
            print(f"⚠️  Could not import error monitor: {e}")
        logger.warning(f"Error monitor import failed: {e}")
        return False

    except Exception as e:
        if verbose:
            print(f"❌ Error monitor initialization failed: {e}")
        logger.error(f"Error monitor initialization failed: {e}")
        return False


def cleanup_error_monitor():
    """Stop error monitoring on shutdown."""
    try:
        from terminator_error_monitor_integration import get_integration
        integration = get_integration()
        integration.stop()
        logger.info("Error monitor stopped")
    except Exception as e:
        logger.debug(f"Error stopping monitor: {e}")


# Auto-initialize on import
_initialized = False

def auto_init():
    """Automatically initialize error monitor (called on import)."""
    global _initialized
    if not _initialized:
        _initialized = initialize_error_monitor(verbose=False)
        return _initialized
    return True


if __name__ == "__main__":
    # Test initialization
    success = initialize_error_monitor(verbose=True)
    sys.exit(0 if success else 1)
