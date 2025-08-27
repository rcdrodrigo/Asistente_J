# -*- coding: utf-8 -*-
"""
tools/file_analysis.py — Lee y resume archivos de texto (simple).
"""
from .base import BaseTool
from pathlib import Path

class FileAnalysisTool(BaseTool):
    name = "file"
    description = "Lee un archivo de texto: !file ruta/al/archivo.txt"

    def __init__(self, settings):
        super().__init__(settings)

    def run(self, *args) -> str:
        if not args:
            return self.help()
        p = Path(args[0])
        if not p.exists():
            return f"Archivo no encontrado: {p}"
        text = p.read_text(encoding="utf-8", errors="ignore")
        snippet = text.strip().splitlines()[:20]
        return "\n".join(snippet) if snippet else "(archivo vacío)"