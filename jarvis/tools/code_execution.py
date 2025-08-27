# -*- coding: utf-8 -*-
"""
tools/code_execution.py — Ejecuta código Python en un entorno controlado (muy básico).
"""
import runpy
import tempfile
from .base import BaseTool

class CodeRunTool(BaseTool):
    name = "runpy"
    description = "Ejecuta un script Python aislado: !runpy print('hola')"

    def run(self, *code: str) -> str:
        src = " ".join(code)
        with tempfile.TemporaryDirectory() as td:
            path = f"{td}/snippet.py"
            with open(path, "w", encoding="utf-8") as f:
                f.write(src)
            try:
                runpy.run_path(path, run_name="__main__")
                return "Ejecución OK (sin salida capturada)."
            except SystemExit as e:
                return f"Finalizó con SystemExit: {e.code}"
            except Exception as e:
                return f"Error al ejecutar: {e}"
