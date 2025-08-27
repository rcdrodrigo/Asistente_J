# -*- coding: utf-8 -*-
"""
tools/base.py — Clase base para herramientas.
"""
from abc import ABC, abstractmethod

class BaseTool(ABC):
    name: str = "tool"
    description: str = "Herramienta genérica"

    def __init__(self, settings):
        self.settings = settings

    @abstractmethod
    def run(self, *args, **kwargs) -> str:
        ...

    def help(self) -> str:
        return f"{self.name}: {self.description}"
