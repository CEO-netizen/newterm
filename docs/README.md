# NewTerm

A highly customizable terminal emulator for Wayland with GPU acceleration and customizable themes.

## Features

- **GPU Acceleration**: Hardware-accelerated rendering for smooth performance
- **Customizable Themes**: Multiple UI themes including Default, Dark, and OLED
- **Tab Management**: Multi-tab interface with customizable tab styling
- **Plugin System**: Extensible plugin architecture for additional functionality
- **Keybinding Management**: Customizable keyboard shortcuts
- **Session Management**: Save and restore terminal sessions
- **Wayland Native**: Built specifically for Wayland compositors

## Installation

### From Source

```bash
git clone https://github.com/CEO-netizen/newterm.git
cd newterm
pip install -e .
```

### From Package (Arch Linux)

```bash
makepkg -si
```

## Usage

Run NewTerm with:

```bash
newterm
```

## Configuration

NewTerm stores configuration in `~/.config/newterm/config.json`. You can customize:

- UI themes (Default, Dark, OLED)
- Terminal colors and fonts
- Keybindings
- Plugin settings
- Performance options

## UI Themes

NewTerm includes several built-in UI themes:

- **Default**: Light theme with traditional colors
- **Dark**: Dark theme for low-light environments
- **OLED**: Ultra-dark theme optimized for OLED displays

### OLED Theme

The OLED theme is specifically designed for OLED displays, featuring:
- Pure black backgrounds (#000000)
- High contrast text for readability
- Reduced eye strain in dark environments
- Optimized for OLED screen technology

## Keybindings

Default keybindings include:

- `Ctrl+Shift+T`: New tab
- `Ctrl+Shift+W`: Close tab
- `Ctrl+Shift+C`: Copy
- `Ctrl+Shift+V`: Paste
- `Ctrl+Shift+F`: Find
- `Ctrl+Shift+P`: Command palette
- `F11`: Toggle fullscreen

## Plugin System

NewTerm supports plugins for extended functionality. Plugins can:
- Add new menu items
- Provide additional themes
- Extend terminal functionality
- Integrate with external tools

## Development

### Requirements

- Python 3.8+
- PyGObject
- VTE3
- GTK+ 3.0

### Building

```bash
python -m build --wheel
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report issues, or suggest features.

## License

This project is licensed under the GNU General Public License v3 (GPLv3).

## Changelog

### Version 0.1.4

- Added OLED UI theme for OLED displays
- Improved theme system with dynamic color application
- Enhanced preferences dialog with UI theme selection
- Updated version numbers across all files

### Version 0.1.3

- Initial release
- Basic terminal functionality
- Plugin system foundation
- Theme support

## Support

For support, please open an issue on GitHub or contact the maintainer.

---

**NewTerm** - A modern, customizable terminal emulator for Wayland
