"""OSINT plugin system for Pawpy."""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List

logger = logging.getLogger("pawpy.plugins")
PluginFunc = Callable[[Dict[str, Any]], Dict[str, Any]]
_plugins: List[PluginFunc] = []


def _discover_plugins(plugin_dir=None) -> None:
    if plugin_dir is None:
        plugin_dir = Path(__file__).parent
    else:
        plugin_dir = Path(plugin_dir)
    if not plugin_dir.is_dir():
        return
    for py_file in sorted(plugin_dir.glob("*.py")):
        if py_file.name.startswith("__"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                f"pawpy.plugins.{py_file.stem}", py_file
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            func = getattr(module, "collect", None)
            if callable(func):
                _plugins.append(func)
                logger.info("Loaded OSINT plugin: %s", py_file.stem)
        except Exception:
            logger.exception("Failed to load plugin: %s", py_file.stem)


def run_plugins(profile: Dict[str, Any]) -> Dict[str, Any]:
    if not _plugins:
        _discover_plugins()
    for plugin_func in _plugins:
        try:
            profile = plugin_func(profile)
        except Exception:
            logger.exception("Plugin %s raised an exception", plugin_func.__name__)
    return profile


def list_plugins() -> List[str]:
    if not _plugins:
        _discover_plugins()
    return [fn.__module__ for fn in _plugins]
