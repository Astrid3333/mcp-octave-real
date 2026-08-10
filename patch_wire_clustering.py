"""
patch_wire_clustering.py
Wirea clustering_tool.py en server.py: agrega el import y la funcion @mcp.tool().
Correr desde ~/mcp-octave-real (mismo directorio que server.py y clustering_tool.py).
"""
from pathlib import Path
import re
import shutil

SERVER = Path("server.py")
CLUSTERING = Path("clustering_tool.py")

assert SERVER.exists(), "Falta server.py en el directorio actual"
assert CLUSTERING.exists(), "Falta clustering_tool.py en el directorio actual"

src = SERVER.read_text()

if "clustering_tool" in src:
    print("clustering_tool ya parece estar wireado en server.py (se encontro la cadena "
          "'clustering_tool'). No se hicieron cambios, revisa manualmente si esto es un "
          "falso positivo antes de re-correr.")
    raise SystemExit(0)

# --- backup ---
backup = SERVER.with_suffix(SERVER.suffix + ".bak_clustering")
shutil.copy(SERVER, backup)
print(f"Backup guardado en {backup}")

# --- 1) agregar el import, despues del ultimo import de tool "from X import compute_Y" ---
import_line = "from clustering_tool import compute_clustering\n"

anchor_glm = "from glm_tool import compute_glm\n"
if anchor_glm in src:
    src = src.replace(anchor_glm, anchor_glm + import_line, 1)
    print("Import de clustering_tool agregado (despues de 'glm_tool').")
else:
    # fallback: insertar despues del ultimo "from ..._tool import compute_..." que aparezca
    matches = list(re.finditer(r"^from \S+ import compute_\S+\n", src, flags=re.MULTILINE))
    if not matches:
        raise RuntimeError(
            "No se encontro ni el anchor 'glm_tool' ni ningun import 'from ... import "
            "compute_...' para insertar despues. Wirealo a mano."
        )
    last = matches[-1]
    insert_at = last.end()
    src = src[:insert_at] + import_line + src[insert_at:]
    print(f"Anchor 'glm_tool' no encontrado — import de clustering_tool agregado despues "
          f"de '{last.group().strip()}' (fallback).")

# --- 2) agregar la funcion @mcp.tool() al final del archivo ---
tool_function = '''@mcp.tool()
def clustering_tool(mode: str, params: dict = None) -> dict:
    """Fase C de estadistica: clustering y reduccion de dimensionalidad. mode='kmeans': K-means con inicializacion k-means++, devuelve labels, centroides, inertia, silhouette_score y davies_bouldin_score (params: X, k, n_init, max_iter, random_state). mode='hierarchical': clustering jerarquico via scipy (linkage single/complete/average), devuelve matriz de linkage y orden de dendrograma para math_visualization_tool; si se pasa n_clusters tambien devuelve la asignacion de clusters por corte (params: X, linkage, n_clusters). mode='pca_extended': extiende el PCA de linear_algebra_tool con biplot completo — scores, loadings y contribucion porcentual de cada variable por componente (params: X, n_components, standardize, feature_names). Validado cruzado contra sklearn (KMeans, AgglomerativeClustering via adjusted_rand_score, PCA)."""
    return compute_clustering(mode, **(params or {}))
'''

src = src.rstrip("\n") + "\n\n\n" + tool_function
SERVER.write_text(src)
print("Funcion clustering_tool agregada.")
print("server.py actualizado.\n")
print(f"Revisa el diff con: git diff server.py")
print(f"Si algo salio mal, restaura con: cp {backup} server.py")
