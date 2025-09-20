"""
NewTerm Configuration Validator Module

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

from typing import Dict, Any, List, Optional, Union

class ConfigValidator:
    """Validates configuration values with graceful error handling."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get the default configuration structure."""
        return {
            "theme": {
                "background_color": "#000000",
                "foreground_color": "#FFFFFF",
                "cursor_color": "#FFFFFF",
                "palette": [
                    "#000000", "#800000", "#008000", "#808000",
                    "#000080", "#800080", "#008080", "#C0C0C0",
                    "#808080", "#FF0000", "#00FF00", "#FFFF00",
                    "#0000FF", "#FF00FF", "#00FFFF", "#FFFFFF"
                ]
            },
            "font": {
                "family": "Monospace",
                "size": 12
            },
            "keybindings": {
                "copy": "<Ctrl><Shift>C",
                "paste": "<Ctrl><Shift>V",
                "new_tab": "<Ctrl><Shift>T",
                "close_tab": "<Ctrl><Shift>W",
                "next_tab": "<Ctrl>Page_Down",
                "prev_tab": "<Ctrl>Page_Up",
                "split_horizontal": "<Ctrl><Alt>H",
                "split_vertical": "<Ctrl><Alt>V",
                "close_pane": "<Ctrl><Alt>Q",
                "zoom_in": "<Ctrl>plus",
                "zoom_out": "<Ctrl>minus",
                "reset_zoom": "<Ctrl>0",
                "find": "<Ctrl><Shift>F",
                "command_palette": "<Ctrl><Shift>P",
                "preferences": "<Ctrl>comma",
                "toggle_fullscreen": "F11",
                "new_window": "<Ctrl><Shift>N",
                "quit": "<Ctrl><Alt>Q",
                "scroll_up": "<Ctrl><Shift>Up",
                "scroll_down": "<Ctrl><Shift>Down",
                "scroll_to_top": "<Ctrl>Home",
                "scroll_to_bottom": "<Ctrl>End",
                "page_up": "Page_Up",
                "page_down": "Page_Down",
                "select_all": "<Ctrl><Shift>A",
                "select_word": "<Ctrl><Alt>W",
                "select_line": "<Ctrl><Shift>L",
                "clear_selection": "Escape",
                "split_pane_h": "<Ctrl><Alt>H",
                "split_pane_v": "<Ctrl><Alt>V"
            },
            "scrollback_lines": 1000,
            "gpu_acceleration": True,
            "restore_session": True,
            "show_menu_bar": True,
            "show_status_bar": False,
            "auto_save_session": True,
            "audible_bell": False,
            "urgent_bell": True,
            "mouse_autohide": False,
            "debug_mode": False,
            "log_commands": False,
            "plugins": {
                "enabled": [],
                "disabled": [],
                "auto_load": True
            },
            "session": {
                "max_tabs": 10,
                "save_on_exit": True,
                "restore_on_start": True
            },
            "performance": {
                "max_scrollback": 10000,
                "terminal_bell": True,
                "cursor_blink": True,
                "cursor_shape": "block"
            }
        }

    def validate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration and merge with defaults gracefully."""
        self.errors = []
        self.warnings = []

        # Start with defaults
        validated_config = self.get_default_config()

        # Merge user config, but only override if values are explicitly set
        self._merge_config(validated_config, config)

        # Validate critical values
        self._validate_theme(validated_config.get('theme', {}))
        self._validate_font(validated_config.get('font', {}))
        self._validate_keybindings(validated_config.get('keybindings', {}))
        self._validate_scrollback(validated_config.get('scrollback_lines'))
        self._validate_gpu_acceleration(validated_config.get('gpu_acceleration'))
        self._validate_session_settings(validated_config.get('session', {}))
        self._validate_plugin_settings(validated_config.get('plugins', {}))
        self._validate_performance_settings(validated_config.get('performance', {}))

        return validated_config

    def _merge_config(self, defaults: Dict[str, Any], user_config: Dict[str, Any]):
        """Merge user config into defaults, only overriding explicitly set values."""
        for key, value in user_config.items():
            if key in defaults:
                if isinstance(defaults[key], dict) and isinstance(value, dict):
                    # Recursively merge nested dictionaries
                    if not defaults[key]:  # If defaults is empty dict, replace entirely
                        defaults[key] = value
                    else:
                        self._merge_config(defaults[key], value)
                else:
                    # For non-dict values, only override if user provided a non-None value
                    if value is not None:
                        defaults[key] = value
            else:
                # Add new keys that aren't in defaults
                defaults[key] = value

    def _validate_theme(self, theme: Dict[str, Any]):
        """Validate theme configuration."""
        if not isinstance(theme, dict):
            return

        # Validate colors
        for color_key in ['background_color', 'foreground_color', 'cursor_color']:
            if color_key in theme:
                color = theme[color_key]
                if not self._is_valid_color(color):
                    self.warnings.append(f"Invalid color format for {color_key}: {color}")

        # Validate palette
        if 'palette' in theme:
            palette = theme['palette']
            if isinstance(palette, list):
                if len(palette) != 16:
                    self.warnings.append(f"Palette should have 16 colors, got {len(palette)}")
                for i, color in enumerate(palette):
                    if not self._is_valid_color(color):
                        self.warnings.append(f"Invalid color in palette at index {i}: {color}")

    def _validate_font(self, font: Dict[str, Any]):
        """Validate font configuration."""
        if not isinstance(font, dict):
            return

        if 'size' in font:
            size = font['size']
            if not isinstance(size, (int, float)) or size <= 0:
                self.warnings.append(f"Font size should be a positive number, got: {size}")

        if 'family' in font:
            family = font['family']
            if not isinstance(family, str) or not family.strip():
                self.warnings.append(f"Font family should be a non-empty string, got: {family}")

    def _validate_keybindings(self, keybindings: Dict[str, Any]):
        """Validate keybinding configuration."""
        if not isinstance(keybindings, dict):
            return

        for action, key_combo in keybindings.items():
            if not isinstance(key_combo, str) or not key_combo.strip():
                self.warnings.append(f"Keybinding for '{action}' should be a non-empty string")

    def _validate_scrollback(self, scrollback):
        """Validate scrollback lines."""
        if scrollback is not None:
            if not isinstance(scrollback, int) or scrollback < 0:
                self.warnings.append(f"Scrollback lines should be a non-negative integer, got: {scrollback}")

    def _validate_gpu_acceleration(self, gpu_acceleration):
        """Validate GPU acceleration setting."""
        if gpu_acceleration is not None:
            if not isinstance(gpu_acceleration, bool):
                self.warnings.append(f"GPU acceleration should be true/false, got: {gpu_acceleration}")

    def _validate_session_settings(self, session: Dict[str, Any]):
        """Validate session configuration."""
        if not isinstance(session, dict):
            return

        if 'max_tabs' in session:
            max_tabs = session['max_tabs']
            if not isinstance(max_tabs, int) or max_tabs < 1 or max_tabs > 50:
                self.warnings.append(f"max_tabs should be between 1 and 50, got: {max_tabs}")

        if 'save_on_exit' in session:
            save_on_exit = session['save_on_exit']
            if not isinstance(save_on_exit, bool):
                self.warnings.append(f"save_on_exit should be true/false, got: {save_on_exit}")

        if 'restore_on_start' in session:
            restore_on_start = session['restore_on_start']
            if not isinstance(restore_on_start, bool):
                self.warnings.append(f"restore_on_start should be true/false, got: {restore_on_start}")

    def _validate_plugin_settings(self, plugins: Dict[str, Any]):
        """Validate plugin configuration."""
        if not isinstance(plugins, dict):
            return

        if 'auto_load' in plugins:
            auto_load = plugins['auto_load']
            if not isinstance(auto_load, bool):
                self.warnings.append(f"auto_load should be true/false, got: {auto_load}")

        if 'enabled' in plugins:
            enabled = plugins['enabled']
            if not isinstance(enabled, list):
                self.warnings.append("enabled should be a list of plugin names")
            else:
                for plugin_name in enabled:
                    if not isinstance(plugin_name, str):
                        self.warnings.append(f"Plugin name should be string, got: {plugin_name}")

        if 'disabled' in plugins:
            disabled = plugins['disabled']
            if not isinstance(disabled, list):
                self.warnings.append("disabled should be a list of plugin names")
            else:
                for plugin_name in disabled:
                    if not isinstance(plugin_name, str):
                        self.warnings.append(f"Plugin name should be string, got: {plugin_name}")

    def _validate_performance_settings(self, performance: Dict[str, Any]):
        """Validate performance configuration."""
        if not isinstance(performance, dict):
            return

        if 'max_scrollback' in performance:
            max_scrollback = performance['max_scrollback']
            if not isinstance(max_scrollback, int) or max_scrollback < 100 or max_scrollback > 1000000:
                self.warnings.append(f"max_scrollback should be between 100 and 1000000, got: {max_scrollback}")

        if 'terminal_bell' in performance:
            terminal_bell = performance['terminal_bell']
            if not isinstance(terminal_bell, bool):
                self.warnings.append(f"terminal_bell should be true/false, got: {terminal_bell}")

        if 'cursor_blink' in performance:
            cursor_blink = performance['cursor_blink']
            if not isinstance(cursor_blink, bool):
                self.warnings.append(f"cursor_blink should be true/false, got: {cursor_blink}")

        if 'cursor_shape' in performance:
            cursor_shape = performance['cursor_shape']
            valid_shapes = ['block', 'ibeam', 'underline']
            if cursor_shape not in valid_shapes:
                self.warnings.append(f"cursor_shape should be one of {valid_shapes}, got: {cursor_shape}")

    def _is_valid_color(self, color) -> bool:
        """Check if a color string is valid."""
        if not isinstance(color, str):
            return False

        # Check hex color format (#RRGGBB or #RGB)
        if color.startswith('#'):
            color = color[1:]
            if len(color) in (3, 6):
                try:
                    int(color, 16)
                    return True
                except ValueError:
                    pass

        return False

    def get_errors(self) -> List[str]:
        """Get validation errors (critical issues)."""
        return self.errors.copy()

    def get_warnings(self) -> List[str]:
        """Get validation warnings (non-critical issues)."""
        return self.warnings.copy()

def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a configuration dictionary."""
    validator = ConfigValidator()
    validated = validator.validate(config)

    # Print warnings but don't fail
    for warning in validator.get_warnings():
        print(f"Config warning: {warning}")

    return validated
