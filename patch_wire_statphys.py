#!/usr/bin/env python3
"""
Wirea statistical_physics_tool.py (Ising 2D + Potts grain growth, fase 2
del roadmap de materiales/fisica) como tool nuevo en server.py.

Uso: correr desde dentro de ~/mcp-octave-real
    python3 patch_wire_statphys.py

Requiere que statistical_physics_tool.py ya este copiado en el directorio.
"""
from pathlib import Path

SERVER = Path("server.py")
STATPHYS = Path("statistical_physics_tool.py")
assert SERVER.exists(), "Correr este script dentro de ~/mcp-octave-real"
assert STATPHYS.exists(), "Falta statistical_physics_tool.py en el directorio actual"

src = SERVER.read_text()
backup = SERVER.with_suffix(".py.bak3")
backup.write_text(src)
print(f"Backup guardado en {backup}")

import_line = "from statistical_physics_tool import compute_statistical_physics"
if import_line not in src:
    # Insertar despues del import de composite_homogenization si existe,
    # si no, al final del bloque de imports conocido
    marker = "from composite_homogenization import compute_composite_homogenization"
    if marker in src:
        src = src.replace(marker, marker + "\n" + import_line, 1)
    else:
        last_import_marker = "from reaction_diffusion_tool_real import compute_reaction_diffusion as compute_reaction_diffusion_real"
        assert last_import_marker in src, "no se encontro ningun marcador de import conocido"
        src = src.replace(last_import_marker, last_import_marker + "\n" + import_line, 1)
    print("Import de statistical_physics_tool agregado.")
else:
    print("AVISO: el import ya existia, no se toco.")

tool_function = '''

@mcp.tool()
def statistical_physics_tool(mode: str, params: dict = None) -> dict:
    """Fisica estadistica y sistemas complejos: modelo de Ising 2D via Monte Carlo Metropolis (magnetizacion, energia, calor especifico, estimacion de temperatura critica vs valor exacto de Onsager) y modelo de Potts de q estados para crecimiento de grano/microestructura (evolucion de numero de granos y area promedio en el tiempo). mode='ising_2d' o 'potts_grain_growth'."""
    return compute_statistical_physics(mode, **(params or {}))
'''
if "def statistical_physics_tool" not in src:
    src = src.rstrip() + "\n" + tool_function
    print("Funcion statistical_physics_tool agregada.")
else:
    print("AVISO: statistical_physics_tool ya existia, no se toco.")

SERVER.write_text(src)
print("server.py actualizado.")
print()
print("Revisa el diff con: git diff server.py")
print("Si algo salio mal, restaura con: cp server.py.bak3 server.py")
