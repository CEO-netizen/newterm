"""
NewTerm Plugin Manager Module

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

This module handles loading, managing, and executing plugins.
"""

import os
import sys
import importlib.util
import json
import hashlib
from typing import Dict, Any, List, Optional, Type, Callable
from pathlib import Path
import logging
from plugin_api import PluginBase, PluginEvent, PLUGIN_CONFIG_SCHEMA

class PluginLoadError(Exception):
    """Exception raised when a plugin fails to load."""
    pass

class PluginManager:
    """Manages plugins for the terminal application."""

    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.expanduser("~/.config/newterm")
        self.plugin_dir = os.path.join(self.config_dir, "plugins")
        self.enabled_plugins: Dict[str, PluginBase] = {}
        self.disabled_plugins: Dict[str, PluginBase] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.event_hooks: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger("newterm.plugins")

        # Create plugin directory if it doesn't exist
        os.makedirs(self.plugin_dir, exist_ok=True)

        # Set up logging
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging for plugins."""
        log_file = os.path.join(self.config_dir, "plugins.log")
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def discover_plugins(self) -> List[Dict[str, Any]]:
        """Discover available plugins in the plugin directory."""
        plugins = []

        if not os.path.exists(self.plugin_dir):
            return plugins

        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)

            if os.path.isdir(plugin_path):
                # Check for plugin.json or __init__.py
                plugin_config_path = os.path.join(plugin_path, "plugin.json")
                init_path = os.path.join(plugin_path, "__init__.py")

                if os.path.exists(plugin_config_path):
                    try:
                        with open(plugin_config_path, 'r') as f:
                            config = json.load(f)

                        config['path'] = plugin_path
                        config['id'] = self._generate_plugin_id(plugin_path)
                        plugins.append(config)
                    except Exception as e:
                        self.logger.error(f"Error loading plugin config {plugin_config_path}: {e}")

                elif os.path.exists(init_path):
                    # Legacy plugin support
                    plugins.append({
                        'name': item,
                        'version': '1.0.0',
                        'description': 'Legacy plugin',
                        'path': plugin_path,
                        'id': self._generate_plugin_id(plugin_path),
                        'legacy': True
                    })

        return plugins

    def _generate_plugin_id(self, plugin_path: str) -> str:
        """Generate a unique ID for a plugin."""
        return hashlib.md5(plugin_path.encode()).hexdigest()[:8]

    def load_plugin(self, plugin_config: Dict[str, Any]) -> Optional[PluginBase]:
        """Load a single plugin."""
        plugin_path = plugin_config['path']
        plugin_id = plugin_config['id']

        try:
            # Check if plugin is already loaded
            if plugin_id in self.enabled_plugins or plugin_id in self.disabled_plugins:
                return self.enabled_plugins.get(plugin_id) or self.disabled_plugins.get(plugin_id)

            # Load plugin module
            if plugin_config.get('legacy', False):
                plugin_class = self._load_legacy_plugin(plugin_path, plugin_config)
            else:
                plugin_class = self._load_modern_plugin(plugin_path, plugin_config)

            if not plugin_class:
                raise PluginLoadError("Could not load plugin class")

            # Create plugin instance
            plugin = plugin_class(self, plugin_config)

            # Validate dependencies
            if not self._check_dependencies(plugin):
                self.logger.warning(f"Plugin {plugin_config['name']} has unmet dependencies")
                self.disabled_plugins[plugin_id] = plugin
                return None

            # Load plugin configuration
            plugin_config = self._load_plugin_config(plugin_id, plugin_config)

            # Call on_load hook
            try:
                plugin.on_load()
            except Exception as e:
                self.logger.error(f"Error in plugin on_load: {e}")

            # Register event hooks
            self._register_event_hooks(plugin)

            # Store plugin
            if plugin.is_enabled():
                self.enabled_plugins[plugin_id] = plugin
                self.logger.info(f"Loaded plugin: {plugin.get_name()} v{plugin.get_version()}")
            else:
                self.disabled_plugins[plugin_id] = plugin

            return plugin

        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_config.get('name', 'unknown')}: {e}")
            return None

    def _load_legacy_plugin(self, plugin_path: str, config: Dict[str, Any]) -> Optional[Type[PluginBase]]:
        """Load a legacy plugin (Python module)."""
        try:
            import importlib
            plugin_name = config['name'].replace('-', '_')
            sys.path.insert(0, plugin_path)

            try:
                module = importlib.import_module(plugin_name)
                # Look for plugin class
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, PluginBase) and
                        attr != PluginBase):
                        return attr
            finally:
                sys.path.remove(plugin_path)

        except Exception as e:
            self.logger.error(f"Error loading legacy plugin: {e}")

        return None

    def _load_modern_plugin(self, plugin_path: str, config: Dict[str, Any]) -> Optional[Type[PluginBase]]:
        """Load a modern plugin with plugin.json."""
        try:
            # Look for main plugin file
            main_file = config.get('main', 'plugin.py')
            main_path = os.path.join(plugin_path, main_file)

            if not os.path.exists(main_path):
                raise PluginLoadError(f"Main plugin file not found: {main_file}")

            # Load the module
            spec = importlib.util.spec_from_file_location(f"plugin_{config['id']}", main_path)
            if not spec:
                raise PluginLoadError("Could not create module spec")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, PluginBase) and
                    attr != PluginBase):
                    return attr

        except Exception as e:
            self.logger.error(f"Error loading modern plugin: {e}")

        return None

    def _check_dependencies(self, plugin: PluginBase) -> bool:
        """Check if plugin dependencies are satisfied."""
        dependencies = plugin.get_dependencies()

        for dep in dependencies:
            # Check if dependency is loaded
            dep_found = False
            for loaded_plugin in self.enabled_plugins.values():
                if loaded_plugin.get_name() == dep:
                    dep_found = True
                    break

            if not dep_found:
                return False

        return True

    def _load_plugin_config(self, plugin_id: str, plugin_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load plugin-specific configuration."""
        config_file = os.path.join(self.config_dir, f"plugin_{plugin_id}.json")

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading plugin config: {e}")

        # Return default config
        return plugin_config.get('config', {})

    def _register_event_hooks(self, plugin: PluginBase):
        """Register event hooks for a plugin."""
        # Get all methods with _plugin_hooks attribute
        for attr_name in dir(plugin):
            attr = getattr(plugin, attr_name)
            if hasattr(attr, '_plugin_hooks'):
                for event_type in attr._plugin_hooks:
                    if event_type not in self.event_hooks:
                        self.event_hooks[event_type] = []
                    self.event_hooks[event_type].append(attr)

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin."""
        plugin = self.enabled_plugins.get(plugin_id) or self.disabled_plugins.get(plugin_id)

        if not plugin:
            return False

        try:
            # Call on_unload hook
            plugin.on_unload()

            # Remove from collections
            if plugin_id in self.enabled_plugins:
                del self.enabled_plugins[plugin_id]
            if plugin_id in self.disabled_plugins:
                del self.disabled_plugins[plugin_id]

            # Remove event hooks
            for event_type, hooks in self.event_hooks.items():
                self.event_hooks[event_type] = [
                    hook for hook in hooks
                    if not hasattr(hook, '__self__') or hook.__self__ != plugin
                ]

            self.logger.info(f"Unloaded plugin: {plugin.get_name()}")
            return True

        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False

    def emit_event(self, event_type: str, **kwargs):
        """Emit an event to all registered hooks."""
        if event_type not in self.event_hooks:
            return

        for hook in self.event_hooks[event_type]:
            try:
                hook(**kwargs)
            except Exception as e:
                self.logger.error(f"Error in plugin hook for {event_type}: {e}")

    def get_plugin(self, plugin_id: str) -> Optional[PluginBase]:
        """Get a plugin by ID."""
        return self.enabled_plugins.get(plugin_id) or self.disabled_plugins.get(plugin_id)

    def get_enabled_plugins(self) -> Dict[str, PluginBase]:
        """Get all enabled plugins."""
        return self.enabled_plugins.copy()

    def get_disabled_plugins(self) -> Dict[str, PluginBase]:
        """Get all disabled plugins."""
        return self.disabled_plugins.copy()

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin."""
        plugin = self.disabled_plugins.get(plugin_id)
        if not plugin:
            return False

        if not self._check_dependencies(plugin):
            self.logger.warning(f"Cannot enable plugin {plugin_id}: unmet dependencies")
            return False

        plugin.set_enabled(True)
        self.enabled_plugins[plugin_id] = plugin
        del self.disabled_plugins[plugin_id]

        try:
            plugin.on_load()
            self.logger.info(f"Enabled plugin: {plugin.get_name()}")
            return True
        except Exception as e:
            self.logger.error(f"Error enabling plugin {plugin_id}: {e}")
            return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin."""
        plugin = self.enabled_plugins.get(plugin_id)
        if not plugin:
            return False

        plugin.set_enabled(False)
        self.disabled_plugins[plugin_id] = plugin
        del self.enabled_plugins[plugin_id]

        self.logger.info(f"Disabled plugin: {plugin.get_name()}")
        return True

    def reload_plugin(self, plugin_id: str) -> bool:
        """Reload a plugin."""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return False

        config = self.plugin_configs.get(plugin_id, {})
        self.unload_plugin(plugin_id)
        return self.load_plugin(config) is not None

    def get_plugin_info(self) -> List[Dict[str, Any]]:
        """Get information about all plugins."""
        plugins = []

        for plugin_id, plugin in self.enabled_plugins.items():
            plugins.append({
                'id': plugin_id,
                'name': plugin.get_name(),
                'version': plugin.get_version(),
                'description': plugin.get_description(),
                'author': plugin.get_author(),
                'enabled': True
            })

        for plugin_id, plugin in self.disabled_plugins.items():
            plugins.append({
                'id': plugin_id,
                'name': plugin.get_name(),
                'version': plugin.get_version(),
                'description': plugin.get_description(),
                'author': plugin.get_author(),
                'enabled': False
            })

        return plugins

    def install_plugin(self, plugin_path: str) -> bool:
        """Install a plugin from a file or URL."""
        # TODO: Implement plugin installation
        # This would handle downloading, extracting, and validating plugins
        self.logger.info(f"Plugin installation not yet implemented: {plugin_path}")
        return False

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin."""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return False

        # Get plugin path
        plugin_path = getattr(plugin, '_plugin_path', None)
        if not plugin_path:
            return False

        try:
            # Remove plugin directory
            import shutil
            shutil.rmtree(plugin_path)

            # Remove config
            config_file = os.path.join(self.config_dir, f"plugin_{plugin_id}.json")
            if os.path.exists(config_file):
                os.remove(config_file)

            # Unload plugin
            self.unload_plugin(plugin_id)

            self.logger.info(f"Uninstalled plugin: {plugin.get_name()}")
            return True

        except Exception as e:
            self.logger.error(f"Error uninstalling plugin {plugin_id}: {e}")
            return False
