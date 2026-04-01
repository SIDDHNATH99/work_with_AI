"""
Persistent key-value memory store backed by a JSON file.
All writes are atomic (write-to-temp, then rename).
"""

import json
import pathlib
import re

_MEM_FILE = pathlib.Path("memory_store.json")
_KEY_RE = re.compile(r"^[\w\-]{1,64}$")


def _load() -> dict:
    if _MEM_FILE.exists():
        try:
            return json.loads(_MEM_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save(data: dict) -> None:
    tmp = _MEM_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(_MEM_FILE)


def _valid_key(key: str) -> bool:
    return bool(key and _KEY_RE.match(key))


def memory_set(key: str, value: str) -> dict:
    if not _valid_key(key):
        return {"error": "Key must be 1-64 alphanumeric/underscore/hyphen characters"}
    data = _load()
    data[key] = str(value)
    _save(data)
    return {"status": "stored", "key": key}


def memory_get(key: str) -> dict:
    if not _valid_key(key):
        return {"error": "Invalid key format"}
    data = _load()
    if key not in data:
        return {"error": f"Key '{key}' not found", "available_keys": list(data.keys())}
    return {"key": key, "value": data[key]}


def memory_list() -> dict:
    data = _load()
    return {"keys": list(data.keys()), "count": len(data)}


def memory_delete(key: str) -> dict:
    if not _valid_key(key):
        return {"error": "Invalid key format"}
    data = _load()
    if key not in data:
        return {"error": f"Key '{key}' not found"}
    del data[key]
    _save(data)
    return {"status": "deleted", "key": key}
