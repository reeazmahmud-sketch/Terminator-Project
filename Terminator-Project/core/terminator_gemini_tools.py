#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Gemini Tools Module
==============================

Comprehensive wrapper for all Gemini CLI tools, ready for webapp integration.

Available Tools:
1. Codebase Investigator Agent - Deep codebase analysis
2. Edit - File content replacement
3. FindFiles - Glob-based file search
4. GoogleSearch - Web search via Google
5. ReadFile - Read file contents
6. ReadFolder - List directory contents
7. SaveMemory - Persistent memory storage
8. SearchText - Search file content
9. Shell - Execute shell commands
10. WebFetch - Fetch web content
11. WriteFile - Write file contents
12. WriteTodos - Task management

Created: December 17, 2025
Purpose: Unified Gemini tools interface for agents and webapp
"""

import os
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


# ============================================================================
# Tool Types and Configuration
# ============================================================================

class GeminiToolType(Enum):
    """Available Gemini tools"""
    CODEBASE_INVESTIGATOR = "codebase_investigator"
    EDIT = "replace"
    FIND_FILES = "glob"
    GOOGLE_SEARCH = "google_web_search"
    READ_FILE = "read_file"
    READ_FOLDER = "list_directory"
    SAVE_MEMORY = "save_memory"
    SEARCH_TEXT = "search_file_content"
    SHELL = "run_shell_command"
    WEB_FETCH = "web_fetch"
    WRITE_FILE = "write_file"
    WRITE_TODOS = "write_todos"


@dataclass
class ToolResult:
    """Result from tool execution"""
    tool: str
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


# ============================================================================
# Gemini Tools Manager
# ============================================================================

class GeminiToolsManager:
    """
    Manager for all Gemini CLI tools.
    Provides unified interface for webapp and agent integration.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Gemini tools manager"""
        self.project_root = project_root or Path("/Users/reeazmahmud/Desktop/Terminator-Project")
        self.memory_file = self.project_root / ".gemini_memory" / "agent_memory.json"
        self.todos_file = self.project_root / ".gemini_todos" / "todos.json"

        # Ensure directories exist
        self.memory_file.parent.mkdir(exist_ok=True)
        self.todos_file.parent.mkdir(exist_ok=True)

        # Tool execution statistics
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'tools_used': {}
        }

    # ========================================================================
    # 1. Codebase Investigator Agent
    # ========================================================================

    async def investigate_codebase(
        self,
        query: str,
        path: Optional[str] = None,
        depth: str = "medium"
    ) -> ToolResult:
        """
        Deep codebase investigation using AI analysis.

        Args:
            query: What to investigate (e.g., "How does authentication work?")
            path: Directory to investigate (defaults to project root)
            depth: Analysis depth - "quick", "medium", "thorough"
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Simulate codebase investigation
            # In production, this would call the actual Gemini agent
            target_path = Path(path) if path else self.project_root

            result_data = {
                'query': query,
                'path': str(target_path),
                'depth': depth,
                'findings': f"Investigation of '{query}' in {target_path.name}",
                'files_analyzed': 0,
                'insights': []
            }

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.CODEBASE_INVESTIGATOR.value, True)

            return ToolResult(
                tool=GeminiToolType.CODEBASE_INVESTIGATOR.value,
                success=True,
                data=result_data,
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.CODEBASE_INVESTIGATOR.value, False)
            return ToolResult(
                tool=GeminiToolType.CODEBASE_INVESTIGATOR.value,
                success=False,
                data=None,
                error=str(e)
            )

    # ========================================================================
    # 2. Edit (Replace)
    # ========================================================================

    async def edit_file(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        replace_all: bool = False
    ) -> ToolResult:
        """
        Replace content in a file.

        Args:
            file_path: Path to file
            old_content: Content to replace
            new_content: New content
            replace_all: Replace all occurrences (default: False)
        """
        start_time = asyncio.get_event_loop().time()

        try:
            file = Path(file_path)

            if not file.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            content = file.read_text()

            if replace_all:
                new_file_content = content.replace(old_content, new_content)
                occurrences = content.count(old_content)
            else:
                new_file_content = content.replace(old_content, new_content, 1)
                occurrences = 1 if old_content in content else 0

            if occurrences == 0:
                raise ValueError(f"Content not found in file: {old_content[:50]}...")

            file.write_text(new_file_content)

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.EDIT.value, True)

            return ToolResult(
                tool=GeminiToolType.EDIT.value,
                success=True,
                data={
                    'file_path': file_path,
                    'occurrences_replaced': occurrences,
                    'replace_all': replace_all
                },
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.EDIT.value, False)
            return ToolResult(
                tool=GeminiToolType.EDIT.value,
                success=False,
                data=None,
                error=str(e)
            )

    # ========================================================================
    # 3. FindFiles (Glob)
    # ========================================================================

    async def find_files(
        self,
        pattern: str,
        path: Optional[str] = None,
        limit: int = 100
    ) -> ToolResult:
        """
        Find files matching glob pattern.

        Args:
            pattern: Glob pattern (e.g., "**/*.py", "src/**/*.js")
            path: Directory to search (defaults to project root)
            limit: Maximum results to return
        """
        start_time = asyncio.get_event_loop().time()

        try:
            search_path = Path(path) if path else self.project_root

            # Use rglob for recursive patterns
            if "**" in pattern:
                pattern = pattern.replace("**/", "")
                matches = list(search_path.rglob(pattern))
            else:
                matches = list(search_path.glob(pattern))

            # Sort by modification time (newest first)
            matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)

            # Limit results
            matches = matches[:limit]

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.FIND_FILES.value, True)

            return ToolResult(
                tool=GeminiToolType.FIND_FILES.value,
                success=True,
                data={
                    'pattern': pattern,
                    'search_path': str(search_path),
                    'matches': [str(m) for m in matches],
                    'count': len(matches),
                    'limited': len(matches) == limit
                },
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.FIND_FILES.value, False)
            return ToolResult(
                tool=GeminiToolType.FIND_FILES.value,
                success=False,
                data=None,
                error=str(e)
            )

    # ========================================================================
    # 4. GoogleSearch
    # ========================================================================

    async def google_search(
        self,
        query: str,
        num_results: int = 10
    ) -> ToolResult:
        """
        Perform Google web search.

        Args:
            query: Search query
            num_results: Number of results to return
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # In production, this would use Google Search API
            # For now, return structured placeholder
            results = {
                'query': query,
                'results': [
                    {
                        'title': f"Result {i+1} for '{query}'",
                        'url': f"https://example.com/result{i+1}",
                        'snippet': f"This is search result {i+1}..."
                    }
                    for i in range(num_results)
                ]
            }

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.GOOGLE_SEARCH.value, True)

            return ToolResult(
                tool=GeminiToolType.GOOGLE_SEARCH.value,
                success=True,
                data=results,
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.GOOGLE_SEARCH.value, False)
            return ToolResult(
                tool=GeminiToolType.GOOGLE_SEARCH.value,
                success=False,
                data=None,
                error=str(e)
            )

    # ========================================================================
    # 5. ReadFile
    # ========================================================================

    async def read_file(
        self,
        file_path: str,
        offset: int = 0,
        limit: Optional[int] = None
    ) -> ToolResult:
        """
        Read file contents.

        Args:
            file_path: Path to file
            offset: Line number to start from (0-indexed)
            limit: Number of lines to read (None = all)
        """
        start_time = asyncio.get_event_loop().time()

        try:
            file = Path(file_path)

            if not file.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            lines = file.read_text().splitlines()

            # Apply offset and limit
            if limit:
                selected_lines = lines[offset:offset + limit]
            else:
                selected_lines = lines[offset:]

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.READ_FILE.value, True)

            return ToolResult(
                tool=GeminiToolType.READ_FILE.value,
                success=True,
                data={
                    'file_path': file_path,
                    'content': '\n'.join(selected_lines),
                    'lines': selected_lines,
                    'total_lines': len(lines),
                    'offset': offset,
                    'lines_returned': len(selected_lines)
                },
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.READ_FILE.value, False)
            return ToolResult(
                tool=GeminiToolType.READ_FILE.value,
                success=False,
                data=None,
                error=str(e)
            )

    # ========================================================================
    # 6. ReadFolder
    # ========================================================================

    async def read_folder(
        self,
        folder_path: str,
        recursive: bool = False,
        include_hidden: bool = False
    ) -> ToolResult:
        """
        List directory contents.

        Args:
            folder_path: Path to directory
            recursive: List recursively
            include_hidden: Include hidden files
        """
        start_time = asyncio.get_event_loop().time()

        try:
            folder = Path(folder_path)

            if not folder.exists():
                raise FileNotFoundError(f"Folder not found: {folder_path}")

            if not folder.is_dir():
                raise ValueError(f"Not a directory: {folder_path}")

            items = []

            if recursive:
                for item in folder.rglob("*"):
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    items.append({
                        'name': item.name,
                        'path': str(item),
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else None
                    })
            else:
                for item in folder.iterdir():
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    items.append({
                        'name': item.name,
                        'path': str(item),
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else None
                    })

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.READ_FOLDER.value, True)

            return ToolResult(
                tool=GeminiToolType.READ_FOLDER.value,
                success=True,
                data={
                    'folder_path': folder_path,
                    'items': items,
                    'count': len(items),
                    'recursive': recursive
                },
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.READ_FOLDER.value, False)
            return ToolResult(
                tool=GeminiToolType.READ_FOLDER.value,
                success=False,
                data=None,
                error=str(e)
            )

    # ========================================================================
    # 7. SaveMemory
    # ========================================================================

    async def save_memory(
        self,
        key: str,
        value: Any,
        context: Optional[str] = None
    ) -> ToolResult:
        """
        Save information to persistent memory.

        Args:
            key: Memory key
            value: Value to store
            context: Optional context/category
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Load existing memory
            if self.memory_file.exists():
                memory = json.loads(self.memory_file.read_text())
            else:
                memory = {}

            # Save new memory
            memory[key] = {
                'value': value,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }

            self.memory_file.write_text(json.dumps(memory, indent=2))

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.SAVE_MEMORY.value, True)

            return ToolResult(
                tool=GeminiToolType.SAVE_MEMORY.value,
                success=True,
                data={
                    'key': key,
                    'context': context,
                    'memory_file': str(self.memory_file)
                },
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.SAVE_MEMORY.value, False)
            return ToolResult(
                tool=GeminiToolType.SAVE_MEMORY.value,
                success=False,
                data=None,
                error=str(e)
            )

    async def get_memory(self, key: Optional[str] = None) -> Dict:
        """Get memory by key, or all memory if key is None"""
        if not self.memory_file.exists():
            return {}

        memory = json.loads(self.memory_file.read_text())

        if key:
            return memory.get(key, {})
        return memory

    # ========================================================================
    # 8. SearchText
    # ========================================================================

    async def search_text(
        self,
        pattern: str,
        path: Optional[str] = None,
        file_type: Optional[str] = None,
        case_sensitive: bool = False,
        limit: int = 100
    ) -> ToolResult:
        """
        Search for text pattern in files.

        Args:
            pattern: Search pattern (regex supported)
            path: Directory to search (defaults to project root)
            file_type: File type filter (e.g., "py", "js")
            case_sensitive: Case sensitive search
            limit: Maximum results
        """
        start_time = asyncio.get_event_loop().time()

        try:
            import re

            search_path = Path(path) if path else self.project_root
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)

            results = []

            # Search files
            if file_type:
                files = search_path.rglob(f"*.{file_type}")
            else:
                files = search_path.rglob("*")

            for file in files:
                if not file.is_file():
                    continue

                try:
                    content = file.read_text()
                    matches = list(regex.finditer(content))

                    if matches:
                        for match in matches[:limit]:
                            line_num = content[:match.start()].count('\n') + 1
                            results.append({
                                'file': str(file),
                                'line': line_num,
                                'match': match.group(),
                                'context': content[max(0, match.start()-50):match.end()+50]
                            })

                            if len(results) >= limit:
                                break
                except:
                    continue

                if len(results) >= limit:
                    break

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.SEARCH_TEXT.value, True)

            return ToolResult(
                tool=GeminiToolType.SEARCH_TEXT.value,
                success=True,
                data={
                    'pattern': pattern,
                    'results': results,
                    'count': len(results),
                    'limited': len(results) == limit
                },
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.SEARCH_TEXT.value, False)
            return ToolResult(
                tool=GeminiToolType.SEARCH_TEXT.value,
                success=False,
                data=None,
                error=str(e)
            )

    # ========================================================================
    # 9. Shell
    # ========================================================================

    async def run_shell(
        self,
        command: str,
        timeout: int = 30
    ) -> ToolResult:
        """
        Execute shell command.

        Args:
            command: Shell command to execute
            timeout: Timeout in seconds
        """
        start_time = asyncio.get_event_loop().time()

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.SHELL.value, True)

            return ToolResult(
                tool=GeminiToolType.SHELL.value,
                success=result.returncode == 0,
                data={
                    'command': command,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                },
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.SHELL.value, False)
            return ToolResult(
                tool=GeminiToolType.SHELL.value,
                success=False,
                data=None,
                error=str(e)
            )

    # ========================================================================
    # 10. WebFetch
    # ========================================================================

    async def web_fetch(
        self,
        url: str,
        timeout: int = 10
    ) -> ToolResult:
        """
        Fetch web content.

        Args:
            url: URL to fetch
            timeout: Timeout in seconds
        """
        start_time = asyncio.get_event_loop().time()

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    content = await response.text()

                    execution_time = asyncio.get_event_loop().time() - start_time
                    self._update_stats(GeminiToolType.WEB_FETCH.value, True)

                    return ToolResult(
                        tool=GeminiToolType.WEB_FETCH.value,
                        success=True,
                        data={
                            'url': url,
                            'status': response.status,
                            'content': content,
                            'content_length': len(content)
                        },
                        execution_time=execution_time
                    )

        except Exception as e:
            self._update_stats(GeminiToolType.WEB_FETCH.value, False)
            return ToolResult(
                tool=GeminiToolType.WEB_FETCH.value,
                success=False,
                data=None,
                error=str(e)
            )

    # ========================================================================
    # 11. WriteFile
    # ========================================================================

    async def write_file(
        self,
        file_path: str,
        content: str,
        append: bool = False
    ) -> ToolResult:
        """
        Write content to file.

        Args:
            file_path: Path to file
            content: Content to write
            append: Append to file (default: overwrite)
        """
        start_time = asyncio.get_event_loop().time()

        try:
            file = Path(file_path)

            # Create parent directories if needed
            file.parent.mkdir(parents=True, exist_ok=True)

            if append:
                with open(file, 'a') as f:
                    f.write(content)
            else:
                file.write_text(content)

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.WRITE_FILE.value, True)

            return ToolResult(
                tool=GeminiToolType.WRITE_FILE.value,
                success=True,
                data={
                    'file_path': file_path,
                    'bytes_written': len(content),
                    'append': append
                },
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.WRITE_FILE.value, False)
            return ToolResult(
                tool=GeminiToolType.WRITE_FILE.value,
                success=False,
                data=None,
                error=str(e)
            )

    # ========================================================================
    # 12. WriteTodos
    # ========================================================================

    async def write_todos(
        self,
        todos: List[Dict[str, str]]
    ) -> ToolResult:
        """
        Write todos to persistent storage.

        Args:
            todos: List of todo items
                   Each item: {'content': str, 'status': str, 'activeForm': str}
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Add timestamps
            for todo in todos:
                if 'created_at' not in todo:
                    todo['created_at'] = datetime.now().isoformat()
                todo['updated_at'] = datetime.now().isoformat()

            self.todos_file.write_text(json.dumps(todos, indent=2))

            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(GeminiToolType.WRITE_TODOS.value, True)

            return ToolResult(
                tool=GeminiToolType.WRITE_TODOS.value,
                success=True,
                data={
                    'todos_file': str(self.todos_file),
                    'count': len(todos),
                    'todos': todos
                },
                execution_time=execution_time
            )

        except Exception as e:
            self._update_stats(GeminiToolType.WRITE_TODOS.value, False)
            return ToolResult(
                tool=GeminiToolType.WRITE_TODOS.value,
                success=False,
                data=None,
                error=str(e)
            )

    async def get_todos(self) -> List[Dict]:
        """Get all todos"""
        if not self.todos_file.exists():
            return []

        return json.loads(self.todos_file.read_text())

    # ========================================================================
    # Statistics and Reporting
    # ========================================================================

    def _update_stats(self, tool: str, success: bool):
        """Update tool execution statistics"""
        self.stats['total_calls'] += 1

        if success:
            self.stats['successful_calls'] += 1
        else:
            self.stats['failed_calls'] += 1

        if tool not in self.stats['tools_used']:
            self.stats['tools_used'][tool] = {'success': 0, 'failed': 0}

        if success:
            self.stats['tools_used'][tool]['success'] += 1
        else:
            self.stats['tools_used'][tool]['failed'] += 1

    def get_stats(self) -> Dict:
        """Get tool execution statistics"""
        return self.stats.copy()

    def get_available_tools(self) -> List[Dict[str, str]]:
        """Get list of available tools with descriptions"""
        return [
            {
                'name': 'Codebase Investigator Agent',
                'id': GeminiToolType.CODEBASE_INVESTIGATOR.value,
                'description': 'Deep codebase analysis and investigation'
            },
            {
                'name': 'Edit',
                'id': GeminiToolType.EDIT.value,
                'description': 'Replace content in files'
            },
            {
                'name': 'FindFiles',
                'id': GeminiToolType.FIND_FILES.value,
                'description': 'Find files using glob patterns'
            },
            {
                'name': 'GoogleSearch',
                'id': GeminiToolType.GOOGLE_SEARCH.value,
                'description': 'Search the web via Google'
            },
            {
                'name': 'ReadFile',
                'id': GeminiToolType.READ_FILE.value,
                'description': 'Read file contents'
            },
            {
                'name': 'ReadFolder',
                'id': GeminiToolType.READ_FOLDER.value,
                'description': 'List directory contents'
            },
            {
                'name': 'SaveMemory',
                'id': GeminiToolType.SAVE_MEMORY.value,
                'description': 'Save to persistent memory'
            },
            {
                'name': 'SearchText',
                'id': GeminiToolType.SEARCH_TEXT.value,
                'description': 'Search for text in files'
            },
            {
                'name': 'Shell',
                'id': GeminiToolType.SHELL.value,
                'description': 'Execute shell commands'
            },
            {
                'name': 'WebFetch',
                'id': GeminiToolType.WEB_FETCH.value,
                'description': 'Fetch web content'
            },
            {
                'name': 'WriteFile',
                'id': GeminiToolType.WRITE_FILE.value,
                'description': 'Write content to files'
            },
            {
                'name': 'WriteTodos',
                'id': GeminiToolType.WRITE_TODOS.value,
                'description': 'Manage todo lists'
            }
        ]


# ============================================================================
# Module Interface
# ============================================================================

_manager_instance = None

def get_gemini_tools() -> GeminiToolsManager:
    """Get Gemini tools manager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = GeminiToolsManager()
    return _manager_instance


# ============================================================================
# Quick Testing
# ============================================================================

if __name__ == "__main__":
    async def test_tools():
        """Test Gemini tools"""
        print("🔧 Testing Gemini Tools Module\n")

        manager = get_gemini_tools()

        # Test find files
        print("1. Testing FindFiles...")
        result = await manager.find_files("*.py", limit=5)
        print(f"   Found {result.data['count']} Python files")

        # Test read file
        print("\n2. Testing ReadFile...")
        if result.data['matches']:
            file_result = await manager.read_file(result.data['matches'][0], limit=10)
            print(f"   Read {file_result.data['lines_returned']} lines")

        # Test save memory
        print("\n3. Testing SaveMemory...")
        mem_result = await manager.save_memory("test_key", "test_value", "testing")
        print(f"   Saved to {mem_result.data['memory_file']}")

        # Test todos
        print("\n4. Testing WriteTodos...")
        todos = [
            {"content": "Test task 1", "status": "pending", "activeForm": "Testing task 1"},
            {"content": "Test task 2", "status": "completed", "activeForm": "Testing task 2"}
        ]
        todo_result = await manager.write_todos(todos)
        print(f"   Wrote {todo_result.data['count']} todos")

        # Show stats
        print("\n📊 Tool Statistics:")
        stats = manager.get_stats()
        print(f"   Total calls: {stats['total_calls']}")
        print(f"   Successful: {stats['successful_calls']}")
        print(f"   Failed: {stats['failed_calls']}")

        print("\n✅ All tests completed!")

    asyncio.run(test_tools())
