import os
import shutil
import zipfile
import subprocess
from typing import List, Optional

class FileSystemMCP:
    """
    MCP Module for Advanced File System Operations.
    Target OS: macOS/Linux (compatible with Windows via pathlib).
    """
    
    def move_file(self, source: str, dest: str, overwrite: bool = False) -> str:
        """Move a file or directory."""
        if not os.path.exists(source):
            return f"Error: Source '{source}' not found."
        
        if os.path.exists(dest) and not overwrite:
            return f"Error: Destination '{dest}' exists. Set overwrite=True to force."
            
try:
            shutil.move(source, dest)
            return f"Successfully moved '{source}' to '{dest}'."
        except Exception as e:
            return f"Error moving file: {e}"

    def archive_files(self, sources: List[str], archive_name: str) -> str:
        """Create a ZIP archive from a list of files/folders."""
        try:
            with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for src in sources:
                    if os.path.isdir(src):
                        for root, _, files in os.walk(src):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.path.dirname(src))
                                zipf.write(file_path, arcname)
                    else:
                        zipf.write(src, os.path.basename(src))
            return f"Archive '{archive_name}' created successfully."
        except Exception as e:
            return f"Error creating archive: {e}"

    def sync_to_cloud(self, source: str, provider: str = "gdrive") -> str:
        """
        Sync files to cloud storage (Requires rclone).
        Supports: icloud, gdrive, dropbox.
        """
        # Placeholder for rclone command
        # cmd = ["rclone", "sync", source, f"{provider}:/Backups/{os.path.basename(source)}"]
        
        if provider not in ["gdrive", "icloud", "dropbox"]:
            return "Error: Unsupported provider. Use 'gdrive', 'icloud', or 'dropbox'."
            
        # Simulation
        return f"Synced '{source}' to {provider} (Simulated rclone execution)."

    def list_files(self, path: str) -> str:
        """List files in a directory."""
        try:
            items = os.listdir(path)
            return "\n".join(items)
        except Exception as e:
            return f"Error listing directory: {e}"

# Tool Registry for MCP
tools = [
    FileSystemMCP().move_file,
    FileSystemMCP().archive_files,
    FileSystemMCP().sync_to_cloud,
    FileSystemMCP().list_files
]
