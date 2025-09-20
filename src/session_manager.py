"""
NewTerm Session Manager Module

Copyright (C) 2024 NewTerm Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import os
from typing import Dict, Any, List, Optional
from config import Config

class SessionManager:
    """Manages terminal sessions (save/restore tabs and state)."""

    def __init__(self, config: Config):
        self.config = config
        self.session_file = os.path.expanduser("~/.config/newterm/session.json")
        self.auto_save = config.get('auto_save_session', True)

    def save_session(self, tabs_data: List[Dict[str, Any]], active_tab_index: int = 0):
        """Save current session to file."""
        if not self.auto_save:
            return

        try:
            session_data = {
                "version": "1.0",
                "tabs": tabs_data,
                "active_tab": active_tab_index,
                "timestamp": self._get_timestamp()
            }

            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            print(f"Error saving session: {e}")

    def restore_session(self) -> Optional[Dict[str, Any]]:
        """Restore previous session from file."""
        try:
            if not os.path.exists(self.session_file):
                return None

            # Check if file is empty
            if os.path.getsize(self.session_file) == 0:
                print("Session file is empty, starting fresh")
                return None

            with open(self.session_file, 'r') as f:
                session_data = json.load(f)

            # Check version compatibility
            if session_data.get("version") != "1.0":
                print(f"Incompatible session version: {session_data.get('version')}")
                return None

            return session_data

        except json.JSONDecodeError as e:
            print(f"Session file corrupted: {e}, starting fresh")
            # Remove corrupted file
            try:
                os.remove(self.session_file)
            except:
                pass
            return None
        except Exception as e:
            print(f"Error restoring session: {e}")
            return None

    def clear_session(self):
        """Clear the saved session."""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception as e:
            print(f"Error clearing session: {e}")

    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session."""
        try:
            if not os.path.exists(self.session_file):
                return {"exists": False, "tabs": 0}

            with open(self.session_file, 'r') as f:
                session_data = json.load(f)

            return {
                "exists": True,
                "tabs": len(session_data.get("tabs", [])),
                "active_tab": session_data.get("active_tab", 0),
                "timestamp": session_data.get("timestamp", "unknown")
            }

        except Exception as e:
            return {"exists": False, "error": str(e)}

    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()

    def set_auto_save(self, enabled: bool):
        """Enable or disable auto-save."""
        self.auto_save = enabled
        self.config.config['auto_save_session'] = enabled
        self.config.save_config()
