import os
from datetime import datetime

source_dir = "/Users/reeazmahmud/Desktop/Terminator-Project"
destinations = [
    "/Users/reeazmahmud/Desktop/Terminator-Project/terminator_filesystem_index.txt",
    "/Users/reeazmahmud/Desktop/B1ClaudeCode-CLI/terminator_filesystem_index.txt",
    "/Users/reeazmahmud/Desktop/B2Gemini-CLI/terminator_filesystem_index.txt"
]

ignore_dirs = {'.git', '__pycache__', '.DS_Store', 'venv', 'node_modules', '.vscode', '.idea'}

def generate_file_list(start_path):
    lines = [f"Terminator-Project File Index - Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "="*60, ""]
    
    for root, dirs, files in os.walk(start_path):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        lines.append(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in ignore_dirs:
                lines.append(f"{subindent}{f}")
                
    return "\n".join(lines)

try:
    print(f"Scanning {source_dir}...")
    content = generate_file_list(source_dir)
    
    for dest in destinations:
        try:
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Saved to: {dest}")
        except Exception as e:
            print(f"❌ Failed to save to {dest}: {e}")

except Exception as e:
    print(f"Critical Error: {e}")
