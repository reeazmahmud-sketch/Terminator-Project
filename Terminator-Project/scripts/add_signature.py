import os
from datetime import datetime

SIGNATURE_TEXT = """Terminator Universal Framework
Architect: Reeaz Mahmud | AI Partner: Gemini
Date: December 17, 2025"""

COMMENT_STYLES = {
    ".py": ("#", ""),
    ".sh": ("#", ""),
    ".yaml": ("#", ""),
    ".yml": ("#", ""),
    ".c": ("/*", " */"),
    ".h": ("/*", " */"),
    ".swift": ("//", ""),
    ".tsx": ("//", ""),
    ".ts": ("//", ""),
    ".js": ("//", ""),
    ".md": ("<!--", "-->")
}

TARGET_DIR = "Terminator_Universal_Framework"

def get_comment_block(style):
    start, end = style
    lines = SIGNATURE_TEXT.split('\n')
    if start == "/*":
        comment = "/*\n"
        for line in lines:
            comment += f" * {line}\n"
        comment += " */\n\n"
    elif start == "<!--":
        comment = "<!--\n"
        for line in lines:
            comment += f"  {line}\n"
        comment += "-->\n\n"
    else:
        comment = ""
        for line in lines:
            comment += f"{start} {line}\n"
        comment += "\n"
    return comment

def process_file(filepath):
    ext = os.path.splitext(filepath)[1]
    if ext not in COMMENT_STYLES:
        return

    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Avoid double signing
        if "Architect: Reeaz Mahmud" in content:
            return

        style = COMMENT_STYLES[ext]
        header = get_comment_block(style)
        
        # Handle shebangs for scripts
        if content.startswith("#!"):
            lines = content.split('\n')
            new_content = lines[0] + '\n\n' + header + '\n'.join(lines[1:])
        else:
            new_content = header + content

        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Signed: {filepath}")
    except Exception as e:
        print(f"Skipped {filepath}: {e}")

def main():
    print(f"Signing files in {TARGET_DIR}...")
    for root, dirs, files in os.walk(TARGET_DIR):
        if "venv" in root or "__pycache__" in root:
            continue
        for file in files:
            process_file(os.path.join(root, file))
    print("Done.")

if __name__ == "__main__":
    main()
