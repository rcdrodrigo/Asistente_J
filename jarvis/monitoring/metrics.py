# -*- coding: utf-8 -*-
"""
monitoring/metrics.py — Métricas sencillas en memoria.
"""
from collections import defaultdict
_counts = defaultdict(int)

def inc(name: str):
    _counts[name] += 1

def dump() -> dict:
    return dict(_counts)
