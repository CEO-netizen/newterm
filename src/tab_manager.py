"""
NewTerm Tab Manager Module

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
from gi.repository import Gtk, Vte, GLib, Gdk, Pango
import os
import signal
import json
from typing import Dict, Any, List, Optional, Callable
from config import Config

class TerminalTab:
    """Represents a single terminal tab."""

    def __init__(self, tab_manager, title: str = "Terminal"):
        self.tab_manager = tab_manager
        self.title = title
        self.terminal = Vte.Terminal()
        self.pid = None
        self.working_directory = os.environ.get('HOME', '/')

        # Configure terminal
        self.terminal.set_scrollback_lines(self.tab_manager.config.get('scrollback_lines', 1000))
        self.apply_theme()

        # Connect signals
        self.terminal.connect("child-exited", self.on_child_exited)
        self.terminal.connect("window-title-changed", self.on_title_changed)
        self.terminal.connect("button-press-event", self.on_button_press)

        # Spawn shell
        self.spawn_shell()

    def apply_theme(self):
        """Apply current theme to terminal."""
        theme = self.tab_manager.config.get('theme', {})
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
        font = self.tab_manager.config.get('font', {})
        font_family = font.get('family', 'Monospace')
        font_size = font.get('size', 12)
        font_desc = Pango.FontDescription()
        font_desc.set_family(font_family)
        font_desc.set_size(font_size * Pango.SCALE)
        self.terminal.set_font(font_desc)

    def spawn_shell(self):
        """Spawn the shell process."""
        shell = os.environ.get('SHELL', '/bin/bash')

        # Create environment variables
        env = os.environ.copy()
        env['TERM'] = 'xterm-256color'
        env['COLORTERM'] = 'truecolor'

        # Convert environment to the format expected by VTE
        env_array = [f"{k}={v}" for k, v in env.items()]

        try:
            self.pid = self.terminal.spawn_sync(
                Vte.PtyFlags.DEFAULT,
                self.working_directory,
                [shell],
                env_array,
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,
                None,
            )[1]
        except Exception as e:
            print(f"Error spawning shell: {e}")
            # Fallback to simpler spawn
            try:
                self.pid = self.terminal.spawn_sync(
                    Vte.PtyFlags.DEFAULT,
                    self.working_directory,
                    [shell],
                    [],
                    GLib.SpawnFlags.DEFAULT,
                    None,
                    None,
                )[1]
            except Exception as e2:
                print(f"Fallback spawn also failed: {e2}")
                self.pid = None

    def on_child_exited(self, terminal, status):
        """Handle child process exit."""
        self.pid = None
        print(f"Shell exited with status: {status}")

    def on_title_changed(self, terminal):
        """Handle terminal title changes."""
        title = self.terminal.get_window_title()
        if title:
            self.title = title
            self.tab_manager.update_tab_title(self)

    def on_button_press(self, terminal, event):
        """Handle mouse button press events."""
        if event.button == 3:  # Right click
            self.show_context_menu(event)
            return True
        return False

    def show_context_menu(self, event):
        """Show context menu for the tab."""
        menu = Gtk.Menu()

        # Copy
        copy_item = Gtk.MenuItem(label="Copy")
        copy_item.connect("activate", lambda x: self.terminal.copy_clipboard())
        menu.append(copy_item)

        # Paste
        paste_item = Gtk.MenuItem(label="Paste")
        paste_item.connect("activate", lambda x: self.terminal.paste_clipboard())
        menu.append(paste_item)

        menu.append(Gtk.SeparatorMenuItem())

        # Close Tab
        close_item = Gtk.MenuItem(label="Close Tab")
        close_item.connect("activate", lambda x: self.tab_manager.close_tab(self))
        menu.append(close_item)

        # New Tab
        new_tab_item = Gtk.MenuItem(label="New Tab")
        new_tab_item.connect("activate", lambda x: self.tab_manager.new_tab())
        menu.append(new_tab_item)

        menu.show_all()
        menu.popup_at_pointer(event)

    def get_terminal(self) -> Vte.Terminal:
        """Get the terminal widget."""
        return self.terminal

    def set_title(self, title: str):
        """Set the tab title."""
        self.title = title
        self.tab_manager.update_tab_title(self)

    def get_title(self) -> str:
        """Get the tab title."""
        return self.title

    def focus(self):
        """Focus this tab."""
        self.tab_manager.set_active_tab(self)

class TabManager:
    """Manages multiple terminal tabs."""

    def __init__(self, config: Config):
        self.config = config
        self.tabs: List[TerminalTab] = []
        self.active_tab: Optional[TerminalTab] = None
        self.notebook: Optional[Gtk.Notebook] = None
        self.tab_close_buttons: Dict[TerminalTab, Gtk.Button] = {}



    def create_notebook(self) -> Gtk.Notebook:
        """Create the notebook widget for tabs."""
        if self.notebook is None:
            self.notebook = Gtk.Notebook()
            self.notebook.set_scrollable(True)
            self.notebook.set_show_tabs(True)
            self.notebook.set_tab_pos(Gtk.PositionType.TOP)

            # Connect signals
            self.notebook.connect("switch-page", self.on_tab_switched)
            self.notebook.connect("page-removed", self.on_tab_removed)

            # Style the notebook
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(b"""
                .notebook tab {
                    padding: 4px 8px;
                    border: 1px solid #555;
                    background-color: #333;
                    color: #fff;
                }
                .notebook tab:active {
                    background-color: #555;
                }
            """)
            self.notebook.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        return self.notebook

    def new_tab(self, title: str = "Terminal", directory: str = None) -> TerminalTab:
        """Create a new tab."""
        tab = TerminalTab(self, title)

        if directory:
            tab.working_directory = directory

        # Create tab label with close button
        tab_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        tab_label = Gtk.Label(label=title)
        tab_label_box.pack_start(tab_label, True, True, 0)

        # Close button
        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.set_focus_on_click(False)
        close_button.add(Gtk.Label(label="×"))
        close_button.get_style_context().add_class("tab-close-button")
        close_button.connect("clicked", lambda btn: self.close_tab(tab))
        tab_label_box.pack_start(close_button, False, False, 0)

        # Add to notebook
        page_num = self.notebook.append_page(tab.get_terminal(), tab_label_box)
        self.notebook.set_tab_reorderable(tab.get_terminal(), True)
        self.notebook.set_tab_detachable(tab.get_terminal(), True)

        # Store references
        self.tabs.append(tab)
        self.tab_close_buttons[tab] = close_button

        # Set as active if first tab
        if len(self.tabs) == 1:
            self.set_active_tab(tab)

        return tab

    def close_tab(self, tab: Optional[TerminalTab] = None) -> bool:
        """Close a tab."""
        if tab is None:
            tab = self.active_tab

        if not tab:
            return False

        # Don't close if it's the last tab
        if len(self.tabs) == 1:
            return False

        # Find tab index
        page_num = self.notebook.page_num(tab.get_terminal())

        # Remove from notebook
        self.notebook.remove_page(page_num)

        # Clean up
        if tab in self.tabs:
            self.tabs.remove(tab)

        if tab in self.tab_close_buttons:
            del self.tab_close_buttons[tab]

        # Kill process if still running
        if tab.pid:
            try:
                os.kill(tab.pid, signal.SIGTERM)
            except:
                pass

        # Set new active tab
        if self.tabs:
            new_index = min(page_num, len(self.tabs) - 1)
            self.set_active_tab(self.tabs[new_index])

        return True

    def set_active_tab(self, tab: TerminalTab):
        """Set the active tab."""
        if tab in self.tabs:
            self.active_tab = tab
            page_num = self.notebook.page_num(tab.get_terminal())
            self.notebook.set_current_page(page_num)

    def get_active_tab(self) -> Optional[TerminalTab]:
        """Get the currently active tab."""
        return self.active_tab

    def update_tab_title(self, tab: TerminalTab):
        """Update a tab's title in the UI."""
        if tab in self.tab_close_buttons:
            page_num = self.notebook.page_num(tab.get_terminal())
            tab_label = self.notebook.get_tab_label(tab.get_terminal())
            if tab_label:
                children = tab_label.get_children()
                if children:
                    label = children[0]
                    if isinstance(label, Gtk.Label):
                        label.set_text(tab.get_title())

    def on_tab_switched(self, notebook, page, page_num):
        """Handle tab switching."""
        if 0 <= page_num < len(self.tabs):
            self.active_tab = self.tabs[page_num]

    def on_tab_removed(self, notebook, child, page_num):
        """Handle tab removal."""
        # Clean up references
        for i, tab in enumerate(self.tabs):
            if tab.get_terminal() == child:
                if tab in self.tab_close_buttons:
                    del self.tab_close_buttons[tab]
                self.tabs.remove(tab)
                break

    def get_tabs(self) -> List[TerminalTab]:
        """Get all tabs."""
        return self.tabs.copy()

    def next_tab(self) -> bool:
        """Switch to next tab."""
        if not self.tabs or not self.active_tab:
            return False

        current_index = self.tabs.index(self.active_tab)
        next_index = (current_index + 1) % len(self.tabs)
        self.set_active_tab(self.tabs[next_index])
        return True

    def previous_tab(self) -> bool:
        """Switch to previous tab."""
        if not self.tabs or not self.active_tab:
            return False

        current_index = self.tabs.index(self.active_tab)
        prev_index = (current_index - 1) % len(self.tabs)
        self.set_active_tab(self.tabs[prev_index])
        return True



    def get_notebook(self) -> Gtk.Notebook:
        """Get the notebook widget."""
        return self.notebook
