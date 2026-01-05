#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Claude Activity Logger Agent
======================================

Automatically logs EVERY change Claude makes to the system.

Tracks:
- Files created
- Files modified
- Files deleted
- Commands executed
- Agents created/modified
- Configuration changes

Creates detailed logs in: .claude_activity/

Created: December 17, 2025
Purpose: Complete audit trail of all Claude activities
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


# ============================================================================
# Activity Types
# ============================================================================

class ActivityType(Enum):
    """Type of activity"""
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    COMMAND_EXECUTED = "command_executed"
    AGENT_CREATED = "agent_created"
    AGENT_MODIFIED = "agent_modified"
    CONFIGURATION_CHANGED = "config_changed"
    DOCUMENTATION_UPDATED = "doc_updated"


@dataclass
class ClaudeActivity:
    """A single activity by Claude"""
    activity_id: str
    timestamp: str
    activity_type: ActivityType
    description: str
    file_path: Optional[str] = None
    command: Optional[str] = None
    before_hash: Optional[str] = None
    after_hash: Optional[str] = None
    lines_added: int = 0
    lines_removed: int = 0
    user_request: Optional[str] = None


# ============================================================================
# Claude Activity Logger
# ============================================================================

class ClaudeActivityLogger:
    """
    Logs all Claude activities for complete audit trail.
    """

    def __init__(self):
        """Initialize activity logger"""
        self.project_root = Path("/Users/reeazmahmud/Desktop/Terminator-Project")
        self.log_dir = self.project_root / ".claude_activity"
        self.log_dir.mkdir(exist_ok=True)

        # Log files
        self.daily_log_file = self.log_dir / f"claude_{datetime.now().strftime('%Y%m%d')}.log"
        self.activity_json = self.log_dir / "activities.json"
        self.summary_file = self.log_dir / "CLAUDE_ACTIVITY_SUMMARY.md"

        # State
        self.activities: List[ClaudeActivity] = []
        self.current_session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        self._load_activities()

    def _load_activities(self) -> None:
        """Load existing activities"""
        if self.activity_json.exists():
            try:
                with open(self.activity_json, 'r') as f:
                    data = json.load(f)
                    for act_dict in data:
                        activity = ClaudeActivity(
                            activity_id=act_dict['activity_id'],
                            timestamp=act_dict['timestamp'],
                            activity_type=ActivityType(act_dict['activity_type']),
                            description=act_dict['description'],
                            file_path=act_dict.get('file_path'),
                            command=act_dict.get('command'),
                            before_hash=act_dict.get('before_hash'),
                            after_hash=act_dict.get('after_hash'),
                            lines_added=act_dict.get('lines_added', 0),
                            lines_removed=act_dict.get('lines_removed', 0),
                            user_request=act_dict.get('user_request')
                        )
                        self.activities.append(activity)
            except Exception as e:
                print(f"⚠️  Could not load activities: {e}")

    def _save_activities(self) -> None:
        """Save activities to JSON"""
        try:
            with open(self.activity_json, 'w') as f:
                json.dump(
                    [self._activity_to_dict(a) for a in self.activities],
                    f,
                    indent=2
                )
        except Exception as e:
            print(f"⚠️  Could not save activities: {e}")

    def _activity_to_dict(self, activity: ClaudeActivity) -> dict:
        """Convert activity to dict"""
        return {
            **asdict(activity),
            'activity_type': activity.activity_type.value
        }

    def log_file_created(self, file_path: str, description: str, user_request: str = None):
        """Log file creation"""
        content_hash = self._get_file_hash(file_path)

        activity = ClaudeActivity(
            activity_id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            activity_type=ActivityType.FILE_CREATED,
            description=description,
            file_path=file_path,
            after_hash=content_hash,
            user_request=user_request
        )

        self._record_activity(activity)

    def log_file_modified(self, file_path: str, description: str, user_request: str = None):
        """Log file modification"""
        activity = ClaudeActivity(
            activity_id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            activity_type=ActivityType.FILE_MODIFIED,
            description=description,
            file_path=file_path,
            after_hash=self._get_file_hash(file_path),
            user_request=user_request
        )

        self._record_activity(activity)

    def log_file_deleted(self, file_path: str, description: str, user_request: str = None):
        """Log file deletion"""
        activity = ClaudeActivity(
            activity_id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            activity_type=ActivityType.FILE_DELETED,
            description=description,
            file_path=file_path,
            user_request=user_request
        )

        self._record_activity(activity)

    def log_command(self, command: str, description: str, user_request: str = None):
        """Log command execution"""
        activity = ClaudeActivity(
            activity_id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            activity_type=ActivityType.COMMAND_EXECUTED,
            description=description,
            command=command,
            user_request=user_request
        )

        self._record_activity(activity)

    def _record_activity(self, activity: ClaudeActivity) -> None:
        """Record an activity"""
        self.activities.append(activity)

        # Write to daily log
        with open(self.daily_log_file, 'a') as f:
            f.write(f"[{activity.timestamp}] {activity.activity_type.value}: {activity.description}\n")
            if activity.file_path:
                f.write(f"  File: {activity.file_path}\n")
            if activity.command:
                f.write(f"  Command: {activity.command}\n")
            f.write("\n")

        # Save JSON
        self._save_activities()

        # Update summary
        self._update_summary()

        print(f"📝 Logged: {activity.activity_type.value} - {activity.description}")

    def _update_summary(self) -> None:
        """Update summary markdown file"""
        summary = f"""# Claude Activity Summary

**Session:** {self.current_session_id}
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statistics

- **Total Activities:** {len(self.activities)}
- **Files Created:** {sum(1 for a in self.activities if a.activity_type == ActivityType.FILE_CREATED)}
- **Files Modified:** {sum(1 for a in self.activities if a.activity_type == ActivityType.FILE_MODIFIED)}
- **Files Deleted:** {sum(1 for a in self.activities if a.activity_type == ActivityType.FILE_DELETED)}
- **Commands Executed:** {sum(1 for a in self.activities if a.activity_type == ActivityType.COMMAND_EXECUTED)}

## Recent Activities (Last 20)

"""

        for activity in self.activities[-20:]:
            summary += f"""### [{activity.timestamp[:19]}] {activity.activity_type.value}

**Description:** {activity.description}
"""
            if activity.file_path:
                summary += f"**File:** `{activity.file_path}`\n"
            if activity.command:
                summary += f"**Command:** `{activity.command}`\n"
            if activity.user_request:
                summary += f"**User Request:** {activity.user_request}\n"

            summary += "\n---\n\n"

        with open(self.summary_file, 'w') as f:
            f.write(summary)

    def _get_file_hash(self, file_path: str) -> Optional[str]:
        """Get hash of file contents"""
        try:
            path = Path(file_path)
            if path.exists():
                with open(path, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()
        except:
            pass
        return None

    def _generate_id(self) -> str:
        """Generate activity ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def get_session_report(self) -> str:
        """Get report for current session"""
        session_activities = [
            a for a in self.activities
            if a.timestamp.startswith(datetime.now().strftime('%Y-%m-%d'))
        ]

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           CLAUDE ACTIVITY REPORT - TODAY                     ║
╚══════════════════════════════════════════════════════════════╝

📊 Today's Statistics:
   • Total activities: {len(session_activities)}
   • Files created: {sum(1 for a in session_activities if a.activity_type == ActivityType.FILE_CREATED)}
   • Files modified: {sum(1 for a in session_activities if a.activity_type == ActivityType.FILE_MODIFIED)}
   • Commands: {sum(1 for a in session_activities if a.activity_type == ActivityType.COMMAND_EXECUTED)}

📁 Files Affected:
"""

        files_affected = set(a.file_path for a in session_activities if a.file_path)
        for file_path in sorted(files_affected):
            report += f"   • {file_path}\n"

        report += f"""
📝 Log Files:
   • Daily log: {self.daily_log_file}
   • Activity JSON: {self.activity_json}
   • Summary: {self.summary_file}
"""

        return report


# ============================================================================
# Module Interface
# ============================================================================

_logger_instance = None

def get_activity_logger() -> ClaudeActivityLogger:
    """Get the activity logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ClaudeActivityLogger()
    return _logger_instance


# Quick logging functions
def log_created(file: str, desc: str, request: str = None):
    """Quick log for file creation"""
    get_activity_logger().log_file_created(file, desc, request)


def log_modified(file: str, desc: str, request: str = None):
    """Quick log for file modification"""
    get_activity_logger().log_file_modified(file, desc, request)


def log_deleted(file: str, desc: str, request: str = None):
    """Quick log for file deletion"""
    get_activity_logger().log_file_deleted(file, desc, request)


def log_command(cmd: str, desc: str, request: str = None):
    """Quick log for command execution"""
    get_activity_logger().log_command(cmd, desc, request)


if __name__ == "__main__":
    # Demo
    logger = get_activity_logger()
    print(logger.get_session_report())
