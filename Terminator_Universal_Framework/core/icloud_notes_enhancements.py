# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR iCloud Notes Enhancement Module
Adds create, delete, list, and search functionality for Apple Notes (iCloud synced)
"""

import subprocess
from typing import Optional

def create_apple_note(title: str, content: str, folder: str = None) -> str:
    """
    Create a new note in Apple Notes (synced to iCloud if enabled).
    
    Args:
        title: Note title
        content: Note content/body text
        folder: Optional folder name (defaults to Notes)
    
    Returns:
        Success or error message
    """
    try:
        title = title.strip()
        content = content.strip()
        
        if not title or not content:
            return "❌ Error: Both title and content are required"
        
        # Escape special characters for AppleScript
        title_escaped = title.replace('"', '\\"')
        content_escaped = content.replace('"', '\\"')
        
        if folder:
            folder_escaped = folder.replace('"', '\\"')
            script = f"""
            tell application "Notes"
                activate
                set theFolder to folder "{folder_escaped}"
                tell theFolder
                    make new note with properties {{name:"{title_escaped}", body:"{content_escaped}"}}
                end tell
            end tell
            return "Note created successfully in {folder}"
            """
        else:
            script = f"""
            tell application "Notes"
                activate
                set theAccount to account "On My Mac"
                tell theAccount
                    make new note with properties {{name:"{title_escaped}", body:"{content_escaped}"}}
                end tell
            end tell
            return "Note created successfully"
            """
        
        result = subprocess.run(
            ["osascript", "-e", script], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            return f"✅ Successfully created note '{title}' in Apple Notes"
        else:
            error = result.stderr.strip()
            if "not permitted" in error.lower():
                return "⚠️ Permission denied. Grant Automation access in System Settings → Privacy & Security → Automation"
            return f"❌ Error creating note: {error}"
    
    except subprocess.TimeoutExpired:
        return "❌ Request timeout - Apple Notes took too long to respond"
    except Exception as e:
        return f"❌ Note creation error: {str(e)}"


def delete_apple_note(note_name: str, confirm: bool = True) -> str:
    """
    Delete a note from Apple Notes.
    
    Args:
        note_name: Name of the note to delete
        confirm: Whether to ask for confirmation (for safety)
    
    Returns:
        Success or error message
    """
    try:
        note_name = note_name.strip()
        
        if not note_name:
            return "❌ Error: Note name is required"
        
        if confirm:
            return f"⚠️ Confirm deletion of '{note_name}'? This action cannot be undone. Use: delete_apple_note('{note_name}', confirm=False) to proceed."
        
        # Escape special characters
        note_name_escaped = note_name.replace('"', '\\"')
        
        script = f"""
        tell application "Notes"
            activate
            set theNotes to notes whose name contains "{note_name_escaped}"
            if (count of theNotes) > 0 then
                set theNote to item 1 of theNotes
                delete theNote
                return "deleted"
            else
                return "not_found"
            end if
        end tell
        """
        
        result = subprocess.run(
            ["osascript", "-e", script], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            if "deleted" in response:
                return f"✅ Successfully deleted note '{note_name}' from Apple Notes"
            elif "not_found" in response:
                return f"❌ Note '{note_name}' not found in Apple Notes"
        
        error = result.stderr.strip()
        if "not permitted" in error.lower():
            return "⚠️ Permission denied. Grant Automation access in System Settings → Privacy & Security → Automation"
        return f"❌ Error deleting note: {error}"
    
    except subprocess.TimeoutExpired:
        return "❌ Request timeout - Apple Notes took too long to respond"
    except Exception as e:
        return f"❌ Note deletion error: {str(e)}"


def list_apple_notes(limit: int = 50) -> str:
    """
    List all notes in Apple Notes.
    
    Args:
        limit: Maximum number of notes to return
    
    Returns:
        Formatted list of notes
    """
    try:
        script = f"""
        tell application "Notes"
            activate
            set allNotes to every note
            set noteList to {{}}
            repeat with i from 1 to (count of allNotes)
                if i > {limit} then exit repeat
                set currentNote to item i of allNotes
                set noteList to noteList & (name of currentNote)
            end repeat
            return noteList as text
        end tell
        """
        
        result = subprocess.run(
            ["osascript", "-e", script], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            notes_output = result.stdout.strip()
            if notes_output:
                notes = notes_output.split(", ")
                formatted_list = "📝 **Notes in Apple Notes:**\n\n"
                for i, note in enumerate(notes, 1):
                    formatted_list += f"{i}. {note}\n"
                return formatted_list
            else:
                return "📝 No notes found in Apple Notes"
        else:
            error = result.stderr.strip()
            if "not permitted" in error.lower():
                return "⚠️ Permission denied. Grant Automation access in System Settings → Privacy & Security → Automation"
            return f"❌ Error listing notes: {error}"
    
    except subprocess.TimeoutExpired:
        return "❌ Request timeout - Apple Notes took too long to respond"
    except Exception as e:
        return f"❌ Note listing error: {str(e)}"


def search_apple_notes(query: str) -> str:
    """
    Search for notes in Apple Notes by title or content.
    
    Args:
        query: Search term
    
    Returns:
        Matching notes with content preview
    """
    try:
        query = query.strip()
        
        if not query:
            return "❌ Error: Search query is required"
        
        # Escape special characters
        query_escaped = query.replace('"', '\\"')
        
        script = f"""
        tell application "Notes"
            activate
            set searchResults to {{}}
            repeat with oneNote in every note
                set noteName to name of oneNote
                set noteBody to body of oneNote
                
                if noteName contains "{query_escaped}" or noteBody contains "{query_escaped}" then
                    set searchResults to searchResults & {{noteName}}
                end if
            end repeat
            return searchResults as text
        end tell
        """
        
        result = subprocess.run(
            ["osascript", "-e", script], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            notes_output = result.stdout.strip()
            if notes_output:
                notes = notes_output.split(", ")
                formatted_results = f"🔍 **Search Results for '{query}':**\n\n"
                for i, note in enumerate(notes, 1):
                    formatted_results += f"{i}. {note}\n"
                return formatted_results
            else:
                return f"🔍 No notes found matching '{query}'"
        else:
            error = result.stderr.strip()
            if "not permitted" in error.lower():
                return "⚠️ Permission denied. Grant Automation access in System Settings → Privacy & Security → Automation"
            return f"❌ Error searching notes: {error}"
    
    except subprocess.TimeoutExpired:
        return "❌ Request timeout - Apple Notes took too long to respond"
    except Exception as e:
        return f"❌ Note search error: {str(e)}"


def get_note_count() -> str:
    """Get total number of notes in Apple Notes."""
    try:
        script = """
        tell application "Notes"
            activate
            set noteCount to count of every note
            return noteCount as text
        end tell
        """
        
        result = subprocess.run(
            ["osascript", "-e", script], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            count = result.stdout.strip()
            return f"📊 Total notes in Apple Notes: {count}"
        else:
            return "❌ Could not retrieve note count"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Tool registration
icloud_notes_tools = {
    "create_apple_note": create_apple_note,
    "delete_apple_note": delete_apple_note,
    "list_apple_notes": list_apple_notes,
    "search_apple_notes": search_apple_notes,
    "get_note_count": get_note_count,
}

