#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
LangChain Agent with Ollama - Web Search & File Access
Phase 1: Core AI Assistant (Updated for Python 3.14+)
With Intelligent Multi-Model Selection
"""

import json
import os
import subprocess
import time

from langchain_ollama import OllamaLLM

# Import Terminator Model Manager
try:
    from terminator_model_manager import TerminatorModelManager, TaskType

    MODEL_MANAGER_AVAILABLE = True
except ImportError:
    MODEL_MANAGER_AVAILABLE = False
    print("⚠️  Model Manager not available. Using default model selection.")

# DuckDuckGo search (package renamed from duckduckgo_search to ddgs)
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

# YouTube search with fallback
try:
    import yt_dlp

    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

try:
    from youtubesearchpython import VideosSearch

    YOUTUBE_SEARCH_AVAILABLE = True
except ImportError:
    YOUTUBE_SEARCH_AVAILABLE = False

# Translation support
try:
    from deep_translator import GoogleTranslator

    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False

# === TOOLS ===


def web_search(query: str) -> str:
    """Search the internet for current information using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "No results found."

            output = []
            for i, r in enumerate(results, 1):
                output.append(
                    f"{i}. {r['title']}\n   {r['href']}\n   {r['body'][:200]}..."
                )
            return "\n\n".join(output)
    except Exception as e:
        return f"Search error: {str(e)}"


def file_search(query: str) -> str:
    """Search for files on macOS using Spotlight. Input: filename or content keywords."""
    try:
        # Use mdfind for Spotlight search
        result = subprocess.run(
            ["mdfind", query], capture_output=True, text=True, timeout=10
        )

        files = result.stdout.strip().split("\n")[:10]  # Limit to 10 results

        if not files or files == [""]:
            return f"No files found matching: {query}"

        output = [f"Found {len(files)} files:"]
        for f in files:
            output.append(f"  • {f}")
        return "\n".join(output)
    except Exception as e:
        return f"File search error: {str(e)}"


def read_file(filepath: str) -> str:
    """Read the contents of a file. Input: full file path."""
    try:
        filepath = filepath.strip()
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(10000)  # Limit to 10k chars
            if len(content) == 10000:
                content += "\n... [truncated]"
            return content
    except Exception as e:
        return f"Read error: {str(e)}"


def list_directory(path: str) -> str:
    """List files and folders in a directory. Input: directory path."""
    try:
        path = path.strip() or os.getcwd()
        if not os.path.isdir(path):
            return f"Not a directory: {path}"

        items = os.listdir(path)
        dirs = [d for d in items if os.path.isdir(os.path.join(path, d))]
        files = [f for f in items if os.path.isfile(os.path.join(path, f))]

        output = [f"Directory: {path}\n"]
        if dirs:
            output.append("Folders:")
            for d in sorted(dirs)[:20]:
                output.append(f"  📁 {d}")
        if files:
            output.append("Files:")
            for f in sorted(files)[:20]:
                output.append(f"  📄 {f}")
        return "\n".join(output)
    except Exception as e:
        return f"Directory error: {str(e)}"


def translate_to_bengali(text: str) -> str:
    """Translate text to Bengali. Input: English text."""
    try:
        if not TRANSLATION_AVAILABLE:
            return "Translation not available. Install: pip install deep-translator"

        translator = GoogleTranslator(source="en", target="bn")
        bengali_text = translator.translate(text)

        return f"Bengali Translation:\n{bengali_text}"
    except Exception as e:
        return f"Translation error: {str(e)}"


def create_folder_structure(subject: str) -> str:
    """Create organized folder structure based on subject. Input: subject/category name."""
    try:
        subject = subject.strip().replace(" ", "_").lower()

        # Safe directory - only create in user's Downloads or Documents
        home = os.path.expanduser("~")
        base_path = os.path.join(home, "Downloads", subject)

        # Prevent directory traversal attacks
        if not os.path.abspath(base_path).startswith(os.path.abspath(home)):
            return f"Error: Can only create folders in home directory"

        # Create main folder
        os.makedirs(base_path, exist_ok=True)

        # Create sub-folders based on category
        subfolders = {
            "AI": ["models", "datasets", "research"],
            "programming": ["python", "javascript", "java", "documentation"],
            "python": ["projects", "libraries", "scripts"],
            "web": ["frontend", "backend", "fullstack"],
            "design": ["ui", "ux", "graphics"],
            "project": ["docs", "code", "assets", "tests"],
            "learning": ["courses", "tutorials", "notes"],
            "media": ["videos", "images", "audio"],
        }

        # Find matching subfolders
        matching_folders = subfolders.get(subject, ["documents", "resources"])

        created = [f"📁 {subject}/"]
        for subfolder in matching_folders:
            subfolder_path = os.path.join(base_path, subfolder)
            os.makedirs(subfolder_path, exist_ok=True)
            created.append(f"   📂 {subfolder}/")

        return f"✅ Created folder structure in ~/Downloads/{subject}:\n" + "\n".join(
            created
        )
    except Exception as e:
        return f"Folder creation error: {str(e)}"


def youtube_search(query: str) -> str:
    """Search YouTube for videos. Input: video search query."""
    try:
        # Use yt-dlp for YouTube search if available
        if YTDLP_AVAILABLE:
            try:
                ydl = yt_dlp.YoutubeDL(
                    {
                        "quiet": True,
                        "no_warnings": True,
                        "extract_flat": "in_playlist",
                        "skip_download": True,
                    }
                )

                search_query = f"ytsearch5:{query}"
                info = ydl.extract_info(search_query, download=False)

                if not info or "entries" not in info or not info["entries"]:
                    # Fallback to web search if no results
                    return web_search(query)

                output = [f"Found YouTube videos for '{query}':\n"]
                for i, video in enumerate(info["entries"][:5], 1):
                    title = video.get("title", "No title")
                    video_id = video.get("id", "")
                    channel = video.get("uploader", "Unknown channel")
                    url = f"https://www.youtube.com/watch?v={video_id}"

                    output.append(f"{i}. {title}")
                    output.append(f"   Channel: {channel}")
                    output.append(f"   Link: {url}\n")

                return "\n".join(output)
            except Exception as e:
                # Fallback to web search
                return web_search(query)
        else:
            # Fallback to web search if yt-dlp not available
            return web_search(query)
    except Exception as e:
        return f"YouTube search error: {str(e)}"


def sync_to_cloud(path: str, service: str = "gdrive") -> str:
    """Sync folder to cloud storage. Input: folder path and service name (gdrive, dropbox, onedrive)."""
    try:
        path = path.strip() or os.path.expanduser("~/Downloads")

        if not os.path.exists(path):
            return f"Path not found: {path}"

        # Validate service name
        valid_services = ["gdrive", "dropbox", "onedrive", "drive"]
        if service.lower() not in valid_services:
            return f"Invalid service. Use: {', '.join(valid_services)}"

        # Map service names to rclone remotes
        service_map = {
            "gdrive": "gdrive",
            "drive": "gdrive",
            "dropbox": "dropbox",
            "onedrive": "onedrive",
        }

        remote_name = service_map.get(service.lower(), "gdrive")

        # Run rclone sync
        result = subprocess.run(
            [
                "rclone",
                "sync",
                path,
                f"{remote_name}:/Terminator-Backups/{os.path.basename(path)}",
                "--progress",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            return f"✅ Synced '{os.path.basename(path)}' to {service.upper()} successfully!"
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            return f"Sync error: {error_msg}"

    except subprocess.TimeoutExpired:
        return "Sync timeout - large folder may take longer"
    except Exception as e:
        return f"Cloud sync error: {str(e)}"


def open_in_zed(path: str) -> str:
    """Open file or folder in Zed editor. Input: file or folder path."""
    try:
        path = path.strip()

        if not path:
            return "No path provided. Use: open_in_zed('/path/to/file')"

        if not os.path.exists(path):
            return f"Path not found: {path}"

        # Check if Zed is installed
        result = subprocess.run(["which", "zed"], capture_output=True, text=True)

        if result.returncode != 0:
            return "Zed editor not found. Install with: brew install zed"

        # Open in Zed
        subprocess.Popen(["zed", path])

        item_type = "folder" if os.path.isdir(path) else "file"
        return f"✅ Opening {item_type} in Zed: {path}"

    except Exception as e:
        return f"Zed open error: {str(e)}"


def read_apple_note(note_name: str) -> str:
    """Read text from Apple Notes by note name. Input: note name (e.g., 'Test Document')."""
    try:
        note_name = note_name.strip()

        if not note_name:
            return "No note name provided. Use: read_apple_note('Note Name')"

        # AppleScript to get note content from Apple Notes
        script = f"""
        tell application "Notes"
            activate
            set theNotes to notes whose name contains "{note_name}"
            if (count of theNotes) > 0 then
                set theNote to item 1 of theNotes
                set noteContent to body of theNote
                return noteContent
            else
                return "Note not found: {note_name}"
            end if
        end tell
        """

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            content = result.stdout.strip()
            if "Note not found" in content:
                return f"❌ Note '{note_name}' not found in Apple Notes"
            return f"📝 Content from '{note_name}':\n\n{content}"
        else:
            error = result.stderr.strip()
            if "not permitted" in error.lower():
                return "⚠️ Permission denied. Grant access to Notes in System Settings → Privacy & Security → Automation"
            return f"Error reading note: {error}"

    except subprocess.TimeoutExpired:
        return "Request timeout - Apple Notes took too long to respond"
    except Exception as e:
        return f"Note reading error: {str(e)}"


def edit_apple_note(note_name: str, new_content: str) -> str:
    """Edit/update Apple Notes content. Input: note name and new content text."""
    try:
        note_name = note_name.strip()
        new_content = new_content.strip()

        if not note_name or not new_content:
            return "Error: Both note name and content are required"

        # AppleScript to update note content
        script = f"""
        tell application "Notes"
            activate
            set theNotes to notes whose name contains "{note_name}"
            if (count of theNotes) > 0 then
                set theNote to item 1 of theNotes
                set body of theNote to "{new_content.replace('"', '\\"')}"
                return "Note updated successfully"
            else
                return "Note not found: {note_name}"
            end if
        end tell
        """

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            response = result.stdout.strip()
            if "Note not found" in response:
                return f"❌ Note '{note_name}' not found in Apple Notes"
            return f"✅ Successfully updated '{note_name}' in Apple Notes"
        else:
            error = result.stderr.strip()
            if "not permitted" in error.lower():
                return "⚠️ Permission denied. Grant access to Notes in System Settings → Privacy & Security → Automation"
            return f"Error updating note: {error}"

    except subprocess.TimeoutExpired:
        return "Request timeout - Apple Notes took too long to respond"
    except Exception as e:
        return f"Note editing error: {str(e)}"


def software_bug_assistant_tool(query: str) -> str:
    """Interact with the Java Software Bug Assistant to triage and debug software issues. Input: The bug query or description."""
    # Use relative path for portability across devices and OS
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    JAVA_JAR_PATH = os.path.join(
        PROJECT_ROOT,
        "software-bug-assistant",
        "target",
        "software-bug-assistant-1.0-SNAPSHOT-jar-with-dependencies.jar",
    )

    if not os.path.exists(JAVA_JAR_PATH):
        return f"Error: Software Bug Assistant JAR not found at {JAVA_JAR_PATH}. Please compile the Java project."

    try:
        # Start the Java process
        process = subprocess.Popen(
            ["java", "-jar", JAVA_JAR_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line-buffered
        )

        # Discard initial prompt "You > "
        process.stdout.readline()

        # Send the query to the Java assistant's stdin
        process.stdin.write(query + "\n")
        process.stdin.flush()

        response_lines = []
        timeout_seconds = 60
        start_time = time.time()

        while True:
            # Check if process has exited or if timeout occurred
            if process.poll() is not None:
                break
            if time.time() - start_time > timeout_seconds:
                process.terminate()
                return "Error: Software Bug Assistant timed out."

            line = process.stdout.readline()
            if line.strip().startswith("Agent > "):
                response_lines.append(line.replace("Agent > ", "").strip())
                break  # Assuming the agent provides a single turn response after its prompt
            elif line.strip():  # Capture other output before Agent > if any
                response_lines.append(line.strip())

        # Read any remaining output or error for debugging
        stderr_output = process.stderr.read().strip()
        if stderr_output:
            logger.error(f"Software Bug Assistant Stderr: {stderr_output}")

        return "\n".join(response_lines)

    except FileNotFoundError:
        return f"Error: Java executable not found. Is Java installed and in your PATH?"
    except Exception as e:
        return f"Error interacting with Software Bug Assistant: {str(e)}"


# === AGENT SETUP ===


class SimpleAgent:
    """Simple ReAct-style agent for Ollama that doesn't require tool binding."""

    def __init__(self, model: str = "qwen2", auto_select: bool = True):
        self.auto_select = auto_select
        self.default_model = model
        self.current_model = model

        # Initialize model manager if available
        if MODEL_MANAGER_AVAILABLE and auto_select:
            self.model_manager = TerminatorModelManager()
            print(f"🤖 Terminator: Multi-model AI initialized")
            print(f"   Default: {model} | Auto-select: Enabled")
        else:
            self.model_manager = None
            print(f"🤖 Terminator: Using single model: {model}")

        # Initialize OllamaLLM with timeout and retry logic
        self.llm = OllamaLLM(
            model=model,
            temperature=0,
            base_url="http://localhost:11434",  # Explicit URL
            timeout=120.0,  # 2 minute timeout
            request_timeout=120.0
        )
        self.tool_functions = {
            "web_search": web_search,
            "youtube_search": youtube_search,
            "translate_to_bengali": translate_to_bengali,
            "create_folder_structure": create_folder_structure,
            "file_search": file_search,
            "read_file": read_file,
            "list_directory": list_directory,
            "sync_to_cloud": sync_to_cloud,
            "open_in_zed": open_in_zed,
            "read_apple_note": read_apple_note,
            "edit_apple_note": edit_apple_note,
            "software_bug_assistant": software_bug_assistant_tool,
        }

    def invoke(self, messages_dict):
        """Simple single-turn agent with tool use."""
        query = (
            messages_dict["messages"][0][1]
            if isinstance(messages_dict["messages"][0], tuple)
            else str(messages_dict["messages"][0])
        )

        # First pass: Get reasoning
        reasoning_prompt = f"""You are a helpful AI assistant with access to tools.

Available tools:
1. web_search(query) - Search the internet for information
2. youtube_search(query) - Search YouTube for videos
3. translate_to_bengali(text) - Translate text to Bengali language
4. create_folder_structure(subject) - Create organized folder structure by subject (AI, python, web, etc)
5. file_search(query) - Search files on the computer
6. read_file(path) - Read file contents
7. list_directory(path) - List directory contents
8. sync_to_cloud(path, service) - Sync folder to cloud storage (gdrive, dropbox, onedrive)
9. open_in_zed(path) - Open file or folder in Zed editor
10. read_apple_note(note_name) - Read notes from Apple Notes (e.g., "Test Document")
11. edit_apple_note(note_name, new_content) - Edit/update note content in Apple Notes
12. software_bug_assistant(query) - Interact with the Java Software Bug Assistant for bug triage

User query: {query}

Think about which tool(s) would best answer this question. If you need to use tools, format your response like this:
ACTION: tool_name
INPUT: the input for the tool

If you don't need tools, just provide your answer directly."""

        # Try to invoke with retry logic
        max_retries = 3
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(reasoning_prompt)
                break  # Success, exit retry loop
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    import time
                    print(f"  ⚠️  Connection attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)  # Wait before retry
                else:
                    # All retries exhausted
                    raise last_error

        # Check if we need to use a tool
        if "ACTION:" in response:
            lines = response.split("\n")
            tool_name = None
            tool_input = None

            for i, line in enumerate(lines):
                if "ACTION:" in line:
                    tool_name = line.replace("ACTION:", "").strip().lower()
                if "INPUT:" in line:
                    tool_input = line.replace("INPUT:", "").strip()

            # Call the tool
            if tool_name and tool_name in self.tool_functions:
                print(f"  🔧 Using tool: {tool_name}")
                print(f"  📝 Input: {tool_input}\n")
                # Call the function directly
                tool_result = self.tool_functions[tool_name](tool_input)

                # Second pass: Use tool result to answer
                final_prompt = f"""Based on the tool results below, answer the user's query.

User query: {query}

Tool result:
{tool_result}

Please provide a clear, helpful answer based on this information."""

                final_response = self.llm.invoke(final_prompt)
                return {"messages": [("user", query), ("assistant", final_response)]}

        # No tool needed, just return the response
        return {"messages": [("user", query), ("assistant", response)]}


def create_agent(model: str = "qwen2", auto_select: bool = True):
    """
    Create a simple agent for Ollama.

    Args:
        model: Default model to use
        auto_select: Enable intelligent model selection (default: True)
    """
    return SimpleAgent(model=model, auto_select=auto_select)


def main():
    import requests

    print("\n" + "=" * 60)
    print("  🤖 Terminator AI Agent with Ollama + Web Search + YouTube")
    print("  Web Search + YouTube + File Access + LangGraph")
    print("=" * 60)
    print("\n📊 Tools available:")
    print("  • 🔍 web_search - Search the internet via DuckDuckGo")
    print("  • 📺 youtube_search - Search YouTube for videos")
    print("  • 📁 file_search - Find files on your Mac (Spotlight)")
    print("  • 📄 read_file - Read file contents")
    print("  • 📂 list_directory - List folder contents")
    print("\n💡 Try: 'search youtube for Gemini CLI'")
    print("💡 Try: 'what is the latest news about AI?'")
    print("💡 Try: 'find markdown files' or 'read file ~/Desktop/AI/CLAUDE.md'")
    print("\n⌨️  Type 'quit' to exit.\n")

    # Check Ollama connection before proceeding
    print("🔌 Checking Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is ready\n")
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            print("ℹ️  Start Ollama with: ollama serve\n")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama at http://localhost:11434")
        print("ℹ️  Start Ollama with: ollama serve\n")
        return
    except Exception as e:
        print(f"❌ Ollama check error: {e}\n")
        return

    print("🚀 Initializing agent...\n")
    agent = create_agent()

    while True:
        try:
            query = input("You: ").strip()
            if not query:
                continue
            if query.lower() in ["quit", "exit", "q"]:
                print("\n✅ Goodbye!")
                break

            print("\n🤔 Agent thinking...\n")
            # Simple agent returns {'messages': [('user', ...), ('assistant', ...)]}
            result = agent.invoke({"messages": [("user", query)]})

            # Extract the final message from the agent
            if result and "messages" in result:
                # Get the last message (should be from the agent)
                last_message = result["messages"][-1]
                if isinstance(last_message, tuple):
                    # It's a tuple (role, content)
                    content = last_message[1]
                elif hasattr(last_message, "content"):
                    content = last_message.content
                else:
                    content = str(last_message)
                print(f"🤖 Agent: {content}\n")
            else:
                print(f"🤖 Agent: {result}\n")

        except KeyboardInterrupt:
            print("\n✅ Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
