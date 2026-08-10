"""
patch_wire_optical_sequence_id.py

Wirea optical_sequence_id_tool.py en server.py:
  1. Agrega el import (despues del ultimo import de un modulo *_tool)
  2. Agrega la funcion wrapper @mcp.tool() al final del archivo

Requiere que polarization_mapping_tool.py ya este wireado (optical_sequence_id
lo importa directamente).

Uso:
    cp ~/Descargas/optical_sequence_id_tool.py ~/mcp-octave-real/
    cp ~/Descargas/patch_wire_optical_sequence_id.py ~/mcp-octave-real/
    cd ~/mcp-octave-real
    python3 patch_wire_optical_sequence_id.py
    python3 -c "import ast; ast.parse(open('server.py').read()); print('sintaxis OK')"
    python3 -c "import server; print('import de server.py OK')"
    git diff server.py
"""

import re
import shutil
import sys

SERVER_PATH = "server.py"
BACKUP_PATH = "server.py.bak_opticalsequenceid"

IMPORT_LINE = "from optical_sequence_id_tool import compute_optical_sequence_id\n"

TOOL_FUNC = '''

@mcp.tool()
def optical_sequence_id_tool(mode: str = "generate", params: dict = None) -> dict:
    """Simula difraccion de un haz coherente sobre una mascara de fase 2D derivada de polarization_mapping, para generar un identificador optico de una secuencia de ADN. mode='generate': genera el id (params: seq, mapping='slit_1d'|'folded_2d'|'codon_blocks' default slit_1d, diffraction='fraunhofer'|'fresnel' default fraunhofer, output_size default 128, wavelength/distance/dx solo para fresnel, hash_precision, top_k_peaks, include_pattern). mode='compare': compara dos secuencias (params: seq_a, seq_b, + mismos params fisicos) devolviendo pattern_correlation (correlacion pixel a pixel, discrimina bien) y ambos hashes. mode='validate_energy_conservation'/'validate_translation_invariance'/'validate_all': controles sinteticos de la implementacion de difraccion. Devuelve dict serializable; errores como {"error": ...} sin excepcion."""
    return compute_optical_sequence_id(mode, **(params or {}))
'''


def main():
    try:
        with open(SERVER_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: no se encontro {SERVER_PATH} en el directorio actual.")
        sys.exit(1)

    if "compute_optical_sequence_id" in content:
        print("optical_sequence_id ya parece estar wireado en server.py (se encontro "
              "'compute_optical_sequence_id'). No se hicieron cambios.")
        sys.exit(0)

    if "compute_polarization_mapping" not in content:
        print("ADVERTENCIA: no se encontro 'compute_polarization_mapping' en server.py. "
              "optical_sequence_id_tool.py depende de polarization_mapping_tool.py -- "
              "asegurate de que ese modulo ya este wireado y presente en el repo antes "
              "de continuar. Se sigue de todos modos.")

    shutil.copy(SERVER_PATH, BACKUP_PATH)
    print(f"Backup guardado en {BACKUP_PATH}")

    import_pattern = re.compile(r"^from \w+ import compute_\w+\n", re.MULTILINE)
    matches = list(import_pattern.finditer(content))
    if not matches:
        print("ERROR: no se encontro ningun import 'from X import compute_Y' como referencia. "
              "Abortando sin modificar server.py.")
        sys.exit(1)
    last_match = matches[-1]
    insert_pos = last_match.end()
    content = content[:insert_pos] + IMPORT_LINE + content[insert_pos:]

    content = content.rstrip("\n") + "\n" + TOOL_FUNC

    with open(SERVER_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("server.py actualizado: import de optical_sequence_id_tool agregado, "
          "wrapper optical_sequence_id_tool() agregado al final con @mcp.tool().")
    print("Revisa el diff con: git diff server.py")
    print(f"Si algo salio mal, restaura con: cp {BACKUP_PATH} server.py")


if __name__ == "__main__":
    main()
