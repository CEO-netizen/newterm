"""
NewTerm - A highly customizable terminal emulator

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
gi.require_version('Vte', '2.91')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, Vte, GLib, Gdk, Pango
import os
import sys
import signal
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config
from keybinding_manager import KeyBindingManager
from tab_manager import TabManager
from plugin_manager import PluginManager
from preferences_dialog import PreferencesDialog
from session_manager import SessionManager

class TerminalWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="NewTerm")
        self.set_default_size(800, 600)

        # Initialize managers
        self.config = Config()
        self.keybinding_manager = KeyBindingManager()
        self.plugin_manager = PluginManager()
        self.session_manager = SessionManager(self.config)

        # Load keybindings from config
        self.keybinding_manager.load_from_config(self.config.config)

        # Load plugins
        self.plugin_manager.discover_plugins()
        plugins = self.plugin_manager.discover_plugins()
        for plugin_config in plugins:
            self.plugin_manager.load_plugin(plugin_config)

        # Create tab manager
        self.tab_manager = TabManager(self.config)

        # Create UI
        self.create_menu_bar()
        self.create_main_ui()

        # Connect keybindings
        self.keybinding_manager.connect_to_window(self, None)

        # Apply UI theme
        self.apply_ui_theme()

        # Set up window properties
        self.show_all()

        # Restore session or create initial tab
        self.restore_or_create_initial_tab()

        # Connect plugin events
        self.connect_plugin_events()

    def create_menu_bar(self):
        """Create the menu bar with all menu items."""
        self.menubar = Gtk.MenuBar()

        # File menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)

        new_tab_item = Gtk.MenuItem(label="New Tab")
        new_tab_item.connect("activate", self.on_new_tab)
        file_menu.append(new_tab_item)

        new_window_item = Gtk.MenuItem(label="New Window")
        new_window_item.connect("activate", self.on_new_window)
        file_menu.append(new_window_item)

        file_menu.append(Gtk.SeparatorMenuItem())

        close_tab_item = Gtk.MenuItem(label="Close Tab")
        close_tab_item.connect("activate", self.on_close_tab)
        file_menu.append(close_tab_item)

        file_menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
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

        edit_menu.append(Gtk.SeparatorMenuItem())

        select_all_item = Gtk.MenuItem(label="Select All")
        select_all_item.connect("activate", self.on_select_all)
        edit_menu.append(select_all_item)

        # View menu
        view_menu = Gtk.Menu()
        view_item = Gtk.MenuItem(label="View")
        view_item.set_submenu(view_menu)

        fullscreen_item = Gtk.MenuItem(label="Toggle Fullscreen")
        fullscreen_item.connect("activate", self.on_toggle_fullscreen)
        view_menu.append(fullscreen_item)

        # Tools menu
        tools_menu = Gtk.Menu()
        tools_item = Gtk.MenuItem(label="Tools")
        tools_item.set_submenu(tools_menu)

        command_palette_item = Gtk.MenuItem(label="Command Palette")
        command_palette_item.connect("activate", self.on_command_palette)
        tools_menu.append(command_palette_item)

        # Preferences menu
        pref_menu = Gtk.Menu()
        pref_item = Gtk.MenuItem(label="Preferences")
        pref_item.set_submenu(pref_menu)

        preferences_item = Gtk.MenuItem(label="Settings")
        preferences_item.connect("activate", self.on_preferences)
        pref_menu.append(preferences_item)

        # Add plugin menu items
        self._add_plugin_menu_items(pref_menu)

        # Help menu
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Help")
        help_item.set_submenu(help_menu)

        about_item = Gtk.MenuItem(label="About")
        about_item.connect("activate", self.on_about)
        help_menu.append(about_item)

        # Add all menus
        self.menubar.append(file_item)
        self.menubar.append(edit_item)
        self.menubar.append(view_item)
        self.menubar.append(tools_item)
        self.menubar.append(pref_item)
        self.menubar.append(help_item)

    def _add_plugin_menu_items(self, parent_menu):
        """Add menu items from plugins."""
        for plugin in self.plugin_manager.get_enabled_plugins().values():
            if hasattr(plugin, 'create_menu_items'):
                menu_items = plugin.create_menu_items()
                for item in menu_items:
                    menu_item = Gtk.MenuItem(label=item.get('label', 'Plugin Item'))
                    menu_item.connect("activate", item.get('callback', lambda: None))
                    parent_menu.append(menu_item)

    def create_main_ui(self):
        """Create the main user interface."""
        # Main vertical box
        main_vbox = Gtk.VBox()

        # Add menu bar
        if self.config.get('show_menu_bar', True):
            main_vbox.pack_start(self.menubar, False, False, 0)

        # Create notebook for tabs
        self.notebook = self.tab_manager.create_notebook()
        main_vbox.pack_start(self.notebook, True, True, 0)

        # Status bar (optional)
        if self.config.get('show_status_bar', False):
            self.status_bar = Gtk.Statusbar()
            main_vbox.pack_start(self.status_bar, False, False, 0)

        self.add(main_vbox)

        # Show all widgets
        self.show_all()

    def apply_ui_theme(self):
        """Apply the current UI theme to menus and window."""
        ui_theme_name = self.config.get('ui_theme', 'Default')
        ui_themes = self.config.get('ui_themes', {})
        theme_colors = ui_themes.get(ui_theme_name, ui_themes.get('Default', {}))

        if not theme_colors:
            return

        # Apply CSS styling for UI elements
        css = f"""
        /* Menu bar styling */
        .menubar {{
            background-color: {theme_colors.get('menu_bar_bg', '#F5F5F5')};
            color: {theme_colors.get('menu_bar_fg', '#000000')};
            border-bottom: 1px solid {theme_colors.get('tab_bar_bg', '#E8E8E8')};
        }}

        /* Menu items */
        .menubar menuitem {{
            background-color: {theme_colors.get('menu_item_bg', '#FFFFFF')};
            color: {theme_colors.get('menu_item_fg', '#000000')};
        }}

        .menubar menuitem:hover {{
            background-color: {theme_colors.get('menu_item_hover_bg', '#E0E0E0')};
            color: {theme_colors.get('menu_item_hover_fg', '#000000')};
        }}

        /* Notebook tabs */
        .notebook tab {{
            background-color: {theme_colors.get('tab_bg', '#D0D0D0')};
            color: {theme_colors.get('tab_fg', '#000000')};
            padding: 4px 8px;
            border: 1px solid {theme_colors.get('tab_bar_bg', '#E8E8E8')};
            border-bottom: none;
        }}

        .notebook tab:hover {{
            background-color: {theme_colors.get('tab_hover_bg', '#C0C0C0')};
            color: {theme_colors.get('tab_hover_fg', '#000000')};
        }}

        .notebook tab:checked {{
            background-color: {theme_colors.get('tab_active_bg', '#FFFFFF')};
            color: {theme_colors.get('tab_active_fg', '#000000')};
        }}

        /* Tab close buttons */
        .tab-close-button {{
            background-color: {theme_colors.get('button_bg', '#E0E0E0')};
            color: {theme_colors.get('button_fg', '#000000')};
            border: none;
            border-radius: 2px;
            padding: 2px 4px;
        }}

        .tab-close-button:hover {{
            background-color: {theme_colors.get('button_bg', '#E0E0E0')};
        }}

        /* Window background */
        .window {{
            background-color: {theme_colors.get('window_bg', '#FFFFFF')};
        }}
        """

        # Apply CSS to the window
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css.encode())

        # Get the screen and apply to all widgets
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Apply to specific widgets
        if hasattr(self, 'menubar') and self.menubar:
            self.menubar.get_style_context().add_provider(
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        if hasattr(self, 'notebook') and self.notebook:
            self.notebook.get_style_context().add_provider(
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def restore_or_create_initial_tab(self):
        """Restore previous session or create initial tab."""
        if self.config.get('restore_session', True):
            session_data = self.session_manager.restore_session()
            if session_data and session_data.get('tabs'):
                # Restore tabs from session
                for i, tab_data in enumerate(session_data.get('tabs', [])):
                    title = tab_data.get('title', 'Terminal')
                    directory = tab_data.get('working_directory', None)
                    tab = self.tab_manager.new_tab(title, directory)

                # Set active tab
                active_index = session_data.get('active_tab', 0)
                if 0 <= active_index < len(self.tab_manager.get_tabs()):
                    self.tab_manager.set_active_tab(self.tab_manager.get_tabs()[active_index])
            else:
                # Create initial tab
                tab = self.tab_manager.new_tab()
                print(f"Created initial tab: {tab}")
        else:
            # Create initial tab
            tab = self.tab_manager.new_tab()
            print(f"Created initial tab: {tab}")

        # Ensure we have at least one tab and it's visible
        if len(self.tab_manager.get_tabs()) == 0:
            print("No tabs found, creating emergency tab")
            tab = self.tab_manager.new_tab()
            print(f"Emergency tab created: {tab}")

        # Make sure the notebook is visible
        if self.notebook:
            self.notebook.show_all()

    def connect_plugin_events(self):
        """Connect plugin events to the plugin manager."""
        # Terminal events
        for tab in self.tab_manager.get_tabs():
            self.plugin_manager.emit_event("terminal_created", terminal=tab.get_terminal())
            tab.get_terminal().connect("child-exited", self.on_terminal_exited)

    def on_terminal_exited(self, terminal, status):
        """Handle terminal process exit."""
        self.plugin_manager.emit_event("terminal_destroyed", terminal=terminal)

    def on_new_tab(self, widget):
        """Handle new tab creation."""
        tab = self.tab_manager.new_tab()
        self.plugin_manager.emit_event("tab_created", tab=tab)

    def on_new_window(self, widget):
        """Handle new window creation."""
        # Create new instance
        os.system(f"{sys.executable} {sys.argv[0]} &")

    def on_close_tab(self, widget):
        """Handle tab closing."""
        active_tab = self.tab_manager.get_active_tab()
        if active_tab:
            self.tab_manager.close_tab(active_tab)
            self.plugin_manager.emit_event("tab_destroyed", tab=active_tab)

    def on_quit(self, widget):
        """Handle application quit."""
        # Save session
        tabs_data = []
        for tab in self.tab_manager.get_tabs():
            tabs_data.append({
                'title': tab.get_title(),
                'working_directory': tab.working_directory
            })

        active_tab_index = 0
        active_tab = self.tab_manager.get_active_tab()
        if active_tab:
            try:
                active_tab_index = self.tab_manager.get_tabs().index(active_tab)
            except ValueError:
                pass

        self.session_manager.save_session(tabs_data, active_tab_index)
        Gtk.main_quit()

    def on_copy(self, widget=None):
        """Handle copy action."""
        active_tab = self.tab_manager.get_active_tab()
        if active_tab:
            active_tab.get_terminal().copy_clipboard()

    def on_paste(self, widget=None):
        """Handle paste action."""
        active_tab = self.tab_manager.get_active_tab()
        if active_tab:
            active_tab.get_terminal().paste_clipboard()

    def on_select_all(self, widget=None):
        """Handle select all action."""
        active_tab = self.tab_manager.get_active_tab()
        if active_tab:
            active_tab.get_terminal().select_all()

    def on_toggle_fullscreen(self, widget=None):
        """Handle fullscreen toggle."""
        if self.is_fullscreen():
            self.unfullscreen()
        else:
            self.fullscreen()

    def on_command_palette(self, widget=None):
        """Handle command palette."""
        # TODO: Implement command palette
        print("Command palette not implemented yet")

    def on_preferences(self, widget=None):
        """Handle preferences dialog."""
        dialog = PreferencesDialog(
            self,
            self.config,
            self.keybinding_manager,
            self.plugin_manager
        )

        def on_config_changed(new_config):
            """Handle configuration changes."""
            # Apply new config to all tabs
            for tab in self.tab_manager.get_tabs():
                tab.apply_theme()

            # Apply UI theme changes
            self.apply_ui_theme()

            # Reload keybindings
            self.keybinding_manager.load_from_config(new_config)
            self.keybinding_manager.connect_to_window(self, None)

            # Notify plugins
            self.plugin_manager.emit_event("config_changed", config=new_config)

        dialog.set_config_changed_callback(on_config_changed)
        dialog.show()

    def on_about(self, widget=None):
        """Handle about dialog."""
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name("NewTerm")
        about_dialog.set_version("2.0.1")
        about_dialog.set_comments("A highly customizable terminal emulator")
        about_dialog.set_website("https://github.com/CEO-netizen/newterm")
        about_dialog.set_copyright("Copyright © 2024 NewTerm Team")

        about_dialog.run()
        about_dialog.destroy()

def main():
    """Main application entry point."""
    # Set up signal handlers
    def signal_handler(signum, frame):
        Gtk.main_quit()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Ensure GPU acceleration if enabled
    if Config().get('gpu_acceleration', True):
        os.environ['GDK_GL'] = 'always'

    # Create and show main window
    win = TerminalWindow()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()
