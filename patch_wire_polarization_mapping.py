"""
patch_wire_polarization_mapping.py

Wirea polarization_mapping_tool.py en server.py:
  1. Agrega el import (despues del ultimo import de un modulo *_tool)
  2. Agrega la funcion wrapper @mcp.tool() al final del archivo

Uso:
    cp ~/Descargas/polarization_mapping_tool.py ~/mcp-octave-real/
    cp ~/Descargas/patch_wire_polarization_mapping.py ~/mcp-octave-real/
    cd ~/mcp-octave-real
    python3 patch_wire_polarization_mapping.py
    python3 -c "import ast; ast.parse(open('server.py').read()); print('sintaxis OK')"
    python3 -c "import server; print('import de server.py OK')"
    git diff server.py
"""

import re
import shutil
import sys

SERVER_PATH = "server.py"
BACKUP_PATH = "server.py.bak_polarizationmapping"

IMPORT_LINE = "from polarization_mapping_tool import compute_polarization_mapping\n"

TOOL_FUNC = '''

@mcp.tool()
def polarization_mapping_tool(mode: str = "map_sequence", params: dict = None) -> dict:
    """Mapea secuencias de ADN a vectores de Stokes [S0,S1,S2,S3], generalizando spin_complex (S1=purina/pirimidina, S2=puente H) y agregando S3 (marco de lectura, posicion mod 3). Primer paso del pipeline hacia optical_sequence_id. mode='map_sequence': mapea una secuencia (params: seq). mode='validate_purine_pyrimidine'/'validate_hydrogen_bond'/'validate_periodicity'(params: repeats opcional, default 30)/'validate_all': corren los controles sinteticos de validacion. Devuelve dict serializable; errores como {"error": ...} sin excepcion."""
    return compute_polarization_mapping(mode, **(params or {}))
'''


def main():
    try:
        with open(SERVER_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: no se encontro {SERVER_PATH} en el directorio actual.")
        sys.exit(1)

    if "compute_polarization_mapping" in content:
        print("polarization_mapping ya parece estar wireado en server.py (se encontro "
              "'compute_polarization_mapping'). No se hicieron cambios.")
        sys.exit(0)

    shutil.copy(SERVER_PATH, BACKUP_PATH)
    print(f"Backup guardado en {BACKUP_PATH}")

    # 1) Insertar el import despues del ultimo "from X_tool import compute_Y"
    import_pattern = re.compile(r"^from \w+ import compute_\w+\n", re.MULTILINE)
    matches = list(import_pattern.finditer(content))
    if not matches:
        print("ERROR: no se encontro ningun import 'from X import compute_Y' como referencia. "
              "Abortando sin modificar server.py.")
        sys.exit(1)
    last_match = matches[-1]
    insert_pos = last_match.end()
    content = content[:insert_pos] + IMPORT_LINE + content[insert_pos:]

    # 2) Agregar la funcion wrapper al final del archivo
    content = content.rstrip("\n") + "\n" + TOOL_FUNC

    with open(SERVER_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("server.py actualizado: import de polarization_mapping_tool agregado, "
          "wrapper polarization_mapping_tool() agregado al final con @mcp.tool().")
    print("Revisa el diff con: git diff server.py")
    print(f"Si algo salio mal, restaura con: cp {BACKUP_PATH} server.py")


if __name__ == "__main__":
    main()
