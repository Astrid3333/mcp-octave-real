#!/usr/bin/env python3
"""
patch_update_readme_fases_abcd.py
Actualiza README.md en mcp-octave-real: corrige el contador de tools a 96 y
agrega una seccion nueva documentando las Fases A-D (statistics_extended_tool,
glm_tool, clustering_tool, y el modo mcmc agregado a stochastic_processes).

No asume el contenido exacto de la seccion "Fases 1-3" ya existente (por eso
no fallo como el patch anterior de la docstring): ubica esa seccion por su
encabezado y busca el SIGUIENTE encabezado de nivel ## o ### para insertar
justo antes, sin importar que texto haya en el medio.

Correr desde ~/mcp-octave-real:
    python3 patch_update_readme_fases_abcd.py
"""
import re
from pathlib import Path

README = Path("README.md")
assert README.exists(), "Falta README.md en el directorio actual"

src = README.read_text()

# --- 1. backup ---
backup = README.with_suffix(".md.bak3")
backup.write_text(src)
print(f"Backup guardado en {backup}")

# --- 2. actualizar contador de tools (regex, no asume el numero viejo) ---
count_pattern = re.compile(r'(\[FastMCP\]\(https://github\.com/jlowin/fastmcp\)\.\s*)\d+( tools\.)')
new_src, n_count = count_pattern.subn(r'\g<1>96\g<2>', src)
if n_count == 0:
    print("AVISO: no se encontro la linea del contador de tools ('... FastMCP ... N tools.'); no se toco el contador.")
else:
    print(f"Conteo de tools actualizado -> 96 ({n_count} ocurrencia(s))")
src = new_src

# --- 3. evitar doble insercion ---
if "Fase A-D" in src or "Fases A-D" in src:
    print("La seccion de Fases A-D ya existe, no se inserta de nuevo.")
    README.write_text(src)
else:
    NEW_SECTION = '''
### Fases A-D: estadística avanzada, ML y muestreo (roadmap completo)
- **`statistics_extended_tool`** — EDA descriptiva (media, mediana, moda,
  cuartiles, asimetría, curtosis, outliers IQR/z-score), tablas de
  contingencia con chi-cuadrado, tests de 2 muestras paramétricos y no
  paramétricos (ttest_ind, ttest_paired, mannwhitney, wilcoxon, ks_2samp),
  ANOVA de 1 vía con post-hoc Bonferroni, tests de normalidad (shapiro,
  jarque_bera), y remuestreo (bootstrap percentil/BCa, test de
  permutaciones). Validado cruzado contra scipy.stats.
- **`glm_tool`** — modelos lineales generalizados y regresión regularizada:
  regresión logística binaria vía IRLS, regresión de Poisson (link log) vía
  IRLS, y Ridge/Lasso con selección de lambda vía validación cruzada
  k-fold. Validado cruzado contra sklearn.
- **`clustering_tool`** — clustering y reducción de dimensionalidad: K-means
  con inicialización k-means++ (inertia, silhouette, Davies-Bouldin),
  clustering jerárquico vía scipy (linkage single/complete/average), y PCA
  extendido (varianza explicada). Validado cruzado contra sklearn.
- **`stochastic_processes`** (extendido) — se sumó el modo `mcmc`:
  Metropolis-Hastings genérico con propuesta random-walk gaussiana sobre un
  target gaussiano o una densidad custom vía expresión sympy, devuelve
  media/covarianza posterior, acceptance rate y effective sample size
  (vía tiempo de autocorrelación integrado).

'''

    anchor = "### Fases 1-3"
    idx = src.find(anchor)
    if idx == -1:
        print("AVISO: no se encontro la seccion '### Fases 1-3' en README.md; no se inserto la seccion nueva.")
        print("Revisa README.md manualmente y agrega la seccion a mano si hace falta.")
        README.write_text(src)
    else:
        # buscar el siguiente encabezado de nivel ## o ### despues del anchor
        search_from = idx + len(anchor)
        next_heading = re.search(r'\n#{2,3} ', src[search_from:])
        if next_heading is None:
            insert_at = len(src)
            print("AVISO: no se encontro un encabezado posterior a 'Fases 1-3'; la seccion nueva se agrega al final del archivo.")
        else:
            insert_at = search_from + next_heading.start() + 1  # +1 para insertar despues del \n

        src = src[:insert_at] + NEW_SECTION + src[insert_at:]
        README.write_text(src)
        print("Seccion 'Fases A-D' insertada despues de la seccion 'Fases 1-3'.")

print("\nRevisa el diff con: git diff README.md")
print("Si algo salio mal, restaura con: cp README.md.bak3 README.md")
