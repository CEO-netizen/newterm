# NewTerm - Advanced Terminal Emulator

A highly customizable and feature-rich terminal emulator built with Python, GTK, and VTE, designed to be compatible with Wayland and GPU-accelerated.

## Features

### Core Terminal Features
- Full terminal emulation with VTE
- GPU acceleration for smooth performance
- Wayland compatible GUI
- Session management (save/restore tabs and state)
- Multiple tab support with drag-and-drop
- Context menus for tabs and terminals

### Advanced Keybinding System
- Comprehensive keybinding management
- Configurable shortcuts for all actions
- Support for complex key combinations (Ctrl+Alt+Shift+key)
- Import/export keybinding configurations
- Conflict detection and resolution

### Plugin System
- Extensible plugin architecture
- Plugin API for custom functionality
- Plugin management interface
- Security sandboxing for plugins
- Auto-loading and dependency management

### Advanced Preferences
- Comprehensive settings dialog with multiple tabs
- Real-time preview of changes
- Theme customization with color pickers
- Font selection and sizing
- Performance and debug settings
- Plugin management interface

### User Interface
- Modern tabbed interface
- Customizable menu bar
- Status bar support
- Fullscreen mode
- Command palette (planned)
- Multiple window support

## Requirements

- Python 3.8+
- PyGObject (GTK bindings for Python)
- VTE (Virtual Terminal Emulator)
- GTK 3.0+

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   sudo pacman -S vte3  # On Arch Linux
   sudo apt install libvte-2.91-dev  # On Ubuntu/Debian
   ```

2. Run the terminal:
   ```bash
   python src/main.py
   ```

## Usage

### Basic Usage
- The terminal opens with your default shell
- Use tabs to organize multiple terminal sessions
- Right-click on tabs or terminals for context menus
- Use the menu bar for all operations

### Keyboard Shortcuts
- `Ctrl+Shift+T`: New tab
- `Ctrl+Shift+W`: Close current tab
- `Ctrl+Page_Down/Up`: Switch between tabs
- `Ctrl+Shift+C/V`: Copy/paste
- `Ctrl+Shift+P`: Command palette
- `Ctrl+comma`: Open preferences
- `F11`: Toggle fullscreen
- `Ctrl+Shift+N`: New window
- `Ctrl+Shift+Q`: Quit

### Session Management
- Sessions are automatically saved on exit
- Previous sessions restore on startup (configurable)
- Maximum number of tabs can be configured
- Working directories are preserved per tab

## Configuration

Edit `~/.config/newterm/config.json` to customize:

### Theme Configuration
```json
"theme": {
  "background_color": "#000000",
  "foreground_color": "#FFFFFF",
  "cursor_color": "#FFFFFF",
  "palette": ["#000000", "#800000", ...]
}
```

### Font Configuration
```json
"font": {
  "family": "Monospace",
  "size": 12
}
```

### Keybindings Configuration
```json
"keybindings": {
  "copy": "<Ctrl><Shift>C",
  "paste": "<Ctrl><Shift>V",
  "new_tab": "<Ctrl><Shift>T",
  "close_tab": "<Ctrl><Shift>W",
  "next_tab": "<Ctrl>Page_Down",
  "prev_tab": "<Ctrl>Page_Up",
  "preferences": "<Ctrl>comma",
  "toggle_fullscreen": "F11"
}
```

### Session Configuration
```json
"session": {
  "max_tabs": 10,
  "save_on_exit": true,
  "restore_on_start": true
}
```

### Plugin Configuration
```json
"plugins": {
  "enabled": ["plugin1", "plugin2"],
  "disabled": ["plugin3"],
  "auto_load": true
}
```

### Performance Configuration
```json
"performance": {
  "max_scrollback": 10000,
  "terminal_bell": true,
  "cursor_blink": true,
  "cursor_shape": "block"
}
```

## Plugin Development

NewTerm supports plugins to extend functionality. Create a plugin by:

1. Create a plugin directory in `~/.config/newterm/plugins/`
2. Add a `plugin.json` configuration file
3. Implement your plugin class inheriting from `PluginBase`
4. Use the plugin API for terminal events and UI integration

Example plugin structure:
```
my_plugin/
├── plugin.json
└── plugin.py
```

## Development

### Architecture
- **KeyBindingManager**: Handles all keyboard shortcuts and actions
- **TabManager**: Manages multiple terminal tabs and sessions
- **PluginManager**: Loads and manages plugins
- **SessionManager**: Handles session save/restore functionality
- **PreferencesDialog**: Advanced settings interface

### Current Features Status
- Full keybinding system
- Tab support with session management
- Plugin system with API
- Advanced preferences dialog
- Theme and font customization
- GPU acceleration support
- Wayland compatibility

### Future Enhancements
- Command palette implementation
- Split pane support
- Search functionality
- Plugin marketplace
- Additional terminal features

## Compatibility

Built with GTK and VTE, supporting:
- Wayland native support
- X11 compatibility
- GPU acceleration for optimal performance
- Modern Linux desktop environments
- Python 3.8+ compatibility

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see the development documentation for:
- Plugin development guidelines
- Code style and architecture
- Testing procedures
- Feature request process

## Feature requests
For feature requests contact me at one of three ways:

- Email: zeroday0x00@disroot.org
- Jabber/xmpp: cr4ck3d-ng@xmpp.is
- Telegram: @znodx