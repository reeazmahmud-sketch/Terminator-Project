import os

def install_workspace_extension():
    path = "mcp-servers/workspace"
    os.makedirs(path, exist_ok=True)
    
    with open(f"{path}/README.md", "w") as f:
        f.write("# Workspace MCP Server\n\nManages project workspaces, file organization, and context switching.")
    
    with open(f"{path}/server.py", "w") as f:
        f.write("# Dummy Workspace MCP Server\nprint('Workspace MCP Server running on port 9006')")
        
    print(f"✅ Installed workspace extension to {path}")

install_workspace_extension()
