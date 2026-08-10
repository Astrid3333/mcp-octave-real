#!/usr/bin/env python3
"""
patch_fix_enzyme_kinetics_mode.py

Bug: compute_enzyme_kinetics chequea `if mode=="full_kinetics"` y
`if mode=="michaelis_menten"`, pero cualquier otro valor -- typo incluido --
cae de largo en la rama final que trata todo como "compare". Fix: validar
mode contra los tres valores conocidos al principio de la funcion, ANTES de
correr la simulacion en Octave (asi tampoco se malgasta el subprocess con un
mode invalido).
"""
import pathlib

TARGET = pathlib.Path("enzyme_kinetics_tool.py")
BACKUP = pathlib.Path("enzyme_kinetics_tool.py.bak_modevalidation")

content = TARGET.read_text(encoding="utf-8")

marker = (
    "def compute_enzyme_kinetics(mode=\"compare\", k1=100.0, km1=10.0, k2=5.0,\n"
    "                             E0=1.0, S0=100.0, t_max=5.0, n_points=50):\n"
    "    Vmax = k2 * E0\n"
)
assert content.count(marker) == 1, "marker no encontrado (o no es unico) -- revisar a mano"

replacement = (
    "_VALID_ENZYME_KINETICS_MODES = (\"full_kinetics\", \"michaelis_menten\", \"compare\")\n\n\n"
    "def compute_enzyme_kinetics(mode=\"compare\", k1=100.0, km1=10.0, k2=5.0,\n"
    "                             E0=1.0, S0=100.0, t_max=5.0, n_points=50):\n"
    "    if mode not in _VALID_ENZYME_KINETICS_MODES:\n"
    "        return {\n"
    "            \"error\": f\"mode desconocido: '{mode}'\",\n"
    "            \"modos_validos\": list(_VALID_ENZYME_KINETICS_MODES),\n"
    "        }\n"
    "    Vmax = k2 * E0\n"
)

BACKUP.write_text(content, encoding="utf-8")
TARGET.write_text(content.replace(marker, replacement, 1), encoding="utf-8")

print(f"Backup guardado en {BACKUP}")
print(f"{TARGET} actualizado: mode invalido ahora devuelve {{'error': ...}} de entrada, "
      "sin correr Octave ni caer en la rama 'compare' por defecto.")
print(f"\nRevisa el diff con: git diff {TARGET}")
print(f"Si algo salio mal, restaura con: cp {BACKUP} {TARGET}")
