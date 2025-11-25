#!/usr/bin/env python3
"""Base class for converting Lua files to YAML."""

from pathlib import Path
from typing import Any, Optional

from lupa import LuaRuntime
import yaml


class LuaToYamlConverter:
    """Base class for converting Lua files to YAML."""

    def __init__(self, p_file_path: Path, p_global_var: str):
        """
        Initialize converter.

        Args:
            p_file_path: Path to Lua file
            p_global_var: Name of global variable to extract
        """
        self.m_file_path = p_file_path
        self.m_global_var = p_global_var
        self.m_lua = None
        self.m_python_data = None

    def load(self) -> None:
        """Load and parse Lua file."""
        if not self.m_file_path.exists():
            raise FileNotFoundError(f"*** Error: File not found: {self.m_file_path}")
        if self.m_file_path.parent.name.startswith('_'):
            return
        with open(self.m_file_path, 'r', encoding='utf-8') as l_file:
            l_content = l_file.read()
        self.m_lua = LuaRuntime(unpack_returned_tuples=True)
        self.m_lua.execute(l_content)
        l_globals = self.m_lua.globals()
        if self.m_global_var not in l_globals:
            raise ValueError(f"*** Error: {self.m_global_var} not found in Lua file")
        l_table = l_globals[self.m_global_var]
        self.m_python_data = self._lua_to_python(l_table)

    def _lua_to_python(self, p_value: Any) -> Any:
        """
        Convert Lua object to Python object.

        Args:
            p_value: Lua object

        Returns:
            Python equivalent
        """
        if p_value is None:
            return None
        if not hasattr(p_value, 'items'):
            return p_value
        l_result = {}
        for c_key, c_val in p_value.items():
            l_py_key = self._lua_to_python(c_key)
            l_py_val = self._lua_to_python(c_val)
            l_result[l_py_key] = l_py_val
        return l_result

    def save_yaml(self, p_output_path: Optional[Path] = None) -> None:
        """
        Save data as YAML file.

        Args:
            p_output_path: Output path (default: same as input with .yaml)
        """
        if not self.m_python_data:
            return False
        if p_output_path is None:
            p_output_path = self.m_file_path.with_suffix('.yaml')
        p_output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(p_output_path, 'w', encoding='utf-8') as l_file:
            yaml.dump(self.m_python_data, l_file, default_flow_style=False, allow_unicode=True)
        return True
