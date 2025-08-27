# -*- coding: utf-8 -*-
"""
core/session.py — Maneja el historial de conversación.
"""
from typing import List, Dict

class Session:
    def __init__(self):
        self.messages: List[Dict[str,str]] = []

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def as_messages(self) -> List[Dict[str,str]]:
        return list(self.messages)
