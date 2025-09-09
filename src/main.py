import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, Vte, GLib, Gdk, Pango
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from config import Config

class TerminalWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="NewTerm")
        self.set_default_size(800, 600)

        # Load config
        self.config = Config()
        print("Loaded config:", self.config.config)

        # Add accel group for keybindings
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)

        # Create menu bar
        self.create_menu_bar()

        # Vte Terminal
        self.terminal = Vte.Terminal()
        self.terminal.set_scrollback_lines(self.config.get('scrollback_lines', 1000))

        # Apply theme
        self.apply_theme()

        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self.terminal)

        # VBox for menu and terminal
        vbox = Gtk.VBox()
        vbox.pack_start(self.menubar, False, False, 0)
        vbox.pack_start(scrolled, True, True, 0)

        self.add(vbox)
        self.show_all()

        # Spawn shell
        self.spawn_shell()

        # Connect keybindings
        self.connect_keybindings()

    def create_menu_bar(self):
        self.menubar = Gtk.MenuBar()

        # File menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)

        new_tab_item = Gtk.MenuItem(label="New Tab")
        new_tab_item.connect("activate", self.on_new_tab)
        file_menu.append(new_tab_item)

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", Gtk.main_quit)
        file_menu.append(quit_item)

        # Edit menu
        edit_menu = Gtk.Menu()
        edit_item = Gtk.MenuItem(label="Edit")
        edit_item.set_submenu(edit_menu)

        copy_item = Gtk.MenuItem(label="Copy")
        copy_item.connect("activate", self.on_copy)
        edit_menu.append(copy_item)

        paste_item = Gtk.MenuItem(label="Paste")
        paste_item.connect("activate", self.on_paste)
        edit_menu.append(paste_item)

        # Preferences menu
        pref_menu = Gtk.Menu()
        pref_item = Gtk.MenuItem(label="Preferences")
        pref_item.set_submenu(pref_menu)

        theme_item = Gtk.MenuItem(label="Theme")
        theme_item.connect("activate", self.on_preferences)
        pref_menu.append(theme_item)

        self.menubar.append(file_item)
        self.menubar.append(edit_item)
        self.menubar.append(pref_item)

    def apply_theme(self):
        theme = self.config.get('theme', {})
        bg = Gdk.RGBA()
        bg.parse(theme.get('background_color', '#000000'))
        self.terminal.set_color_background(bg)

        fg = Gdk.RGBA()
        fg.parse(theme.get('foreground_color', '#FFFFFF'))
        self.terminal.set_color_foreground(fg)

        cursor = Gdk.RGBA()
        cursor.parse(theme.get('cursor_color', '#FFFFFF'))
        self.terminal.set_color_cursor(cursor)

        # Palette
        palette = []
        for color in theme.get('palette', []):
            rgba = Gdk.RGBA()
            rgba.parse(color)
            palette.append(rgba)
        if len(palette) == 16:
            self.terminal.set_colors(fg, bg, palette)

        # Font
        font = self.config.get('font', {})
        font_family = font.get('family', 'Monospace')
        font_size = font.get('size', 12)
        font_desc = Pango.FontDescription()
        font_desc.set_family(font_family)
        font_desc.set_size(font_size * Pango.SCALE)
        print(f"Applying font: {font_family} {font_size}")
        self.terminal.set_font(font_desc)

    def spawn_shell(self):
        # Spawn default shell
        shell = os.environ.get('SHELL', '/bin/bash')
        self.terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            [shell],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )

    def connect_keybindings(self):
        keybindings = self.config.get('keybindings', {})
        # Connect keybindings using accelerators
        for action, accel in keybindings.items():
            if action == 'copy':
                key, mod = Gtk.accelerator_parse(accel)
                self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, self.on_copy)
            elif action == 'paste':
                key, mod = Gtk.accelerator_parse(accel)
                self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, self.on_paste)
            elif action == 'new_tab':
                key, mod = Gtk.accelerator_parse(accel)
                self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, self.on_new_tab)

    def on_new_tab(self, widget):
        # Placeholder for new tab
        print("New tab not implemented yet")

    def on_copy(self, widget):
        self.terminal.copy_clipboard()

    def on_paste(self, widget):
        self.terminal.paste_clipboard()

    def on_preferences(self, widget):
        # Placeholder for preferences dialog
        print("Preferences dialog not implemented yet")

def main():
    # Ensure GPU acceleration if enabled
    if Config().get('gpu_acceleration', True):
        os.environ['GDK_GL'] = 'always'
    win = TerminalWindow()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()
