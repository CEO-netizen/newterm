"""
NewTerm Keybinding Manager Module

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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from typing import Dict, Any, Callable, Optional, List, Tuple
import json
import os

class KeyBinding:
    """Represents a single keybinding with action and description."""

    def __init__(self, key_combo: str, action: str, callback: Callable,
                 description: str = "", category: str = "General"):
        self.key_combo = key_combo
        self.action = action
        self.callback = callback
        self.description = description
        self.category = category
        self.accelerator = self._parse_accelerator(key_combo)

    def _parse_accelerator(self, key_combo: str) -> Tuple[int, Gdk.ModifierType]:
        """Parse key combination string into accelerator components."""
        try:
            key, mod = Gtk.accelerator_parse(key_combo)
            return key, mod
        except Exception as e:
            print(f"Error parsing keybinding '{key_combo}': {e}")
            return 0, 0

    def is_valid(self) -> bool:
        """Check if the keybinding is valid."""
        return self.accelerator[0] != 0

class KeyBindingManager:
    """Manages all keybindings for the terminal application."""

    def __init__(self):
        self.bindings: Dict[str, KeyBinding] = {}
        self.categories: Dict[str, List[str]] = {}
        self.default_bindings = self._get_default_bindings()
        self.conflicts: List[Tuple[str, str]] = []

    def _get_default_bindings(self) -> Dict[str, Dict[str, Any]]:
        """Get default keybindings configuration."""
        return {
            "terminal": {
                "copy": {"key": "<Ctrl><Shift>C", "description": "Copy selected text"},
                "paste": {"key": "<Ctrl><Shift>V", "description": "Paste from clipboard"},
                "new_tab": {"key": "<Ctrl><Shift>T", "description": "Open new tab"},
                "close_tab": {"key": "<Ctrl><Shift>W", "description": "Close current tab"},
                "next_tab": {"key": "<Ctrl>Page_Down", "description": "Next tab"},
                "prev_tab": {"key": "<Ctrl>Page_Up", "description": "Previous tab"},
                "split_horizontal": {"key": "<Ctrl><Shift>H", "description": "Split horizontally"},
                "split_vertical": {"key": "<Ctrl><Shift>V", "description": "Split vertically"},
                "close_pane": {"key": "<Ctrl><Shift>Q", "description": "Close current pane"},
                "zoom_in": {"key": "<Ctrl>plus", "description": "Increase font size"},
                "zoom_out": {"key": "<Ctrl>minus", "description": "Decrease font size"},
                "reset_zoom": {"key": "<Ctrl>0", "description": "Reset font size"},
                "find": {"key": "<Ctrl><Shift>F", "description": "Find in terminal"},
                "command_palette": {"key": "<Ctrl><Shift>P", "description": "Command palette"},
                "preferences": {"key": "<Ctrl>comma", "description": "Open preferences"},
                "toggle_fullscreen": {"key": "F11", "description": "Toggle fullscreen"},
                "new_window": {"key": "<Ctrl><Shift>N", "description": "New window"},
                "quit": {"key": "<Ctrl><Shift>Q", "description": "Quit application"}
            },
            "navigation": {
                "scroll_up": {"key": "<Ctrl><Shift>Up", "description": "Scroll up one page"},
                "scroll_down": {"key": "<Ctrl><Shift>Down", "description": "Scroll down one page"},
                "scroll_to_top": {"key": "<Ctrl>Home", "description": "Scroll to top"},
                "scroll_to_bottom": {"key": "<Ctrl>End", "description": "Scroll to bottom"},
                "page_up": {"key": "Page_Up", "description": "Page up"},
                "page_down": {"key": "Page_Down", "description": "Page down"}
            },
            "selection": {
                "select_all": {"key": "<Ctrl><Shift>A", "description": "Select all"},
                "select_word": {"key": "<Ctrl><Shift>W", "description": "Select word"},
                "select_line": {"key": "<Ctrl><Shift>L", "description": "Select line"},
                "clear_selection": {"key": "Escape", "description": "Clear selection"}
            }
        }

    def register_binding(self, action: str, key_combo: str, callback: Callable,
                        description: str = "", category: str = "General") -> bool:
        """Register a new keybinding."""
        binding = KeyBinding(key_combo, action, callback, description, category)

        if not binding.is_valid():
            print(f"Invalid keybinding: {key_combo}")
            return False

        # Check for conflicts
        for existing_action, existing_binding in self.bindings.items():
            if (existing_binding.accelerator == binding.accelerator and
                existing_action != action):
                self.conflicts.append((action, existing_action))
                print(f"Keybinding conflict: {action} conflicts with {existing_action}")
                return False

        self.bindings[action] = binding

        # Organize by category
        if category not in self.categories:
            self.categories[category] = []
        if action not in self.categories[category]:
            self.categories[category].append(action)

        return True

    def unregister_binding(self, action: str) -> bool:
        """Remove a keybinding."""
        if action in self.bindings:
            binding = self.bindings[action]
            del self.bindings[action]

            # Remove from category
            if binding.category in self.categories:
                if action in self.categories[binding.category]:
                    self.categories[binding.category].remove(action)

            return True
        return False

    def get_binding(self, action: str) -> Optional[KeyBinding]:
        """Get a keybinding by action name."""
        return self.bindings.get(action)

    def get_bindings_by_category(self, category: str) -> List[KeyBinding]:
        """Get all bindings in a category."""
        if category not in self.categories:
            return []

        return [self.bindings[action] for action in self.categories[category]
                if action in self.bindings]

    def load_from_config(self, config: Dict[str, Any]) -> None:
        """Load keybindings from configuration."""
        self.bindings.clear()
        self.categories.clear()
        self.conflicts.clear()

        # Load default bindings first
        for category, actions in self.default_bindings.items():
            for action, details in actions.items():
                # We'll set callbacks later when connecting to UI
                self.register_binding(
                    action,
                    details["key"],
                    lambda: None,  # Placeholder callback
                    details["description"],
                    category
                )

        # Override with user config
        user_bindings = config.get("keybindings", {})
        for action, key_combo in user_bindings.items():
            if action in self.bindings:
                # Update existing binding
                self.bindings[action].key_combo = key_combo
                self.bindings[action].accelerator = self.bindings[action]._parse_accelerator(key_combo)

    def connect_to_window(self, window: Gtk.Window, terminal) -> None:
        """Connect all keybindings to a GTK window."""
        # Create accel group if it doesn't exist
        if not hasattr(window, 'accel_group'):
            window.accel_group = Gtk.AccelGroup()
            window.add_accel_group(window.accel_group)

        # Define action callbacks
        def create_callback(action_name):
            def callback():
                binding = self.get_binding(action_name)
                if binding and binding.callback:
                    return binding.callback()
                return False
            return callback

        # Connect all bindings
        for action, binding in self.bindings.items():
            if binding.is_valid():
                key, mod = binding.accelerator
                callback = create_callback(action)
                window.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, callback)

    def get_all_bindings(self) -> Dict[str, KeyBinding]:
        """Get all registered bindings."""
        return self.bindings.copy()

    def get_conflicts(self) -> List[Tuple[str, str]]:
        """Get list of conflicting bindings."""
        return self.conflicts.copy()

    def export_bindings(self) -> Dict[str, str]:
        """Export current bindings as a dictionary."""
        return {action: binding.key_combo for action, binding in self.bindings.items()}

    def reset_to_defaults(self) -> None:
        """Reset all bindings to defaults."""
        self.bindings.clear()
        self.categories.clear()
        self.conflicts.clear()

        for category, actions in self.default_bindings.items():
            for action, details in actions.items():
                self.register_binding(
                    action,
                    details["key"],
                    lambda: None,
                    details["description"],
                    category
                )
