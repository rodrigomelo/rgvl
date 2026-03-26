"""
Config loader for RGVL targets.
Centralizes hardcoded target names across collectors.

Usage:
    from config.targets import get_targets, get_primary_target, get_search_names
    targets = get_targets()
    primary = get_primary_target()
    names = get_search_names()
"""
import json
import sys
from pathlib import Path
from functools import lru_cache

# Resolve config/ relative to this file
CONFIG_DIR = Path(__file__).parent
PROJECT_ROOT = CONFIG_DIR.parent
TARGETS_FILE = CONFIG_DIR / 'targets.json'


def _load() -> dict:
    """Load targets.json."""
    with open(TARGETS_FILE, encoding='utf-8') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def get_targets() -> list:
    """Return list of target dicts."""
    return _load()['targets']


@lru_cache(maxsize=1)
def get_primary_target() -> dict:
    """Return the primary target (role='primary')."""
    targets = get_targets()
    for t in targets:
        if t.get('role') == 'primary':
            return t
    return targets[0] if targets else {}


@lru_cache(maxsize=1)
def get_search_names() -> list:
    """Return all unique search names across all targets."""
    names = []
    for t in get_targets():
        names.extend(t.get('search_names', []))
    return list(dict.fromkeys(names))  # preserve order, remove dupes


@lru_cache(maxsize=1)
def get_primary_search_names() -> list:
    """Return search names for the primary target only."""
    return get_primary_target().get('search_names', [])
