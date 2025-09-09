# NewTerm - Custom Terminal Emulator

A highly customizable terminal emulator built with Python, GTK, and VTE, designed to be compatible with Wayland and GPU-accelerated.

## Features

- Full terminal emulation with VTE
- Highly customizable themes and fonts
- Menu bar with copy/paste and preferences
- GPU acceleration for smooth performance
- Configurable keybindings
- Wayland compatible GUI

## Requirements

- Python 3.x
- PyGObject (GTK bindings for Python)
- VTE (Virtual Terminal Emulator)

## Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   sudo pacman -S vte3  # On Arch Linux
   ```

2. Run the terminal:
   ```
   python src/main.py
   ```

## Usage

- The terminal opens with your default shell
- Use the menu bar for copy/paste operations
- Access preferences to customize appearance
- All standard terminal features are supported

## Customization

Edit `~/.config/newterm/config.json` to customize:

### Theme
```json
"theme": {
  "background_color": "#000000",
  "foreground_color": "#FFFFFF",
  "cursor_color": "#FFFFFF",
  "palette": ["#000000", "#800000", ...]
}
```

### Font
```json
"font": {
  "family": "Monospace",
  "size": 12
}
```

### Keybindings
```json
"keybindings": {
  "copy": "<Ctrl><Shift>C",
  "paste": "<Ctrl><Shift>V",
  "new_tab": "<Ctrl><Shift>T"
}
```

### Other Options
- `scrollback_lines`: Number of lines to keep in scrollback buffer
- `gpu_acceleration`: Enable GPU acceleration (default: true)

## Development

Current features:
- Theme and font customization
- Menu bar with basic operations
- GPU acceleration support
- Configurable keybindings (basic implementation)

Future enhancements:
- Full keybinding system
- Tab support
- Plugin system
- Advanced preferences dialog

## Compatibility

Built with GTK and VTE, supporting Wayland natively with GPU acceleration for optimal performance on modern Linux desktop environments.
