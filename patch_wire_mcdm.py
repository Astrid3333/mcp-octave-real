#!/usr/bin/env python3
"""
patch_wire_mcdm.py
Wirea mcdm_tool.py en server.py: agrega el import y el wrapper @mcp.tool()
para el nuevo tool mcdm (AHP, TOPSIS, weighted_sum/weighted_product).

Correr desde ~/mcp-octave-real:
    python3 patch_wire_mcdm.py
"""
from pathlib import Path

SERVER = Path("server.py")
MCDM = Path("mcdm_tool.py")

assert SERVER.exists(), "Falta server.py en el directorio actual"
assert MCDM.exists(), "Falta mcdm_tool.py en el directorio actual"

src = SERVER.read_text()

if "compute_mcdm" in src:
    print("mcdm_tool ya esta wireado en server.py, no se modifica nada.")
else:
    backup = SERVER.with_suffix(".py.bak_mcdm")
    backup.write_text(src)
    print(f"Backup guardado en {backup}")

    # --- import: se agrega despues del import de clustering_tool (el ultimo wireado) ---
    anchor_import = "from clustering_tool import compute_clustering"
    assert anchor_import in src, (
        "No se encontro el import de clustering_tool en server.py; "
        "revisa manualmente donde agregar 'from mcdm_tool import compute_mcdm'."
    )
    src = src.replace(anchor_import, anchor_import + "\nfrom mcdm_tool import compute_mcdm", 1)
    print("Import de mcdm_tool agregado (despues de 'clustering_tool').")

    # --- wrapper: se agrega al final del archivo ---
    WRAPPER = '''

@mcp.tool()
def mcdm_tool(mode: str, params: dict = None) -> dict:
    """Decision multicriterio: AHP (ponderacion de criterios via matriz de comparacion pareada, con ratio de consistencia de Saaty), TOPSIS (ranking de alternativas por cercania a los ideales positivo/negativo), y weighted_sum (WSM/WPM: suma o producto ponderado con normalizacion min-max, params incluye method='sum'|'product'). params: pairwise_matrix/criteria_names (ahp); decision_matrix, weights, criteria_types, alternative_names (topsis/weighted_sum)."""
    return compute_mcdm(mode, **(params or {}))
'''
    src = src.rstrip("\n") + "\n" + WRAPPER
    SERVER.write_text(src)
    print("Funcion mcdm_tool agregada al final de server.py.")
    print("\nRevisa el diff con: git diff server.py")
    print("Si algo salio mal, restaura con: cp server.py.bak_mcdm server.py")
