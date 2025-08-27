# -*- coding: utf-8 -*-
"""
tools/registry.py — Registro de herramientas disponibles.
"""
from typing import Dict
from .base import BaseTool
from .system_info import SystemInfoTool
from .documentation import DocTool
from .git_operations import GitTool
from .file_analysis import FileAnalysisTool
from .code_execution import CodeRunTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def add(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str):
        return self._tools.get(name)

    @classmethod
    def default_registry(cls, settings):
        reg = cls()
        reg.add(SystemInfoTool(settings))
        reg.add(DocTool(settings))
        reg.add(GitTool(settings))
        reg.add(FileAnalysisTool(settings))
        reg.add(CodeRunTool(settings))
        return reg
