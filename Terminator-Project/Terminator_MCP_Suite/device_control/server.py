import subprocess
import os
from typing import Dict, Any

class DeviceControlMCP:
    """
    MCP Module for Controlling Devices (macOS, Android, IoT).
    """

    # --- macOS Control ---
    def macos_set_volume(self, level: int) -> str:
        """Set macOS system volume (0-100)."""
        cmd = f"set volume output volume {level}"
        try:
            subprocess.run(["osascript", "-e", cmd])
            return f"Volume set to {level}%"
        except Exception as e:
            return f"Error setting volume: {e}"

    def macos_say(self, text: str) -> str:
        """Make the Mac speak."""
        try:
            subprocess.run(["say", text])
            return "Spoken."
        except Exception as e:
            return f"Error speaking: {e}"

    # --- Android Control (ADB) ---
    def android_launch_app(self, package_name: str) -> str:
        """Launch an app on connected Android device via ADB."""
        try:
            subprocess.run(["adb", "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
            return f"Launched {package_name}"
        except Exception as e:
            return f"ADB Error: {e}"

    # --- IoT Control (Smart Home) ---
    def iot_control_light(self, device_name: str, state: str) -> str:
        """
        Control smart lights (Hue/SmartThings).
        State: 'on' or 'off'.
        """
        # This requires specific API integration (e.g., requests.post to Hue Bridge)
        # For now, we simulate the logic.
        valid_states = ["on", "off"]
        if state.lower() not in valid_states:
            return "Error: State must be 'on' or 'off'."
        
        return f"IoT: Turned {device_name} {state}. (API call simulated)"

    def iot_fridge_status(self) -> str:
        """Get status of Smart Fridge."""
        return "Fridge Status: Temp 3°C, Filter OK, Door Closed. (Simulated)"

# Tool Registry
tools = [
    DeviceControlMCP().macos_set_volume,
    DeviceControlMCP().macos_say,
    DeviceControlMCP().android_launch_app,
    DeviceControlMCP().iot_control_light,
    DeviceControlMCP().iot_fridge_status
]
