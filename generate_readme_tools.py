#!/usr/bin/env python3
"""
generate_readme_tools.py

Genera README_TOOLS.md a partir de server.py, parseando con ast en vez de
mantener una lista a mano (que ya vimos dos veces en este repo que se
desactualiza -- chemometrics/econometrics/archaeological_simulation
"aparecieron" ya construidos sin que quedara registrado en ningun lado).

Fuente de verdad: cada funcion decorada con @mcp.tool() en server.py. De
cada una se extrae: nombre, firma completa (para saber si es mode= u
operation=, y el default), y el docstring completo (lo que FastMCP expone
al cliente MCP como descripcion del tool).

Uso:
    python3 generate_readme_tools.py            # escribe README_TOOLS.md
    python3 generate_readme_tools.py --check     # no escribe nada, solo
                                                   # avisa si README_TOOLS.md
                                                   # esta desactualizado
                                                   # (exit code 1 si difiere)

Correr de nuevo cada vez que se agregue/cambie un @mcp.tool() -- no editar
README_TOOLS.md a mano, se pisa en el proximo run.
"""
import ast
import sys
import pathlib
from datetime import datetime, timezone

SERVER_PY = pathlib.Path("server.py")
OUTPUT = pathlib.Path("README_TOOLS.md")


def _is_mcp_tool_decorator(dec):
    # @mcp.tool() -> Call(func=Attribute(value=Name(id='mcp'), attr='tool'))
    return (
        isinstance(dec, ast.Call)
        and isinstance(dec.func, ast.Attribute)
        and dec.func.attr == "tool"
        and isinstance(dec.func.value, ast.Name)
    )


def _format_arg(arg, default):
    ann = ""
    if arg.annotation is not None:
        try:
            ann = f": {ast.unparse(arg.annotation)}"
        except Exception:
            ann = ""
    if default is not None:
        try:
            default_str = ast.unparse(default)
        except Exception:
            default_str = "..."
        return f"{arg.arg}{ann} = {default_str}"
    return f"{arg.arg}{ann}"


def _format_signature(fn_node):
    args = fn_node.args
    defaults = [None] * (len(args.args) - len(args.defaults)) + list(args.defaults)
    parts = [_format_arg(a, d) for a, d in zip(args.args, defaults)]
    return ", ".join(parts)


def discover_mcp_tools(server_py_path=SERVER_PY):
    tree = ast.parse(server_py_path.read_text(encoding="utf-8"), filename=str(server_py_path))
    tools = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if not any(_is_mcp_tool_decorator(d) for d in node.decorator_list):
            continue
        doc = ast.get_docstring(node) or "(sin docstring)"
        tools.append({
            "name": node.name,
            "signature": _format_signature(node),
            "doc": " ".join(doc.split()),  # colapsa espacios/saltos de linea
            "lineno": node.lineno,
        })
    return sorted(tools, key=lambda t: t["name"])


def render_markdown(tools, server_py_path=SERVER_PY):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Tools disponibles en octave-mcp",
        "",
        f"Generado automaticamente desde `{server_py_path}` el {now} "
        f"por `generate_readme_tools.py`. **No editar a mano** -- correr "
        f"el generador de nuevo despues de agregar o modificar un tool.",
        "",
        f"Total: {len(tools)} tools expuestos via `@mcp.tool()`.",
        "",
        "---",
        "",
    ]
    for t in tools:
        lines.append(f"## `{t['name']}`")
        lines.append("")
        lines.append(f"```python\n{t['name']}({t['signature']})\n```")
        lines.append("")
        lines.append(t["doc"])
        lines.append("")
        lines.append(f"<sub>definido en `{server_py_path}:{t['lineno']}`</sub>")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    if not SERVER_PY.exists():
        print(f"No se encontro {SERVER_PY} en el directorio actual.", file=sys.stderr)
        sys.exit(2)

    tools = discover_mcp_tools()
    if not tools:
        print("No se encontro ningun @mcp.tool() en server.py -- algo esta raro, revisar a mano.", file=sys.stderr)
        sys.exit(2)

    rendered = render_markdown(tools)

    check_mode = "--check" in sys.argv
    if check_mode:
        if not OUTPUT.exists():
            print(f"{OUTPUT} no existe todavia. Correr sin --check para generarlo.")
            sys.exit(1)
        current = OUTPUT.read_text(encoding="utf-8")
        # Ignoramos la linea de timestamp al comparar, si no siempre va a diferir.
        current_body = "\n".join(l for l in current.splitlines() if not l.startswith("Generado automaticamente"))
        new_body = "\n".join(l for l in rendered.splitlines() if not l.startswith("Generado automaticamente"))
        if current_body == new_body:
            print(f"{OUTPUT} esta actualizado ({len(tools)} tools).")
            sys.exit(0)
        else:
            print(f"{OUTPUT} esta DESACTUALIZADO respecto a {SERVER_PY}. Correr sin --check para regenerarlo.")
            sys.exit(1)

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"{OUTPUT} generado con {len(tools)} tools.")


if __name__ == "__main__":
    main()
