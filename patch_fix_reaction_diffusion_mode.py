#!/usr/bin/env python3
"""
patch_fix_reaction_diffusion_mode.py

Bug: compute_reaction_diffusion solo compara `mode == "check_turing_instability"`
en dos puntos. Cualquier otro valor -- incluido un typo -- cae de largo en la
rama de simulate_growth_rate sin avisar. Fix: validar mode contra los dos
valores conocidos al principio de la funcion, devolver {"error": ...} si no
calza (mismo patron de manejo de error que ya usa el resto del archivo).
"""
import pathlib

TARGET = pathlib.Path("reaction_diffusion_tool.py")
BACKUP = pathlib.Path("reaction_diffusion_tool.py.bak_modevalidation")

content = TARGET.read_text(encoding="utf-8")

marker = (
    "def compute_reaction_diffusion(mode=\"check_turing_instability\", a11=1.0, a12=-1.0,\n"
    "                                a21=2.0, a22=-1.5, Du=1.0, Dv=10.0):\n"
    "    trace = a11 + a22\n"
)
assert content.count(marker) == 1, "marker no encontrado (o no es unico) -- revisar a mano"

replacement = (
    "_VALID_REACTION_DIFFUSION_MODES = (\"check_turing_instability\", \"simulate_growth_rate\")\n\n\n"
    "def compute_reaction_diffusion(mode=\"check_turing_instability\", a11=1.0, a12=-1.0,\n"
    "                                a21=2.0, a22=-1.5, Du=1.0, Dv=10.0):\n"
    "    if mode not in _VALID_REACTION_DIFFUSION_MODES:\n"
    "        return {\n"
    "            \"error\": f\"mode desconocido: '{mode}'\",\n"
    "            \"modos_validos\": list(_VALID_REACTION_DIFFUSION_MODES),\n"
    "        }\n"
    "    trace = a11 + a22\n"
)

BACKUP.write_text(content, encoding="utf-8")
TARGET.write_text(content.replace(marker, replacement, 1), encoding="utf-8")

print(f"Backup guardado en {BACKUP}")
print(f"{TARGET} actualizado: mode invalido ahora devuelve {{'error': ...}} en vez de "
      "caer silenciosamente en simulate_growth_rate.")
print(f"\nRevisa el diff con: git diff {TARGET}")
print(f"Si algo salio mal, restaura con: cp {BACKUP} {TARGET}")
