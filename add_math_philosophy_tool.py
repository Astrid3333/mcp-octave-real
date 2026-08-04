#!/usr/bin/env python3
"""
add_math_philosophy_tool.py

Inserta el registro de math_philosophy_history en server.py de forma segura:
- corre desde ~/mcp_octave (busca server.py en el directorio actual)
- hace backup a server.py.bak antes de tocar nada
- si el tool ya esta registrado, no hace nada (evita duplicados si se corre 2 veces)
- inserta el bloque ANTES de 'if __name__ == "__main__":' si ese bloque existe
  -- importante: si se pegara DESPUES de mcp.run(), nunca se ejecutaria,
  porque mcp.run() bloquea y el interprete no llega a leer lo que sigue
- si no hay bloque __main__, agrega al final del archivo

Uso:
    cd ~/mcp_octave
    python3 add_math_philosophy_tool.py
"""
import shutil
import sys
from pathlib import Path

SERVER_PATH = Path("server.py")
MARKER = "math_philosophy_history"

INSERT_BLOCK = '''
from filosofia_historia_mate_tool import compute_math_philosophy_history

@mcp.tool()
def math_philosophy_history(topic: str = "", params: dict = None) -> str:
    """Referencia sobre filosofia e historia de la matematica (8 topics)."""
    return compute_math_philosophy_history(topic, params)

'''

def main():
    if not SERVER_PATH.exists():
        print(f"ERROR: no encuentro {SERVER_PATH.resolve()} -- corre esto desde ~/mcp_octave")
        sys.exit(1)

    content = SERVER_PATH.read_text()

    if MARKER in content:
        print("math_philosophy_history ya esta registrada en server.py -- no toco nada.")
        return

    backup_path = SERVER_PATH.with_suffix(".py.bak")
    shutil.copy(SERVER_PATH, backup_path)

    main_marker = 'if __name__ == "__main__":'
    idx = content.find(main_marker)

    if idx == -1:
        new_content = content.rstrip() + "\n" + INSERT_BLOCK
        where = "al final del archivo (no encontre bloque __main__)"
    else:
        new_content = content[:idx] + INSERT_BLOCK + "\n" + content[idx:]
        where = "justo antes de if __name__ == \"__main__\":"

    SERVER_PATH.write_text(new_content)
    print(f"Listo. Insertado {where}.")
    print(f"Backup del original en {backup_path}")
    print("Reinicia Claude Desktop para que cargue el tool nuevo.")

if __name__ == "__main__":
    main()
