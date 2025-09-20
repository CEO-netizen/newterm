"""
NewTerm Example Plugin

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

This plugin demonstrates the basic plugin API and provides:
- Custom menu items
- Terminal event handling
- Configuration integration
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from plugin_api import PluginBase, TerminalPlugin, UIPlugin, hook

class ExamplePlugin(PluginBase, TerminalPlugin, UIPlugin):
    """Example plugin demonstrating NewTerm plugin capabilities."""

    def get_name(self) -> str:
        return "Example Plugin"

    def get_version(self) -> str:
        return "1.0.0"

    def get_description(self) -> str:
        return "Example plugin demonstrating NewTerm plugin API"

    def on_load(self):
        """Called when the plugin is loaded."""
        print(f"{self.get_name()} v{self.get_version()} loaded!")

        # Show welcome message if configured
        if self.config.get("show_welcome", True):
            GLib.timeout_add(1000, self._show_welcome_message)

    def on_unload(self):
        """Called when the plugin is unloaded."""
        print(f"{self.get_name()} unloaded!")

    def _show_welcome_message(self):
        """Show a welcome message in the active terminal."""
        try:
            # This would need access to the main window's active terminal
            # For now, just print to console
            print("Welcome to NewTerm with plugins!")
            print(self.config.get("custom_message", "Welcome to NewTerm with plugins!"))
        except Exception as e:
            print(f"Error showing welcome message: {e}")
        return False  # Don't repeat

    @hook("terminal_created")
    def on_terminal_created(self, terminal):
        """Called when a new terminal is created."""
        print(f"New terminal created (PID: {terminal.get_pty()})")

        # Add custom styling or behavior to the terminal
        if self.config.get("add_custom_styling", False):
            # This is where you could modify terminal properties
            pass

    @hook("tab_created")
    def on_tab_created(self, tab):
        """Called when a new tab is created."""
        print(f"New tab created: {tab.get_title()}")

    def on_terminal_command(self, terminal, command: str):
        """Called when a command is executed in a terminal."""
        # Log commands if debug mode is enabled
        if self.config.get("log_commands", False):
            print(f"Command executed: {command}")

    def create_menu_items(self):
        """Create custom menu items for this plugin."""
        return [
            {
                "label": "Example Plugin Action",
                "callback": self._on_example_action,
                "separator_before": False,
                "separator_after": False
            },
            {
                "label": "Plugin Settings",
                "callback": self._on_plugin_settings,
                "separator_before": True,
                "separator_after": False
            }
        ]

    def _on_example_action(self):
        """Handle example plugin action."""
        dialog = Gtk.MessageDialog(
            parent=None,  # Would need main window reference
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Example Plugin Action"
        )
        dialog.format_secondary_text("This is an example action from the plugin!")
        dialog.run()
        dialog.destroy()

    def _on_plugin_settings(self):
        """Show plugin settings dialog."""
        dialog = Gtk.MessageDialog(
            parent=None,  # Would need main window reference
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Plugin Settings"
        )
        dialog.format_secondary_text(
            f"Plugin: {self.get_name()}\n"
            f"Version: {self.get_version()}\n"
            f"Author: {self.get_author()}\n"
            f"Config: {self.config}"
        )
        dialog.run()
        dialog.destroy()

    def get_config_schema(self):
        """Get the configuration schema for this plugin."""
        return {
            "type": "object",
            "properties": {
                "show_welcome": {
                    "type": "boolean",
                    "default": True,
                    "description": "Show welcome message on startup"
                },
                "log_commands": {
                    "type": "boolean",
                    "default": False,
                    "description": "Log executed commands"
                },
                "add_custom_styling": {
                    "type": "boolean",
                    "default": False,
                    "description": "Add custom styling to terminals"
                },
                "custom_message": {
                    "type": "string",
                    "default": "Welcome to NewTerm with plugins!",
                    "description": "Custom welcome message"
                }
            }
        }
