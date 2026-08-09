#!/usr/bin/env python3
"""
Wirea glm_tool.py en server.py: agrega el import y registra la funcion
@mcp.tool(). Mismo patron append-only que los patches anteriores (statphys,
cfd, statistics_extended): no toca nada existente, solo agrega al final.

Uso: correr desde dentro de ~/mcp-octave-real, con glm_tool.py ya copiado ahi.
    python3 patch_wire_glm.py
"""
from pathlib import Path

SERVER = Path("server.py")
MODULE = Path("glm_tool.py")
assert SERVER.exists(), "Correr este script dentro de ~/mcp-octave-real"
assert MODULE.exists(), "Falta glm_tool.py en el directorio actual"

src = SERVER.read_text()

backup = SERVER.with_suffix(".py.bak6")
backup.write_text(src)
print(f"Backup guardado en {backup}")

IMPORT_LINE = "from glm_tool import compute_glm"
TOOL_BLOCK = '''

@mcp.tool()
def glm_tool(mode: str, params: dict = None) -> dict:
    """Fase B de estadistica: modelos lineales generalizados y regresion regularizada. mode='logistic_regression': regresion logistica binaria via IRLS, devuelve coeficientes, odds ratios, errores estandar y p-values de Wald. mode='poisson_regression': GLM de conteos (link log) via IRLS, devuelve incidence rate ratios. mode='ridge_lasso': Ridge (solucion cerrada) o Lasso (coordinate descent), con seleccion de lambda via validacion cruzada k-fold; params incluye method='ridge'|'lasso'. Validado cruzado contra sklearn."""
    return compute_glm(mode, params or {})
'''

assert IMPORT_LINE not in src, "El import ya esta presente; parece que ya se corrio este patch."

anchor_candidates = [
    "from statistics_extended_tool import compute_statistics_extended",
    "from cfd_tool import compute_cfd",
]
anchor = next((a for a in anchor_candidates if a in src), None)

if anchor:
    src = src.replace(anchor, anchor + "\n" + IMPORT_LINE, 1)
    print(f"Import de glm_tool agregado (despues de '{anchor.split()[1]}').")
else:
    idx = src.find("@mcp.tool()")
    assert idx != -1, "No se encontro ningun @mcp.tool() en server.py"
    src = src[:idx] + IMPORT_LINE + "\n\n\n" + src[idx:]
    print("Import de glm_tool agregado (fallback: antes del primer @mcp.tool()).")

src = src.rstrip("\n") + "\n" + TOOL_BLOCK
print("Funcion glm_tool agregada.")

SERVER.write_text(src)
print("server.py actualizado.")
print()
print("Revisa el diff con: git diff server.py")
print("Si algo salio mal, restaura con: cp server.py.bak6 server.py")
