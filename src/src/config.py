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
                "new_tab": "<Ctrl><Shift>T"
            },
            "scrollback_lines": 1000,
            "gpu_acceleration": True
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
