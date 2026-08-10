#!/usr/bin/env python3
"""
patch_update_docstring_stochastic.py
Actualiza la docstring del wrapper stochastic_processes_tool en server.py para
que mencione el modo 'mcmc' (Fase D). Usa regex sobre la funcion en vez de un
match de texto exacto, porque el patch anterior (patch_add_mcmc.py) no
encontro la docstring literal esperada y no toco server.py.

Correr desde ~/mcp-octave-real:
    python3 patch_update_docstring_stochastic.py
"""
import re
from pathlib import Path

SERVER = Path("server.py")
assert SERVER.exists(), "Falta server.py en el directorio actual"

src = SERVER.read_text()

NEW_DOC = (
    "Procesos estocasticos: movimiento browniano (estandar/con drift/geometrico), "
    "proceso de Ornstein-Uhlenbeck (reversion a la media, util para variables "
    "ambientales con equilibrio), cadenas de Markov discretas (distribucion "
    "estacionaria, tiempo de primer paso), y mcmc (Metropolis-Hastings generico: "
    "target gaussiano o custom via expresion sympy, devuelve media/covarianza "
    "posterior, acceptance rate y effective sample size)."
)

# Localiza la funcion wrapper completa (decorador + def + docstring) sin asumir
# el texto exacto de la docstring vieja.
pattern = re.compile(
    r'(@mcp\.tool\(\)\s*\ndef stochastic_processes\([^)]*\)\s*->\s*dict:\s*\n\s*""")'
    r'(.*?)'
    r'(""")',
    re.DOTALL,
)

match = pattern.search(src)
if match is None:
    print("AVISO: no se encontro la funcion 'stochastic_processes' en server.py con el patron esperado.")
    print("No se modifico nada. Revisa manualmente el wrapper en server.py.")
else:
    old_doc_body = match.group(2)
    if "mcmc" in old_doc_body:
        print("La docstring ya menciona 'mcmc', no se modifica nada.")
    else:
        backup = SERVER.with_suffix(".py.bak_docmcmc")
        backup.write_text(src)
        print(f"Backup guardado en {backup}")

        new_src = src[:match.start(2)] + NEW_DOC + src[match.end(2):]
        SERVER.write_text(new_src)
        print("Docstring de stochastic_processes_tool en server.py actualizada.")
        print("\nRevisa el diff con: git diff server.py")
        print("Si algo salio mal, restaura con: cp server.py.bak_docmcmc server.py")
