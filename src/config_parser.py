"""
NewTerm Configuration Parser Module

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

import re
import os
from typing import Dict, Any, List, Optional

class ConfigParser:
    """Parser for custom configuration language with graceful error handling."""

    def __init__(self):
        self.line_number = 0
        self.errors = []
        self.warnings = []

    def parse(self, content: str) -> Dict[str, Any]:
        """Parse configuration content into a dictionary."""
        self.line_number = 0
        self.errors = []
        self.warnings = []

        if not content.strip():
            return {}

        try:
            return self._parse_content(content)
        except Exception as e:
            self.errors.append(f"Parse error: {str(e)}")
            return {}

    def _parse_content(self, content: str) -> Dict[str, Any]:
        """Main parsing logic."""
        config = {}
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            self.line_number = i + 1

            if not line or line.startswith('#'):
                i += 1
                continue

            if line.startswith('}') or line.endswith('{'):
                # Handle section endings and beginnings
                i += 1
                continue

            # Parse key-value pairs or sections
            if '=' in line and not line.endswith('{'):
                key, value = self._parse_key_value(line)
                if key:
                    config[key] = value
                i += 1
            elif line.endswith('{'):
                # Parse section
                section_name = line[:-1].strip()
                section_content, new_i = self._parse_section(lines, i + 1)
                config[section_name] = section_content
                i = new_i
            else:
                self.warnings.append(f"Line {self.line_number}: Unrecognized syntax: {line}")
                i += 1

        return config

    def _parse_key_value(self, line: str) -> tuple[Optional[str], Any]:
        """Parse a key=value line."""
        try:
            if '=' not in line:
                return None, None

            key, value_part = line.split('=', 1)
            key = key.strip()
            value_part = value_part.strip()

            # Handle different value types
            if value_part.lower() in ('true', 'false'):
                return key, value_part.lower() == 'true'
            elif value_part.startswith('[') and value_part.endswith(']'):
                return key, self._parse_array(value_part)
            elif value_part.startswith('"') and value_part.endswith('"'):
                return key, value_part[1:-1]
            elif self._is_number(value_part):
                return key, self._parse_number(value_part)
            else:
                return key, value_part
        except Exception as e:
            self.errors.append(f"Line {self.line_number}: Error parsing '{line}': {str(e)}")
            return None, None

    def _parse_array(self, array_str: str) -> List[str]:
        """Parse array syntax [item1, item2, item3]."""
        try:
            # Remove brackets
            inner = array_str[1:-1].strip()
            if not inner:
                return []

            # Split by comma and clean up
            items = [item.strip().strip('"\'') for item in inner.split(',')]
            return [item for item in items if item]  # Remove empty items
        except Exception:
            return []

    def _parse_number(self, value: str) -> Union[int, float]:
        """Parse numeric values."""
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value  # Return as string if not a valid number

    def _is_number(self, value: str) -> bool:
        """Check if string represents a number."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _parse_section(self, lines: List[str], start_i: int) -> tuple[Dict[str, Any], int]:
        """Parse a section block."""
        section_config = {}
        i = start_i

        while i < len(lines):
            line = lines[i].strip()
            self.line_number = i + 1

            if line == '}' or (line.startswith('}') and line.endswith('}')):
                return section_config, i + 1

            if not line or line.startswith('#'):
                i += 1
                continue

            if '=' in line:
                key, value = self._parse_key_value(line)
                if key:
                    section_config[key] = value
                i += 1
            else:
                self.warnings.append(f"Line {self.line_number}: Unrecognized syntax in section: {line}")
                i += 1

        return section_config, i

    def get_errors(self) -> List[str]:
        """Get parsing errors."""
        return self.errors.copy()

    def get_warnings(self) -> List[str]:
        """Get parsing warnings."""
        return self.warnings.copy()

def parse_config_file(file_path: str) -> Dict[str, Any]:
    """Parse a configuration file."""
    if not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        parser = ConfigParser()
        config = parser.parse(content)

        # Log warnings but don't fail
        for warning in parser.get_warnings():
            print(f"Config warning: {warning}")

        return config
    except Exception as e:
        print(f"Error reading config file {file_path}: {e}")
        return {}
