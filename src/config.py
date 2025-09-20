"""
NewTerm Configuration Module

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
import shutil

class Config:
    def __init__(self, config_path=None):
        if config_path is None:
            config_dir = os.path.expanduser("~/.config/newterm")
            os.makedirs(config_dir, exist_ok=True)
            self.config_path = os.path.join(config_dir, "config.json")
            # Copy default if not exists
            if not os.path.exists(self.config_path):
                default_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
                if os.path.exists(default_path):
                    shutil.copy(default_path, self.config_path)
        else:
            self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            return self.get_default_config()

    def get_default_config(self):
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

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
