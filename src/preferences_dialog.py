"""
NewTerm Preferences Dialog Module

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
from gi.repository import Gtk, Gdk, Pango
import json
import os
from typing import Dict, Any, List, Optional, Callable
from config import Config
from keybinding_manager import KeyBindingManager
from plugin_manager import PluginManager

class PreferencesDialog:
    """Advanced preferences dialog for NewTerm."""

    def __init__(self, parent_window: Gtk.Window, config: Config,
                 keybinding_manager: KeyBindingManager, plugin_manager: PluginManager):
        self.parent = parent_window
        self.config = config
        self.keybinding_manager = keybinding_manager
        self.plugin_manager = plugin_manager
        self.dialog = None
        self.current_config = None

        # UI components
        self.theme_combo = None
        self.font_family_entry = None
        self.font_size_spin = None
        self.keybinding_tree = None
        self.keybinding_store = None
        self.plugin_tree = None
        self.plugin_store = None

        # Callbacks
        self.on_config_changed: Optional[Callable] = None

    def show(self):
        """Show the preferences dialog."""
        self.current_config = json.loads(json.dumps(self.config.config))  # Deep copy

        self.dialog = Gtk.Dialog(
            title="Preferences",
            parent=self.parent,
            flags=0
        )
        self.dialog.set_default_size(800, 600)
        self.dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.dialog.add_button("Apply", Gtk.ResponseType.APPLY)
        self.dialog.add_button("OK", Gtk.ResponseType.OK)

        # Create notebook for different preference categories
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.LEFT)

        # General tab
        general_tab = self._create_general_tab()
        notebook.append_page(general_tab, Gtk.Label(label="General"))

        # Appearance tab
        appearance_tab = self._create_appearance_tab()
        notebook.append_page(appearance_tab, Gtk.Label(label="Appearance"))

        # Keybindings tab
        keybindings_tab = self._create_keybindings_tab()
        notebook.append_page(keybindings_tab, Gtk.Label(label="Keybindings"))

        # Plugins tab
        plugins_tab = self._create_plugins_tab()
        notebook.append_page(plugins_tab, Gtk.Label(label="Plugins"))

        # Advanced tab
        advanced_tab = self._create_advanced_tab()
        notebook.append_page(advanced_tab, Gtk.Label(label="Advanced"))

        self.dialog.get_content_area().pack_start(notebook, True, True, 0)
        self.dialog.show_all()

        # Connect signals
        self.dialog.connect("response", self._on_response)

    def _create_general_tab(self) -> Gtk.Widget:
        """Create the general preferences tab."""
        frame = Gtk.Frame(label="General Settings")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        frame.add(vbox)

        # Startup options
        startup_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.restore_session_check = Gtk.CheckButton(label="Restore previous session on startup")
        self.restore_session_check.set_active(self.current_config.get('restore_session', True))
        startup_box.pack_start(self.restore_session_check, False, False, 0)

        self.show_menu_bar_check = Gtk.CheckButton(label="Show menu bar")
        self.show_menu_bar_check.set_active(self.current_config.get('show_menu_bar', True))
        startup_box.pack_start(self.show_menu_bar_check, False, False, 0)

        self.gpu_acceleration_check = Gtk.CheckButton(label="Enable GPU acceleration")
        self.gpu_acceleration_check.set_active(self.current_config.get('gpu_acceleration', True))
        startup_box.pack_start(self.gpu_acceleration_check, False, False, 0)

        vbox.pack_start(startup_box, False, False, 0)

        # Scrollback lines
        scrollback_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        scrollback_label = Gtk.Label(label="Scrollback lines:")
        scrollback_label.set_xalign(0)

        scrollback_adj = Gtk.Adjustment(
            value=self.current_config.get('scrollback_lines', 1000),
            lower=100,
            upper=100000,
            step_increment=100,
            page_increment=1000
        )
        self.scrollback_spin = Gtk.SpinButton(adjustment=scrollback_adj)
        self.scrollback_spin.set_digits(0)

        scrollback_box.pack_start(scrollback_label, False, False, 0)
        scrollback_box.pack_start(self.scrollback_spin, False, False, 0)

        vbox.pack_start(scrollback_box, False, False, 0)

        return frame

    def _create_appearance_tab(self) -> Gtk.Widget:
        """Create the appearance preferences tab."""
        frame = Gtk.Frame(label="Appearance Settings")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        frame.add(vbox)

        # Theme selection
        theme_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        theme_label = Gtk.Label(label="Theme:")
        theme_label.set_xalign(0)

        self.theme_combo = Gtk.ComboBoxText()
        themes = self._get_available_themes()
        for theme_name in themes:
            self.theme_combo.append_text(theme_name)

        current_theme = self.current_config.get('theme_name', 'Default')
        self.theme_combo.set_active(themes.index(current_theme) if current_theme in themes else 0)

        theme_box.pack_start(theme_label, False, False, 0)
        theme_box.pack_start(self.theme_combo, False, False, 0)
        vbox.pack_start(theme_box, False, False, 0)

        # Custom theme editor
        theme_editor_frame = Gtk.Frame(label="Custom Theme")
        theme_editor_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        theme_editor_vbox.set_border_width(5)

        # Color pickers
        colors = [
            ("Background", "background_color"),
            ("Foreground", "foreground_color"),
            ("Cursor", "cursor_color")
        ]

        for label_text, config_key in colors:
            color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            color_label = Gtk.Label(label=f"{label_text}:")
            color_label.set_xalign(0)
            color_label.set_width_chars(12)

            color_button = Gtk.ColorButton()
            color = Gdk.RGBA()
            color.parse(self.current_config.get('theme', {}).get(config_key, '#000000'))
            color_button.set_rgba(color)

            setattr(self, f"{config_key}_button", color_button)
            color_box.pack_start(color_label, False, False, 0)
            color_box.pack_start(color_button, False, False, 0)
            theme_editor_vbox.pack_start(color_box, False, False, 0)

        theme_editor_frame.add(theme_editor_vbox)
        vbox.pack_start(theme_editor_frame, False, False, 0)

        # Font settings
        font_frame = Gtk.Frame(label="Font Settings")
        font_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        font_vbox.set_border_width(5)

        # Font family
        font_family_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        font_family_label = Gtk.Label(label="Font family:")
        font_family_label.set_xalign(0)

        self.font_family_entry = Gtk.Entry()
        self.font_family_entry.set_text(self.current_config.get('font', {}).get('family', 'Monospace'))

        font_family_box.pack_start(font_family_label, False, False, 0)
        font_family_box.pack_start(self.font_family_entry, True, True, 0)
        font_vbox.pack_start(font_family_box, False, False, 0)

        # Font size
        font_size_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        font_size_label = Gtk.Label(label="Font size:")
        font_size_label.set_xalign(0)

        font_size_adj = Gtk.Adjustment(
            value=self.current_config.get('font', {}).get('size', 12),
            lower=6,
            upper=72,
            step_increment=1
        )
        self.font_size_spin = Gtk.SpinButton(adjustment=font_size_adj)
        self.font_size_spin.set_digits(0)

        font_size_box.pack_start(font_size_label, False, False, 0)
        font_size_box.pack_start(self.font_size_spin, False, False, 0)
        font_vbox.pack_start(font_size_box, False, False, 0)

        font_frame.add(font_vbox)
        vbox.pack_start(font_frame, False, False, 0)

        return frame

    def _create_keybindings_tab(self) -> Gtk.Widget:
        """Create the keybindings preferences tab."""
        frame = Gtk.Frame(label="Keybindings")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        frame.add(vbox)

        # Keybinding tree view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(300)

        self.keybinding_store = Gtk.ListStore(str, str, str, str)  # action, key, description, category

        self.keybinding_tree = Gtk.TreeView(model=self.keybinding_store)
        self.keybinding_tree.set_headers_visible(True)

        # Columns
        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)
        renderer.connect("edited", self._on_keybinding_edited)

        for i, title in enumerate(["Action", "Key Combination", "Description", "Category"]):
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_resizable(True)
            if i == 1:  # Key combination column is editable
                column.add_attribute(renderer, "editable", 3)  # Use column 3 for editable flag
                renderer = Gtk.CellRendererText()
                renderer.set_property("editable", True)
                renderer.connect("edited", self._on_keybinding_edited)
            self.keybinding_tree.append_column(column)

        scrolled.add(self.keybinding_tree)
        vbox.pack_start(scrolled, True, True, 0)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        reset_button = Gtk.Button(label="Reset to Defaults")
        reset_button.connect("clicked", self._on_reset_keybindings)
        button_box.pack_end(reset_button, False, False, 0)

        export_button = Gtk.Button(label="Export")
        export_button.connect("clicked", self._on_export_keybindings)
        button_box.pack_end(export_button, False, False, 0)

        import_button = Gtk.Button(label="Import")
        import_button.connect("clicked", self._on_import_keybindings)
        button_box.pack_end(import_button, False, False, 0)

        vbox.pack_start(button_box, False, False, 0)

        # Load current keybindings
        self._load_keybindings()

        return frame

    def _create_plugins_tab(self) -> Gtk.Widget:
        """Create the plugins preferences tab."""
        frame = Gtk.Frame(label="Plugins")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        frame.add(vbox)

        # Plugin tree view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(300)

        self.plugin_store = Gtk.ListStore(bool, str, str, str, str)  # enabled, name, version, description, author

        self.plugin_tree = Gtk.TreeView(model=self.plugin_store)
        self.plugin_tree.set_headers_visible(True)

        # Columns
        renderer = Gtk.CellRendererToggle()
        renderer.connect("toggled", self._on_plugin_toggled)

        column = Gtk.TreeViewColumn("Enabled", renderer, active=0)
        self.plugin_tree.append_column(column)

        for i, title in enumerate(["Name", "Version", "Description", "Author"], 1):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_resizable(True)
            self.plugin_tree.append_column(column)

        scrolled.add(self.plugin_tree)
        vbox.pack_start(scrolled, True, True, 0)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        install_button = Gtk.Button(label="Install Plugin")
        install_button.connect("clicked", self._on_install_plugin)
        button_box.pack_end(install_button, False, False, 0)

        uninstall_button = Gtk.Button(label="Uninstall")
        uninstall_button.connect("clicked", self._on_uninstall_plugin)
        button_box.pack_end(uninstall_button, False, False, 0)

        reload_button = Gtk.Button(label="Reload")
        reload_button.connect("clicked", self._on_reload_plugins)
        button_box.pack_end(reload_button, False, False, 0)

        vbox.pack_start(button_box, False, False, 0)

        # Load current plugins
        self._load_plugins()

        return frame

    def _create_advanced_tab(self) -> Gtk.Widget:
        """Create the advanced preferences tab."""
        frame = Gtk.Frame(label="Advanced Settings")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        frame.add(vbox)

        # Performance settings
        perf_frame = Gtk.Frame(label="Performance")
        perf_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        perf_vbox.set_border_width(5)

        self.audible_bell_check = Gtk.CheckButton(label="Audible bell")
        self.audible_bell_check.set_active(self.current_config.get('audible_bell', False))
        perf_vbox.pack_start(self.audible_bell_check, False, False, 0)

        self.urgent_bell_check = Gtk.CheckButton(label="Urgent bell")
        self.urgent_bell_check.set_active(self.current_config.get('urgent_bell', True))
        perf_vbox.pack_start(self.urgent_bell_check, False, False, 0)

        self.mouse_autohide_check = Gtk.CheckButton(label="Auto-hide mouse cursor")
        self.mouse_autohide_check.set_active(self.current_config.get('mouse_autohide', False))
        perf_vbox.pack_start(self.mouse_autohide_check, False, False, 0)

        perf_frame.add(perf_vbox)
        vbox.pack_start(perf_frame, False, False, 0)

        # Debug settings
        debug_frame = Gtk.Frame(label="Debug")
        debug_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        debug_vbox.set_border_width(5)

        self.debug_mode_check = Gtk.CheckButton(label="Enable debug mode")
        self.debug_mode_check.set_active(self.current_config.get('debug_mode', False))
        debug_vbox.pack_start(self.debug_mode_check, False, False, 0)

        self.log_commands_check = Gtk.CheckButton(label="Log commands")
        self.log_commands_check.set_active(self.current_config.get('log_commands', False))
        debug_vbox.pack_start(self.log_commands_check, False, False, 0)

        debug_frame.add(debug_vbox)
        vbox.pack_start(debug_frame, False, False, 0)

        return frame

    def _get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        themes = ["Default", "Dark", "Light", "Solarized Dark", "Solarized Light"]

        # Add themes from plugins
        for plugin in self.plugin_manager.get_enabled_plugins().values():
            if hasattr(plugin, 'get_themes'):
                plugin_themes = plugin.get_themes()
                themes.extend(plugin_themes.keys())

        return sorted(themes)

    def _load_keybindings(self):
        """Load keybindings into the tree view."""
        self.keybinding_store.clear()

        for action, binding in self.keybinding_manager.get_all_bindings().items():
            self.keybinding_store.append([
                action,
                binding.key_combo,
                binding.description,
                binding.category
            ])

    def _load_plugins(self):
        """Load plugins into the tree view."""
        self.plugin_store.clear()

        for plugin_info in self.plugin_manager.get_plugin_info():
            self.plugin_store.append([
                plugin_info['enabled'],
                plugin_info['name'],
                plugin_info['version'],
                plugin_info['description'],
                plugin_info['author']
            ])

    def _on_response(self, dialog, response_id):
        """Handle dialog response."""
        if response_id == Gtk.ResponseType.OK or response_id == Gtk.ResponseType.APPLY:
            self._apply_changes()

        if response_id == Gtk.ResponseType.OK or response_id == Gtk.ResponseType.CANCEL:
            self.dialog.destroy()

    def _apply_changes(self):
        """Apply the changes to the configuration."""
        # Update config with new values
        self.current_config['restore_session'] = self.restore_session_check.get_active()
        self.current_config['show_menu_bar'] = self.show_menu_bar_check.get_active()
        self.current_config['gpu_acceleration'] = self.gpu_acceleration_check.get_active()
        self.current_config['scrollback_lines'] = self.scrollback_spin.get_value_as_int()

        # Theme settings
        if 'theme' not in self.current_config:
            self.current_config['theme'] = {}

        # Update colors
        for color_key in ['background_color', 'foreground_color', 'cursor_color']:
            button = getattr(self, f"{color_key}_button")
            if button:
                color = button.get_rgba()
                self.current_config['theme'][color_key] = color.to_string()

        # Font settings
        if 'font' not in self.current_config:
            self.current_config['font'] = {}

        self.current_config['font']['family'] = self.font_family_entry.get_text()
        self.current_config['font']['size'] = self.font_size_spin.get_value_as_int()

        # Advanced settings
        self.current_config['audible_bell'] = self.audible_bell_check.get_active()
        self.current_config['urgent_bell'] = self.urgent_bell_check.get_active()
        self.current_config['mouse_autohide'] = self.mouse_autohide_check.get_active()
        self.current_config['debug_mode'] = self.debug_mode_check.get_active()
        self.current_config['log_commands'] = self.log_commands_check.get_active()

        # Save config
        self.config.config = self.current_config
        self.config.save_config()

        # Notify listeners
        if self.on_config_changed:
            self.on_config_changed(self.current_config)

    def _on_keybinding_edited(self, widget, path, text):
        """Handle keybinding editing."""
        iter = self.keybinding_store.get_iter(path)
        action = self.keybinding_store.get_value(iter, 0)

        # Update the keybinding
        self.keybinding_manager.register_binding(
            action,
            text,
            lambda: None,  # Will be set properly when connecting
            self.keybinding_store.get_value(iter, 2),
            self.keybinding_store.get_value(iter, 3)
        )

        # Update the store
        self.keybinding_store.set_value(iter, 1, text)

    def _on_reset_keybindings(self, button):
        """Reset keybindings to defaults."""
        self.keybinding_manager.reset_to_defaults()
        self._load_keybindings()

    def _on_export_keybindings(self, button):
        """Export keybindings to file."""
        dialog = Gtk.FileChooserDialog(
            title="Export Keybindings",
            parent=self.dialog,
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Export", Gtk.ResponseType.OK)

        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if not filename.endswith('.json'):
                filename += '.json'

            try:
                with open(filename, 'w') as f:
                    json.dump(self.keybinding_manager.export_bindings(), f, indent=2)
            except Exception as e:
                error_dialog = Gtk.MessageDialog(
                    parent=self.dialog,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Error exporting keybindings: {e}"
                )
                error_dialog.run()
                error_dialog.destroy()

        dialog.destroy()

    def _on_import_keybindings(self, button):
        """Import keybindings from file."""
        dialog = Gtk.FileChooserDialog(
            title="Import Keybindings",
            parent=self.dialog,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Import", Gtk.ResponseType.OK)

        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()

            try:
                with open(filename, 'r') as f:
                    bindings = json.load(f)

                # Apply imported bindings
                for action, key_combo in bindings.items():
                    self.keybinding_manager.register_binding(
                        action, key_combo, lambda: None, "", "Imported"
                    )

                self._load_keybindings()

            except Exception as e:
                error_dialog = Gtk.MessageDialog(
                    parent=self.dialog,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Error importing keybindings: {e}"
                )
                error_dialog.run()
                error_dialog.destroy()

        dialog.destroy()

    def _on_plugin_toggled(self, renderer, path):
        """Handle plugin enable/disable toggle."""
        iter = self.plugin_store.get_iter(path)
        enabled = not self.plugin_store.get_value(iter, 0)
        name = self.plugin_store.get_value(iter, 1)

        # Find plugin by name
        for plugin_info in self.plugin_manager.get_plugin_info():
            if plugin_info['name'] == name:
                if enabled:
                    self.plugin_manager.enable_plugin(plugin_info['id'])
                else:
                    self.plugin_manager.disable_plugin(plugin_info['id'])
                break

        # Update store
        self.plugin_store.set_value(iter, 0, enabled)

    def _on_install_plugin(self, button):
        """Handle plugin installation."""
        dialog = Gtk.FileChooserDialog(
            title="Install Plugin",
            parent=self.dialog,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Install", Gtk.ResponseType.OK)

        filter_zip = Gtk.FileFilter()
        filter_zip.set_name("Plugin packages")
        filter_zip.add_pattern("*.zip")
        filter_zip.add_pattern("*.tar.gz")
        dialog.add_filter(filter_zip)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()

            if self.plugin_manager.install_plugin(filename):
                info_dialog = Gtk.MessageDialog(
                    parent=self.dialog,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Plugin installed successfully!"
                )
                info_dialog.run()
                info_dialog.destroy()
                self._load_plugins()
            else:
                error_dialog = Gtk.MessageDialog(
                    parent=self.dialog,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Failed to install plugin."
                )
                error_dialog.run()
                error_dialog.destroy()

        dialog.destroy()

    def _on_uninstall_plugin(self, button):
        """Handle plugin uninstallation."""
        selection = self.plugin_tree.get_selection()
        model, iter = selection.get_selected()

        if iter:
            name = model.get_value(iter, 1)

            # Find plugin by name
            for plugin_info in self.plugin_manager.get_plugin_info():
                if plugin_info['name'] == name:
                    confirm_dialog = Gtk.MessageDialog(
                        parent=self.dialog,
                        flags=0,
                        message_type=Gtk.MessageType.QUESTION,
                        buttons=Gtk.ButtonsType.YES_NO,
                        text=f"Are you sure you want to uninstall '{name}'?"
                    )

                    response = confirm_dialog.run()
                    confirm_dialog.destroy()

                    if response == Gtk.ResponseType.YES:
                        if self.plugin_manager.uninstall_plugin(plugin_info['id']):
                            info_dialog = Gtk.MessageDialog(
                                parent=self.dialog,
                                flags=0,
                                message_type=Gtk.MessageType.INFO,
                                buttons=Gtk.ButtonsType.OK,
                                text="Plugin uninstalled successfully!"
                            )
                            info_dialog.run()
                            info_dialog.destroy()
                            self._load_plugins()
                        else:
                            error_dialog = Gtk.MessageDialog(
                                parent=self.dialog,
                                flags=0,
                                message_type=Gtk.MessageType.ERROR,
                                buttons=Gtk.ButtonsType.OK,
                                text="Failed to uninstall plugin."
                            )
                            error_dialog.run()
                            error_dialog.destroy()
                    break

    def _on_reload_plugins(self, button):
        """Reload all plugins."""
        # Get plugin IDs to reload
        plugin_ids = []
        for plugin_info in self.plugin_manager.get_plugin_info():
            plugin_ids.append(plugin_info['id'])

        # Reload each plugin
        for plugin_id in plugin_ids:
            self.plugin_manager.reload_plugin(plugin_id)

        self._load_plugins()

        info_dialog = Gtk.MessageDialog(
            parent=self.dialog,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Plugins reloaded successfully!"
        )
        info_dialog.run()
        info_dialog.destroy()

    def set_config_changed_callback(self, callback: Callable):
        """Set callback for when configuration changes."""
        self.on_config_changed = callback
