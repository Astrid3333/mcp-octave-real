#!/usr/bin/env python3
"""
Actualiza README.md: corrige el conteo de tools (29 -> 88) y agrega
una seccion nueva documentando los 12 tools wireados hoy.
Uso: correr desde dentro de ~/mcp-octave-real
    python3 patch_update_readme.py
"""
from pathlib import Path

README = Path("README.md")
assert README.exists(), "Correr este script dentro de ~/mcp-octave-real"

src = README.read_text()
backup = README.with_suffix(".md.bak")
backup.write_text(src)
print(f"Backup guardado en {backup}")

# 1. Corregir el conteo de tools
old_count = "Construido con [FastMCP](https://github.com/jlowin/fastmcp). 29 tools."
new_count = "Construido con [FastMCP](https://github.com/jlowin/fastmcp). 88 tools."
if old_count in src:
    src = src.replace(old_count, new_count)
    print("Conteo de tools actualizado: 29 -> 88")
else:
    print("AVISO: no se encontro la linea del conteo de tools, revisar manualmente")

# 2. Agregar seccion nueva con los 12 tools de hoy, despues de "### Matemática musical"
new_section = '''
### Ingeniería, simulación y utilidades (agregado reciente)
- **`budgeting_tool`** — presupuestos de construcción: costo directo de
  partidas, análisis de precios unitarios.
- **`construction_scheduling_tool`** — planificación de obra vía ruta
  crítica (CPM): early/late start-finish, holguras.
- **`earthworks_tool`** — movimiento de tierras a escala de trazado y
  terreno: volumen entre secciones transversales.
- **`finite_element_tool`** — método de elementos finitos: barra axial,
  viga en voladizo Euler-Bernoulli.
- **`structural_analysis_tool`** — análisis estructural preliminar:
  reacciones, corte, momento y deflexión de vigas.
- **`quantity_takeoff_tool`** — cubicaciones de construcción: volumen de
  hormigón, área de encofrado, peso de acero.
- **`multibody_dynamics_tool`** — dinámica de cuerpos rígidos y sistemas
  multi-cuerpo (péndulo físico compuesto, entre otros).
- **`particle_simulation_tool`** — simulación de partículas: órbita de
  Kepler de dos cuerpos, colisiones.
- **`ocas_symbolic_tool`** — álgebra simbólica y teoría de números vía
  oCAS (motor Rust, más rápido que sympy para ciertos casos).
- **`math_humanizer_tool`** — convierte conceptos matemáticos complejos en
  explicaciones e historias accesibles.
- **`lyapunov_tool_v2`** — segunda versión del cálculo de exponente de
  Lyapunov máximo, con presets adicionales.
- **`reaction_diffusion_tool_real`** — inestabilidad de Turing
  (reacción-difusión linealizada): evalúa las condiciones de inestabilidad.
'''

anchor = "### Matemática musical"
idx = src.find(anchor)
if idx == -1:
    print("AVISO: no se encontro '### Matemática musical', agregando seccion al final")
    src = src.rstrip() + "\n" + new_section
else:
    # Insertar despues del bloque de Matematica musical (hasta el siguiente '###' o fin de archivo)
    next_section_idx = src.find("\n### ", idx + len(anchor))
    if next_section_idx == -1:
        # No hay mas secciones despues, insertar al final
        src = src.rstrip() + "\n" + new_section
    else:
        src = src[:next_section_idx] + "\n" + new_section + src[next_section_idx:]
    print("Seccion nueva insertada despues de 'Matemática musical'")

README.write_text(src)
print("README.md actualizado.")
print("Revisa el diff con: git diff README.md")
print("Si algo salio mal, restaura con: cp README.md.bak README.md")
