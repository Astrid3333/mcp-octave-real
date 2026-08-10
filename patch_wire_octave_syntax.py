#!/usr/bin/env python3
"""
patch_wire_octave_syntax.py
Wirea octave_syntax_tool.py en server.py: agrega el import y el wrapper
@mcp.tool() para el nuevo tool octave_syntax (validacion de sintaxis sin
ejecutar codigo).

Requiere que el binario 'octave' este instalado y en PATH (ya lo tenes,
es el mismo interprete que usas para el resto de mcp-octave-real).

Correr desde ~/mcp-octave-real:
    python3 patch_wire_octave_syntax.py
"""
from pathlib import Path

SERVER = Path("server.py")
SYNTAX = Path("octave_syntax_tool.py")

assert SERVER.exists(), "Falta server.py en el directorio actual"
assert SYNTAX.exists(), "Falta octave_syntax_tool.py en el directorio actual"

src = SERVER.read_text()

if "compute_octave_syntax" in src:
    print("octave_syntax_tool ya esta wireado en server.py, no se modifica nada.")
else:
    backup = SERVER.with_suffix(".py.bak_octavesyntax")
    backup.write_text(src)
    print(f"Backup guardado en {backup}")

    # --- import: se agrega despues del import de mcdm_tool (el ultimo wireado) ---
    anchor_import = "from mcdm_tool import compute_mcdm"
    assert anchor_import in src, (
        "No se encontro el import de mcdm_tool en server.py; "
        "revisa manualmente donde agregar 'from octave_syntax_tool import compute_octave_syntax'."
    )
    src = src.replace(anchor_import, anchor_import + "\nfrom octave_syntax_tool import compute_octave_syntax", 1)
    print("Import de octave_syntax_tool agregado (despues de 'mcdm_tool').")

    # --- wrapper: se agrega al final del archivo ---
    WRAPPER = '''

@mcp.tool()
def octave_syntax_tool(mode: str, params: dict = None) -> dict:
    """Valida la sintaxis de un fragmento de codigo Octave sin ejecutarlo: envuelve el codigo en una definicion de funcion y la carga via source(), lo que fuerza a Octave a parsear el cuerpo completo (detectando parentesis sin cerrar, 'end'/'endfor'/'endif' faltantes o mal anidados, tokens invalidos, etc.) sin correr ninguna linea del codigo del usuario. mode='syntax_check'. params: code (el fragmento a validar), timeout (segundos, default 10). Devuelve valid=true/false y, si hay error, el mensaje crudo de Octave y la linea detectada."""
    return compute_octave_syntax(mode, **(params or {}))
'''
    src = src.rstrip("\n") + "\n" + WRAPPER
    SERVER.write_text(src)
    print("Funcion octave_syntax_tool agregada al final de server.py.")
    print("\nRevisa el diff con: git diff server.py")
    print("Si algo salio mal, restaura con: cp server.py.bak_octavesyntax server.py")
