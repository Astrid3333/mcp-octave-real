#!/usr/bin/env python3
"""
Wirea cfd_tool.py (Poiseuille flow + lid-driven cavity, fase 3 del
roadmap) como tool nuevo en server.py.

Uso: correr desde dentro de ~/mcp-octave-real
    python3 patch_wire_cfd.py

Requiere que cfd_tool.py ya este copiado en el directorio.
"""
from pathlib import Path

SERVER = Path("server.py")
CFD = Path("cfd_tool.py")
assert SERVER.exists(), "Correr este script dentro de ~/mcp-octave-real"
assert CFD.exists(), "Falta cfd_tool.py en el directorio actual"

src = SERVER.read_text()
backup = SERVER.with_suffix(".py.bak4")
backup.write_text(src)
print(f"Backup guardado en {backup}")

import_line = "from cfd_tool import compute_cfd"
if import_line not in src:
    marker = "from statistical_physics_tool import compute_statistical_physics"
    if marker in src:
        src = src.replace(marker, marker + "\n" + import_line, 1)
    else:
        last_import_marker = "from composite_homogenization import compute_composite_homogenization"
        assert last_import_marker in src, "no se encontro ningun marcador de import conocido"
        src = src.replace(last_import_marker, last_import_marker + "\n" + import_line, 1)
    print("Import de cfd_tool agregado.")
else:
    print("AVISO: el import ya existia, no se toco.")

tool_function = '''

@mcp.tool()
def cfd_tool(mode: str, params: dict = None) -> dict:
    """CFD 2D laminar (sin modelos de turbulencia). mode='poiseuille_flow': flujo de Stokes entre placas paralelas, validado contra la solucion analitica de Hagen-Poiseuille. mode='lid_driven_cavity': Navier-Stokes 2D via formulacion vorticidad-funcion de corriente, cavidad con tapa movil, validado contra el benchmark de Ghia, Ghia & Shin (1982) en Re=100."""
    return compute_cfd(mode, **(params or {}))
'''
if "def cfd_tool" not in src:
    src = src.rstrip() + "\n" + tool_function
    print("Funcion cfd_tool agregada.")
else:
    print("AVISO: cfd_tool ya existia, no se toco.")

SERVER.write_text(src)
print("server.py actualizado.")
print()
print("Revisa el diff con: git diff server.py")
print("Si algo salio mal, restaura con: cp server.py.bak4 server.py")
