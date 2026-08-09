#!/usr/bin/env python3
"""
Patch de la fase 1 (materiales):
1. Extiende finite_element_tool.py con 4 modos nuevos:
   thermal_steady_1d, thermal_transient_1d, thermal_steady_2d, stress_plane
   (usa thermal_analysis.py y stress_analysis.py, que deben estar en el
   mismo directorio).
2. Wirea composite_homogenization.py como tool nuevo en server.py.

Uso: correr desde dentro de ~/mcp-octave-real
    python3 patch_wire_materials.py

Requiere que thermal_analysis.py, stress_analysis.py y
composite_homogenization.py ya esten copiados en el directorio.
"""
from pathlib import Path

FET = Path("finite_element_tool.py")
SERVER = Path("server.py")
for p in (FET, SERVER, Path("thermal_analysis.py"), Path("stress_analysis.py"),
          Path("composite_homogenization.py")):
    assert p.exists(), f"Falta {p} -- correr este script dentro de ~/mcp-octave-real"

# ------------------------------------------------------------------
# 1. Parchear finite_element_tool.py
# ------------------------------------------------------------------
fet_src = FET.read_text()
fet_backup = FET.with_suffix(".py.bak")
fet_backup.write_text(fet_src)
print(f"Backup guardado en {fet_backup}")

# 1a. Agregar imports de los submodulos nuevos, justo debajo de "import numpy as np"
old_import = "import numpy as np"
new_import = (
    "import numpy as np\n"
    "import thermal_analysis as _thermal\n"
    "import stress_analysis as _stress"
)
assert fet_src.count(old_import) == 1, "no se encontro 'import numpy as np' de forma unica"
fet_src = fet_src.replace(old_import, new_import, 1)

# 1b. Ampliar el enum de modos en el schema
old_enum = '"mode": {"type": "string", "enum": ["bar_1d", "beam_bending", "truss_2d"]},'
new_enum = (
    '"mode": {"type": "string", "enum": ['
    '"bar_1d", "beam_bending", "truss_2d", '
    '"thermal_steady_1d", "thermal_transient_1d", "thermal_steady_2d", '
    '"stress_plane"]},'
)
assert fet_src.count(old_enum) == 1, "no se encontro el enum de mode de forma unica"
fet_src = fet_src.replace(old_enum, new_enum, 1)

# 1c. Agregar las 4 funciones wrapper nuevas, antes de "def compute_finite_element"
new_functions = '''
def _thermal_steady_1d(length, n_nodes, k, T_left, T_right, q=None):
    x, T = _thermal.steady_1d(length, n_nodes, k, T_left, T_right, q)
    return {
        "mode": "thermal_steady_1d",
        "x": x.tolist(),
        "temperature": T.tolist(),
    }


def _thermal_transient_1d(length, n_nodes, alpha, T_initial, T_left, T_right, t_end, n_steps):
    x, T = _thermal.transient_1d(length, n_nodes, alpha, T_initial, T_left, T_right, t_end, n_steps)
    return {
        "mode": "thermal_transient_1d",
        "x": x.tolist(),
        "temperature_final": T.tolist(),
        "t_end": t_end,
    }


def _thermal_steady_2d(Lx, Ly, nx, ny, T_top, T_bottom=0.0, T_left=0.0, T_right=0.0):
    T = _thermal.steady_2d(Lx, Ly, nx, ny, T_top, T_bottom, T_left, T_right)
    return {
        "mode": "thermal_steady_2d",
        "temperature_grid": T.tolist(),
        "nx": nx, "ny": ny,
    }


def _stress_plane(Lx, Ly, nx, ny, E, nu, sigma_applied, mode_elasticity="plane_stress", thickness=1.0):
    nodes, U, stresses = _stress.solve_plane_plate(
        Lx, Ly, nx, ny, E, nu, mode_elasticity, sigma_applied, thickness
    )
    sxx_mean = float(stresses[:, 0].mean())
    return {
        "mode": "stress_plane",
        "sigma_xx_mean": sxx_mean,
        "sigma_yy_mean": float(stresses[:, 1].mean()),
        "sigma_xy_mean": float(stresses[:, 2].mean()),
        "sigma_xx_applied": sigma_applied,
        "relative_error_pct": 100 * abs(sxx_mean - sigma_applied) / sigma_applied,
        "note": (
            "Malla rectangular estructurada (Q4). No incluye geometria "
            "circular (caso de Kirsch) todavia."
        ),
    }


'''
anchor = "def compute_finite_element(mode, params=None):"
assert fet_src.count(anchor) == 1, "no se encontro compute_finite_element de forma unica"
fet_src = fet_src.replace(anchor, new_functions + anchor, 1)

# 1d. Agregar las ramas nuevas al dispatcher, antes del "else:" final
old_dispatch_tail = (
    '    elif mode == "truss_2d":\n'
    '        return _truss_2d(**params)\n'
    '    else:\n'
    '        raise ValueError(f"modo desconocido: {mode}. Use bar_1d | beam_bending | truss_2d")'
)
new_dispatch_tail = (
    '    elif mode == "truss_2d":\n'
    '        return _truss_2d(**params)\n'
    '    elif mode == "thermal_steady_1d":\n'
    '        return _thermal_steady_1d(**params)\n'
    '    elif mode == "thermal_transient_1d":\n'
    '        return _thermal_transient_1d(**params)\n'
    '    elif mode == "thermal_steady_2d":\n'
    '        return _thermal_steady_2d(**params)\n'
    '    elif mode == "stress_plane":\n'
    '        return _stress_plane(**params)\n'
    '    else:\n'
    '        raise ValueError(\n'
    '            f"modo desconocido: {mode}. Use bar_1d | beam_bending | truss_2d | "\n'
    '            "thermal_steady_1d | thermal_transient_1d | thermal_steady_2d | stress_plane"\n'
    '        )'
)
assert fet_src.count(old_dispatch_tail) == 1, "no se encontro el final del dispatcher de forma unica"
fet_src = fet_src.replace(old_dispatch_tail, new_dispatch_tail, 1)

FET.write_text(fet_src)
print("finite_element_tool.py actualizado con 4 modos nuevos.")

# ------------------------------------------------------------------
# 2. Parchear server.py: wirear composite_homogenization
# ------------------------------------------------------------------
server_src = SERVER.read_text()
server_backup = SERVER.with_suffix(".py.bak2")
server_backup.write_text(server_src)
print(f"Backup guardado en {server_backup}")

import_line = "from composite_homogenization import compute_composite_homogenization\n"
if import_line not in server_src:
    # agregarlo al final del bloque de imports existente (despues del ultimo import de tool)
    last_import_marker = "from reaction_diffusion_tool_real import compute_reaction_diffusion as compute_reaction_diffusion_real"
    if last_import_marker in server_src:
        server_src = server_src.replace(
            last_import_marker,
            last_import_marker + "\n" + import_line.rstrip(),
            1
        )
        print("Import de composite_homogenization agregado.")
    else:
        print("AVISO: no se encontro el marcador de import esperado; agregando al final del archivo")
        server_src = server_src.rstrip() + "\n" + import_line

tool_function = '''

@mcp.tool()
def composite_homogenization_tool(mode: str, params: dict = None) -> dict:
    """Propiedades efectivas de un material compuesto de 2 fases via reglas de mezcla Voigt (cota superior, iso-deformacion) y Reuss (cota inferior, iso-esfuerzo), derivadas simbolicamente con sympy. mode='elastic_modulus' o 'thermal_conductivity'. params: f1 (fraccion de volumen de fase 1), P1, P2 (propiedad de cada fase)."""
    return compute_composite_homogenization(mode, **(params or {}))
'''
if "def composite_homogenization_tool" not in server_src:
    server_src = server_src.rstrip() + "\n" + tool_function
    print("Funcion composite_homogenization_tool agregada.")
else:
    print("AVISO: composite_homogenization_tool ya existia, no se toco.")

SERVER.write_text(server_src)
print("server.py actualizado.")
print()
print("Revisa los diffs con: git diff finite_element_tool.py server.py")
print("Si algo salio mal, restaura con:")
print("  cp finite_element_tool.py.bak finite_element_tool.py")
print("  cp server.py.bak2 server.py")
