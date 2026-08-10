#!/usr/bin/env python3
"""
patch_wire_llm_math_bridge.py

Wirea llm_math_bridge_tool.py a server.py siguiendo el patron real de este
repo (FastMCP, no un dispatcher manual): un import mas arriba, y un wrapper
delgado @mcp.tool() al final, mismo estilo que budgeting_tool/earthworks_tool
(mode/operation + params dict -> **(params or {})).
"""
import pathlib

TARGET = pathlib.Path("server.py")
BACKUP = pathlib.Path("server.py.bak_llmbridge")

content = TARGET.read_text(encoding="utf-8")

assert "llm_math_bridge_tool" not in content, (
    "llm_math_bridge_tool ya aparece en server.py -- parece que ya esta "
    "wireado (o parcialmente). Revisar a mano antes de aplicar este patch, "
    "para no duplicar el import o el wrapper."
)

import_marker = "from octave_syntax_tool import compute_octave_syntax\n"
assert content.count(import_marker) == 1, "marker de import no encontrado (o no es unico) -- revisar a mano"

new_import_block = import_marker + "from llm_math_bridge_tool import compute_llm_math_bridge\n"
content = content.replace(import_marker, new_import_block, 1)

wrapper = '''
@mcp.tool()
def llm_math_bridge_tool(mode: str = "auto", params: dict = None) -> dict:
    """Puente con un LLM real (Anthropic API) para el pipeline matematico. mode='interpret': decide que tool y parametros usar dada una consulta en lenguaje natural (params: query). mode='explain': explica en espanol un resultado ya calculado (params: tool_name, result, query opcional). mode='orchestrate': encadena varios tools segun haga falta (params: query, max_steps opcional). mode='auto' (default): decide heuristicamente entre las anteriores segun la dificultad de la consulta (params: query, max_steps opcional). Requiere ANTHROPIC_API_KEY en el entorno; sin ella devuelve {"error": ...} en vez de fallar."""
    return compute_llm_math_bridge(mode, **(params or {}))
'''

content = content.rstrip("\n") + "\n" + wrapper.lstrip("\n")

BACKUP.write_text(TARGET.read_text(encoding="utf-8"), encoding="utf-8")
TARGET.write_text(content, encoding="utf-8")

print(f"Backup guardado en {BACKUP}")
print("server.py actualizado: import de llm_math_bridge_tool agregado, "
      "wrapper llm_math_bridge_tool() agregado al final con @mcp.tool().")
print("\nRevisa el diff con: git diff server.py")
print(f"Si algo salio mal, restaura con: cp {BACKUP} server.py")
