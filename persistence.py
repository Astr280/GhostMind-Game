"""Small, defensive local JSON stores. Missing/corrupt files simply use defaults."""
from __future__ import annotations
import json
from pathlib import Path

DATA = Path(__file__).with_name('ghostmind_data.json')
DEFAULTS = {'high_score': 0, 'difficulty': 'EASY', 'show_paths': False, 'muted': False}

def load_preferences() -> dict:
    try:
        value = json.loads(DATA.read_text(encoding='utf8'))
        if not isinstance(value, dict): raise ValueError('settings root is not an object')
        return {**DEFAULTS, **{k: value[k] for k in DEFAULTS if k in value}}
    except (OSError, ValueError, json.JSONDecodeError):
        return DEFAULTS.copy()

def save_preferences(values: dict) -> None:
    safe = {k: values.get(k, DEFAULTS[k]) for k in DEFAULTS}
    try: DATA.write_text(json.dumps(safe, indent=2), encoding='utf8')
    except OSError: pass
