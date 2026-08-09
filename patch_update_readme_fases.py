#!/usr/bin/env python3
"""
Actualiza README.md:
  1. Corrige el contador de tools al valor real (cuenta las ocurrencias de
     "@mcp.tool()" en server.py, no un numero hardcodeado).
  2. Inserta una seccion nueva documentando las 3 fases del roadmap que
     todavia no estaban en el README: extension de finite_element_tool con
     thermal/stress analysis, composite_homogenization, statistical_physics_tool
     y cfd_tool.

Uso: correr desde dentro de ~/mcp-octave-real
    python3 patch_update_readme_fases.py
"""
import re
from pathlib import Path

README = Path("README.md")
SERVER = Path("server.py")
assert README.exists(), "Correr este script dentro de ~/mcp-octave-real"
assert SERVER.exists(), "No se encontro server.py en el directorio actual"

readme = README.read_text()
server = SERVER.read_text()

# Backup
backup = README.with_suffix(".md.bak2")
backup.write_text(readme)
print(f"Backup guardado en {backup}")

# --- 1. Contador real de tools ---
n_tools = len(re.findall(r"@mcp\.tool\(\)", server))
new_readme, n_sub = re.subn(
    r"(\d+)( tools\.)",
    lambda m: f"{n_tools}{m.group(2)}",
    readme,
    count=1,
)
if n_sub:
    print(f"Conteo de tools actualizado -> {n_tools}")
else:
    print("ADVERTENCIA: no se encontro el patron 'N tools.' para actualizar el contador; revisar a mano.")

FASES_SECTION = """

### Fases 1-3: materiales, física estadística y CFD (roadmap completo)
- **`finite_element_tool`** (extendido) — se sumaron 4 modos nuevos de
  análisis térmico y de esfuerzos, además de los 3 modos estructurales
  originales: `thermal_steady_1d`, `thermal_transient_1d` (conducción de
  calor 1D/2D, validado contra serie de Fourier para el caso transitorio),
  `thermal_steady_2d`, y `stress_analysis` (plane stress/plane strain,
  validado contra el caso de Kirsch — placa con agujero, concentración de
  esfuerzos).
- **`composite_homogenization_tool`** — propiedades efectivas de un material
  compuesto de 2 fases vía reglas de mezcla Voigt (cota superior,
  iso-deformación) y Reuss (cota inferior, iso-esfuerzo), derivadas
  simbólicamente con sympy vía `ocas_symbolic_tool`. Modos:
  `elastic_modulus`, `thermal_conductivity`.
- **`statistical_physics_tool`** — física estadística y sistemas complejos:
  modelo de Ising 2D vía Monte Carlo Metropolis (magnetización, energía,
  calor específico, estimación de temperatura crítica vs. valor exacto de
  Onsager) y modelo de Potts de q estados para crecimiento de
  grano/microestructura (evolución de número de granos y área promedio en
  el tiempo). Modos: `ising_2d`, `potts_grain_growth`.
- **`cfd_tool`** — dinámica de fluidos computacional 2D laminar (sin
  modelos de turbulencia): `poiseuille_flow` (flujo de Stokes entre placas
  paralelas, validado contra la solución analítica exacta de
  Hagen-Poiseuille) y `lid_driven_cavity` (Navier-Stokes 2D vía
  formulación vorticidad-función de corriente, cavidad con tapa móvil,
  validado contra el benchmark clásico de Ghia, Ghia & Shin 1982, Re=100,
  error máximo 0.0056 en la línea central).
"""

anchor_re = re.compile(r"### Ingeniería, simulación y utilidades.*?(?=\n### |\n## |\Z)", re.DOTALL)
match = anchor_re.search(new_readme)
if match:
    insert_at = match.end()
    new_readme = new_readme[:insert_at] + FASES_SECTION + new_readme[insert_at:]
    print("Seccion nueva insertada despues de 'Ingeniería, simulación y utilidades'")
else:
    new_readme = new_readme.rstrip("\n") + "\n" + FASES_SECTION
    print("No se encontro la seccion ancla; seccion nueva agregada al final del archivo")

README.write_text(new_readme)
print("README.md actualizado.")
print("Revisa el diff con: git diff README.md")
print("Si algo salio mal, restaura con: cp README.md.bak2 README.md")
