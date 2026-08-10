#!/usr/bin/env python3
"""
smoke_test.py — descubre los tools reales en server.py via ast (sin lista
hardcodeada), importa cada modulo *_tool.py, y llama a cada compute_X con un
modo invalido esperando un ValueError claro (no un traceback crudo).

Objetivo: confirmar que el downgrade de numpy 2.5.1 -> 2.4.x no rompio ningun
import, y que el dispatcher interno de cada tool sigue conectado.

Uso:
    cd ~/mcp-octave-real
    python3 smoke_test.py
"""
import ast
import importlib
import sys

SERVER_PY = "server.py"
INVALID = "__smoketest_invalid__"


def discover_imports(path):
    """Devuelve lista de (modulo, nombre_funcion, alias) para imports tipo
    'from X_tool import compute_Y [as alias]' en server.py."""
    tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.endswith("_tool"):
            for alias in node.names:
                if alias.name.startswith("compute_"):
                    out.append((node.module, alias.name, alias.asname or alias.name))
    return out


def try_import(module_name):
    try:
        mod = importlib.import_module(module_name)
        return mod, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


import json

_ERROR_KEYS = ("error", "errors", "mensaje_error", "error_msg")


def _dict_has_error_key(d):
    return isinstance(d, dict) and any(
        isinstance(k, str) and k.lower() in _ERROR_KEYS for k in d.keys()
    )


def _looks_like_error_response(result):
    """Varios tools no hacen raise ValueError para modo invalido: devuelven
    un dict con una clave tipo 'error', o (ej. filosofia_historia_mate_tool)
    un string JSON serializado con esa misma clave. Los tres patrones son
    validos."""
    if _dict_has_error_key(result):
        return True
    if isinstance(result, str):
        try:
            parsed = json.loads(result)
        except (ValueError, TypeError):
            return False
        return _dict_has_error_key(parsed)
    return False


def _attempt(call):
    """Ejecuta call() y clasifica el resultado.
    Devuelve (status, detalle) con status in {OK, TYPEERROR, FAIL}."""
    try:
        result = call()
    except ValueError:
        return "OK", "ValueError esperado"
    except TypeError as e:
        return "TYPEERROR", str(e)
    except Exception as e:
        return "FAIL", f"{type(e).__name__} inesperado (no ValueError): {e}"
    else:
        if _looks_like_error_response(result):
            return "OK", "dict con clave de error devuelto (patron alternativo a ValueError)"
        return "FAIL", f"acepto el modo invalido sin señal de error (devolvio {type(result).__name__})"


def try_smoketest_call(func):
    """Prueba varias firmas comunes (mode=, operation=, posicional) hasta
    encontrar la que acepta el modulo. Acepta como valido tanto
    'raise ValueError' como 'return {"error": ...}'. Devuelve (status, detalle):
    OK   -> el tool senializo el modo invalido de alguna forma reconocida
    FAIL -> lanzo otra excepcion, o acepto el modo invalido sin decir nada
    SKIP -> ninguna firma probada calzo (TypeError en las tres)
    """
    # Probamos las tres firmas completas en vez de cortar en la primera que
    # no da TypeError: un kwarg con nombre incorrecto puede ser absorbido en
    # silencio por un **kwargs y "tener exito" sin haber tocado el dispatch
    # real (paso por hilbert_tool/graph_tool/qm_tool, cuyo parametro real es
    # 'preset' pero tienen **kwargs). Nos quedamos con el primer OK genuino;
    # si ninguno da OK, reportamos el mejor FAIL/SKIP disponible.
    attempts = []
    for kwarg_name in ("mode", "operation", "preset"):
        status, detail = _attempt(lambda k=kwarg_name: func(**{k: INVALID}))
        attempts.append((kwarg_name, status, detail))
        if status == "OK":
            return "OK", detail + f" (via kwarg '{kwarg_name}')"

    status, detail = _attempt(lambda: func(INVALID))
    if status == "OK":
        return "OK", detail + " (via posicional)"
    attempts.append(("posicional", status, detail))

    if all(s == "TYPEERROR" for _, s, _ in attempts):
        last = attempts[-1][2]
        return "SKIP", f"firma no reconocida (mode=/operation=/preset=/posicional fallaron): {last}"

    # Priorizamos reportar un FAIL real (no un TypeError) si lo hay -- es
    # mas informativo que decir "no calzo ninguna firma".
    for name, status, detail in attempts:
        if status == "FAIL":
            return "FAIL", detail + f" (via '{name}')"
    return "SKIP", f"firma ambigua, revisar a mano: {attempts}"


def main():
    imports = discover_imports(SERVER_PY)
    print(f"Encontrados {len(imports)} imports de compute_* en {SERVER_PY}\n")

    results = {"IMPORT_FAIL": [], "OK": [], "FAIL": [], "SKIP": []}

    for module_name, func_name, alias in imports:
        mod, err = try_import(module_name)
        if err:
            results["IMPORT_FAIL"].append((module_name, err))
            print(f"[IMPORT_FAIL] {module_name}: {err}")
            continue

        func = getattr(mod, func_name, None)
        if func is None:
            msg = f"{func_name} no existe en el modulo"
            results["IMPORT_FAIL"].append((module_name, msg))
            print(f"[IMPORT_FAIL] {module_name}.{func_name}: {msg}")
            continue

        status, detail = try_smoketest_call(func)
        results[status].append((f"{module_name}.{alias}", detail))
        print(f"[{status}] {module_name}.{alias}: {detail}")

    print("\n--- resumen ---")
    total = sum(len(v) for v in results.values())
    for status in ("OK", "FAIL", "SKIP", "IMPORT_FAIL"):
        print(f"{status}: {len(results[status])} / {total}")

    if results["FAIL"] or results["IMPORT_FAIL"]:
        print("\nA revisar:")
        for name, detail in results["FAIL"] + results["IMPORT_FAIL"]:
            print(f"  - {name}: {detail}")
        sys.exit(1)

    if results["SKIP"]:
        print("\nSKIP (firma no estandar, revisar a mano si importa):")
        for name, detail in results["SKIP"]:
            print(f"  - {name}: {detail}")

    print("\nTodos los tools importables y con firma reconocida pasaron el smoke-test.")


if __name__ == "__main__":
    main()
