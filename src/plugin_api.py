"""
NewTerm Plugin API Module

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

This module defines the interfaces and base classes for plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from plugin_manager import PluginManager

class PluginBase(ABC):
    """Base class for all plugins."""

    def __init__(self, plugin_manager: 'PluginManager', config: Dict[str, Any]):
        self.plugin_manager = plugin_manager
        self.config = config
        self.enabled = True

    @abstractmethod
    def get_name(self) -> str:
        """Get the plugin name."""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Get the plugin version."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get the plugin description."""
        pass

    def get_author(self) -> str:
        """Get the plugin author."""
        return self.config.get("author", "Unknown")

    def get_dependencies(self) -> List[str]:
        """Get plugin dependencies."""
        return self.config.get("dependencies", [])

    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self.enabled

    def set_enabled(self, enabled: bool):
        """Enable or disable the plugin."""
        self.enabled = enabled

    def on_load(self):
        """Called when the plugin is loaded."""
        pass

    def on_unload(self):
        """Called when the plugin is unloaded."""
        pass

    def on_terminal_created(self, terminal):
        """Called when a new terminal is created."""
        pass

    def on_terminal_destroyed(self, terminal):
        """Called when a terminal is destroyed."""
        pass

    def on_tab_created(self, tab):
        """Called when a new tab is created."""
        pass

    def on_tab_destroyed(self, tab):
        """Called when a tab is destroyed."""
        pass

    def on_keybinding_pressed(self, action: str, key_combo: str) -> bool:
        """Called when a keybinding is pressed. Return True to consume the event."""
        return False

    def get_config_schema(self) -> Dict[str, Any]:
        """Get the configuration schema for this plugin."""
        return {}

class TerminalPlugin(PluginBase):
    """Plugin that extends terminal functionality."""

    def on_terminal_output(self, terminal, text: str):
        """Called when terminal receives output."""
        pass

    def on_terminal_input(self, terminal, text: str):
        """Called when terminal receives input."""
        pass

    def on_terminal_command(self, terminal, command: str):
        """Called when a command is executed."""
        pass

class UIPlugin(PluginBase):
    """Plugin that adds UI elements."""

    def create_menu_items(self) -> List[Dict[str, Any]]:
        """Create menu items for this plugin."""
        return []

    def create_toolbar_items(self) -> List[Dict[str, Any]]:
        """Create toolbar items for this plugin."""
        return []

    def create_status_bar_items(self) -> List[Dict[str, Any]]:
        """Create status bar items for this plugin."""
        return []

class ThemePlugin(PluginBase):
    """Plugin that provides themes."""

    def get_themes(self) -> Dict[str, Dict[str, Any]]:
        """Get themes provided by this plugin."""
        return {}

class KeyBindingPlugin(PluginBase):
    """Plugin that provides keybindings."""

    def get_keybindings(self) -> Dict[str, Dict[str, Any]]:
        """Get keybindings provided by this plugin."""
        return {}

# Plugin event types
class PluginEvent:
    """Plugin event constants."""

    TERMINAL_CREATED = "terminal_created"
    TERMINAL_DESTROYED = "terminal_destroyed"
    TAB_CREATED = "tab_created"
    TAB_DESTROYED = "tab_destroyed"
    KEYBINDING_PRESSED = "keybinding_pressed"
    CONFIG_CHANGED = "config_changed"
    THEME_CHANGED = "theme_changed"

# Plugin hook decorators
def hook(event_type: str):
    """Decorator to register a hook for a plugin event."""
    def decorator(func):
        if not hasattr(func, '_plugin_hooks'):
            func._plugin_hooks = []
        func._plugin_hooks.append(event_type)
        return func
    return decorator

# Plugin configuration schema
PLUGIN_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "version": {"type": "string"},
        "description": {"type": "string"},
        "author": {"type": "string"},
        "dependencies": {
            "type": "array",
            "items": {"type": "string"}
        },
        "enabled": {"type": "boolean"},
        "config": {
            "type": "object",
            "additionalProperties": True
        }
    },
    "required": ["name", "version"]
}
