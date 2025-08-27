# -*- coding: utf-8 -*-
"""
utils/cache.py — Cache simple en memoria.
"""
from functools import lru_cache

@lru_cache(maxsize=256)
def memo(key: str) -> str:
    # Placeholder: almacena la propia clave.
    return key
