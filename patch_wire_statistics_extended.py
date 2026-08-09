#!/usr/bin/env python3
"""
Wirea statistics_extended_tool.py en server.py: agrega el import y registra
la funcion @mcp.tool(). Mismo patron append-only que patch_wire_statphys.py
y patch_wire_cfd.py (no toca nada existente, solo agrega al final).

Uso: correr desde dentro de ~/mcp-octave-real, con statistics_extended_tool.py
ya copiado ahi.
    python3 patch_wire_statistics_extended.py
"""
from pathlib import Path

SERVER = Path("server.py")
MODULE = Path("statistics_extended_tool.py")
assert SERVER.exists(), "Correr este script dentro de ~/mcp-octave-real"
assert MODULE.exists(), "Falta statistics_extended_tool.py en el directorio actual"

src = SERVER.read_text()

backup = SERVER.with_suffix(".py.bak5")
backup.write_text(src)
print(f"Backup guardado en {backup}")

IMPORT_LINE = "from statistics_extended_tool import compute_statistics_extended"
TOOL_BLOCK = '''

@mcp.tool()
def statistics_extended_tool(mode: str, params: dict = None) -> dict:
    """Fase A de estadistica: descriptiva/EDA (descriptive_stats: media, mediana, moda, cuartiles, asimetria, curtosis, outliers IQR/z-score), tablas de contingencia con chi-cuadrado (contingency_table), tests de 2 muestras parametricos y no parametricos (two_sample_tests: ttest_ind, ttest_paired, mannwhitney, wilcoxon, ks_2samp), ANOVA de 1 via con post-hoc Bonferroni (anova_oneway), tests de normalidad (normality_tests: shapiro, jarque_bera), y remuestreo (resampling: bootstrap percentil/BCa, test de permutaciones). Validado cruzado contra scipy.stats."""
    return compute_statistics_extended(mode, params or {})
'''

assert IMPORT_LINE not in src, "El import ya esta presente; parece que ya se corrio este patch."

# Insertar el import junto a los otros imports de tools tardios (mismo lugar
# que los patches anteriores: al final del bloque de imports, antes del
# primer @mcp.tool() que le sigue)
if "from cfd_tool import compute_cfd" in src:
    src = src.replace(
        "from cfd_tool import compute_cfd",
        "from cfd_tool import compute_cfd\n" + IMPORT_LINE,
        1,
    )
    print("Import de statistics_extended_tool agregado (despues de cfd_tool).")
else:
    # fallback: agregar el import justo antes del primer @mcp.tool()
    idx = src.find("@mcp.tool()")
    assert idx != -1, "No se encontro ningun @mcp.tool() en server.py"
    src = src[:idx] + IMPORT_LINE + "\n\n\n" + src[idx:]
    print("Import de statistics_extended_tool agregado (fallback: antes del primer @mcp.tool()).")

src = src.rstrip("\n") + "\n" + TOOL_BLOCK
print("Funcion statistics_extended_tool agregada.")

SERVER.write_text(src)
print("server.py actualizado.")
print()
print("Revisa el diff con: git diff server.py")
print("Si algo salio mal, restaura con: cp server.py.bak5 server.py")
