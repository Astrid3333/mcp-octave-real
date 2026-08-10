#!/usr/bin/env python3
"""
patch_fix_spacing_llmbridge.py
Cosmetico: agrega la linea en blanco que falta antes del @mcp.tool() de
llm_math_bridge_tool, para que quede igual al resto del archivo.
"""
import pathlib

TARGET = pathlib.Path("server.py")

content = TARGET.read_text(encoding="utf-8")

marker = (
    "    return compute_octave_syntax(mode, **(params or {}))\n"
    "@mcp.tool()\n"
    "def llm_math_bridge_tool"
)
assert content.count(marker) == 1, "marker no encontrado (o no es unico) -- puede que ya este corregido"

fixed = marker.replace(
    "return compute_octave_syntax(mode, **(params or {}))\n@mcp.tool()",
    "return compute_octave_syntax(mode, **(params or {}))\n\n\n@mcp.tool()",
)
content = content.replace(marker, fixed, 1)
TARGET.write_text(content, encoding="utf-8")
print("Espaciado corregido: linea en blanco agregada antes de llm_math_bridge_tool.")
