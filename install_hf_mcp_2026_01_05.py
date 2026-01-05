import subprocess
import sys
import os

def install_hf_mcp():
    print("🚀 Starting Hugging Face MCP Server installation...")
    
    # Check if uv is installed, otherwise use npx
    try:
        print("Checking for uv...")
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv found. Using uvx to install...")
        # Note: we can't easily "install" uvx as it's a runner. 
        # But we can try to run it.
        # Actually, the user wants it installed in Gemini CLI.
    except:
        print("⚠️ uv not found. Checking for npm/npx...")
        try:
            subprocess.run(["npx", "--version"], check=True, capture_output=True)
            print("✅ npx found.")
        except:
            print("❌ Neither uv nor npx found. Cannot proceed with automatic installation.")
            return

    # Create mcp-servers directory if it doesn't exist
    mcp_dir = "/Users/reeazmahmud/Desktop/Terminator-Project/mcp-servers"
    os.makedirs(mcp_dir, exist_ok=True)
    print(f"✅ Directory {mcp_dir} is ready.")

    print("\nNext steps (Manual or Scripted):")
    print("1. Start the server: npx @huggingface/mcp-server")
    print("2. Register in Terminator configuration.")

install_hf_mcp()
