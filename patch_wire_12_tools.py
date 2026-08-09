#!/usr/bin/env python3
"""
Wirea los 12 tools que ya estan copiados como archivo en mcp-octave-real
pero que todavia no estan importados ni registrados como @mcp.tool en server.py.

Uso: correr desde dentro de ~/mcp-octave-real
    python3 patch_wire_12_tools.py
"""
import re
from pathlib import Path

SERVER = Path("server.py")
assert SERVER.exists(), "Correr este script dentro de ~/mcp-octave-real"

src = SERVER.read_text()

# Backup
backup = SERVER.with_suffix(".py.bak")
backup.write_text(src)
print(f"Backup guardado en {backup}")

IMPORTS_BLOCK = '''from budgeting_tool import compute_budgeting
from construction_scheduling_tool import compute_construction_scheduling
from earthworks_tool import compute_earthworks
from finite_element_tool import compute_finite_element
from math_humanizer_tool import compute_math_humanizer
from multibody_dynamics_tool import compute_multibody_dynamics
from ocas_symbolic_tool import compute_ocas_symbolic
from particle_simulation_tool import compute_particle_simulation
from quantity_takeoff_tool import compute_quantity_takeoff
from structural_analysis_tool import compute_structural_analysis
from lyapunov_tool_v2 import compute_lyapunov_exponent as compute_lyapunov_v2
from reaction_diffusion_tool_real import compute_reaction_diffusion as compute_reaction_diffusion_real
'''

TOOLS_BLOCK = '''
@mcp.tool()
def budgeting_tool(mode: str, params: dict = None) -> dict:
    """Presupuestos de construccion: costo directo, analisis de precio unitario (APU), aplicacion de gastos generales/utilidad/contingencia/impuesto, escalamiento por inflacion, resumen por capitulos."""
    return compute_budgeting(mode, **(params or {}))

@mcp.tool()
def construction_scheduling_tool(mode: str, params: dict = None) -> dict:
    """Planificacion de obra: ruta critica (CPM), carga diaria de recursos, compresion de cronograma (crashing) por menor pendiente de costo."""
    return compute_construction_scheduling(mode, **(params or {}))

@mcp.tool()
def earthworks_tool(operation: str, params: dict = None) -> dict:
    """Movimiento de tierras: volumen entre secciones transversales, corte/relleno sobre grilla, esponjamiento/contraccion, diagrama de masas."""
    return compute_earthworks(operation, **(params or {}))

@mcp.tool()
def finite_element_tool(mode: str, params: dict = None) -> dict:
    """Metodo de elementos finitos: barra axial 1D, viga en voladizo Euler-Bernoulli, cercha plana 2D."""
    return compute_finite_element(mode, params or {})

@mcp.tool()
def math_humanizer_tool(mode: str, params: dict = None) -> dict:
    """Explicaciones divulgativas de conceptos matematicos: analogia cotidiana + conexion filosofica + nota tecnica."""
    return compute_math_humanizer(mode, **(params or {}))

@mcp.tool()
def multibody_dynamics_tool(mode: str, params: dict = None) -> dict:
    """Dinamica de cuerpos rigidos: pendulo fisico compuesto, rotacion libre via ecuaciones de Euler, manipulador/pendulo doble planar."""
    return compute_multibody_dynamics(mode, params or {})

@mcp.tool()
def ocas_symbolic_tool(mode: str = "symbolic", params: dict = None) -> dict:
    """Algebra simbolica y teoria de numeros via oCAS (motor Rust): simplify/differentiate/integrate/substitute, primalidad, factorizacion, totient, ecuaciones diofanticas, CRT."""
    return compute_ocas_symbolic(mode=mode, **(params or {}))

@mcp.tool()
def particle_simulation_tool(mode: str, params: dict = None) -> dict:
    """Simulacion de particulas: orbita de Kepler (dos cuerpos), colisiones elasticas en cadena 1D, caminata aleatoria y difusion."""
    return compute_particle_simulation(mode, params or {})

@mcp.tool()
def quantity_takeoff_tool(operation: str, params: dict = None) -> dict:
    """Cubicaciones de construccion: volumen de hormigon, area de encofrado, peso de acero de refuerzo, volumen de excavacion, conteo de albanileria, resumen BOQ."""
    return compute_quantity_takeoff(operation, **(params or {}))

@mcp.tool()
def structural_analysis_tool(mode: str, params: dict = None) -> dict:
    """Analisis estructural preliminar: vigas (reacciones/corte/momento/deflexion), cerchas 2D isostaticas, propiedades de seccion, chequeo de esfuerzo admisible."""
    return compute_structural_analysis(mode, **(params or {}))

@mcp.tool()
def lyapunov_v2_tool(params: dict = None) -> dict:
    """Exponente de Lyapunov maximo (version 2, con soporte de guardado de trayectoria en workspace via run_id): chen_lee, burke_shaw, lorenz, rossler o sistema custom."""
    return compute_lyapunov_v2(**(params or {}))

@mcp.tool()
def reaction_diffusion_real_tool(params: dict = None) -> dict:
    """Inestabilidad de Turing (reaccion-difusion linealizada): evalua las 4 condiciones analiticas clasicas para un sistema de 2 especies."""
    return compute_reaction_diffusion_real(**(params or {}))
'''

import_lines = list(re.finditer(r'^from \S+ import .+$', src, flags=re.MULTILINE))
if not import_lines:
    raise SystemExit("No se encontraron imports 'from ..._tool import ...' en server.py")
last_import_end = import_lines[-1].end()

new_src = src[:last_import_end] + "\n" + IMPORTS_BLOCK + src[last_import_end:]
new_src = new_src.rstrip("\n") + "\n" + TOOLS_BLOCK

if "def budgeting_tool(" in src:
    print("ADVERTENCIA: parece que el patch ya fue aplicado antes (budgeting_tool ya existe). Abortando sin escribir.")
else:
    SERVER.write_text(new_src)
    print("server.py actualizado con los 12 tools nuevos.")
    print("Revisa el diff con: git diff server.py")
    print("Si algo salio mal, restaura con: cp server.py.bak server.py")
