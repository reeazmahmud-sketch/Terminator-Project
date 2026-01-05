import os
import subprocess
import socket
import time

def restart_ollama_server():
    """
    This script automates the process of freeing up port 11434 
    and starting the Ollama server.
    """
    port = 11434
    
    # Block 1: Check if the port is already in use
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('127.0.0.1', port))
        
    if result == 0:
        print(f"Port {port} is busy. Cleaning up existing process...")
        # Block 2: Identify and kill the process using the port
        try:
            # lsof -t -i:11434 returns only the PID (Process ID)
            pid = subprocess.check_output(["lsof", "-t", f"-i:{port}"]).decode().strip()
            if pid:
                # If multiple processes are found, split and kill each
                for p in pid.split('\n'):
                    os.system(f"kill -9 {p}")
                print(f"Successfully killed process(es): {pid}")
                time.sleep(1) # Brief pause to allow the port to clear
        except subprocess.CalledProcessError:
            print("Could not find PID, but port is reported as busy.")

    # Block 3: Start the Ollama server
    print("Starting Ollama serve...")
    try:
        # Using subprocess.run to keep the server output in your terminal
        subprocess.run(["ollama", "serve"])
    except KeyboardInterrupt:
        print("\nOllama server stopped.")

if __name__ == "__main__":
    restart_ollama_server()
