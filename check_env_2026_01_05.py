import shutil
import subprocess
import os

def check_command(cmd):
    path = shutil.which(cmd)
    if path:
        print(f"Command '{cmd}' found at: {path}")
        try:
            result = subprocess.run([cmd, "--help"], capture_output=True, text=True, timeout=5)
            print(f"Help output for '{cmd}':\n{result.stdout[:500]}")
        except Exception as e:
            print(f"Error running '{cmd} --help': {e}")
    else:
        print(f"Command '{cmd}' not found.")

check_command("gemini")
check_command("terminator")
print(f"Current working directory: {os.getcwd()}")

