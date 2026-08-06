"""
plot_tool.py

Módulo para octave-mcp: genera visualizaciones (PNG en base64 + guardado en
disco) a partir de resultados guardados en el workspace (workspace_tool).
Diseñado para NO recalcular nada: solo lee arrays ya persistidos por otros
tools (ej: la trayectoria de un atractor guardada por compute_lyapunov_exponent
cuando se le pasa run_id) y los grafica con matplotlib (backend Agg, headless).

INTEGRACIÓN EN server.py (mismo patrón FastMCP que el resto):

    from plot_tool import plot_run, PLOT_RUN_SCHEMA

    @mcp.tool()
    def plot_workspace_run(run_id: str, plot_type: str = "auto",
                            title: str = None) -> dict:
        return plot_run(run_id, plot_type, title)

FLUJO TÍPICO:
    1. compute_lyapunov(system="chen_lee", run_id="mi_atractor")
       -> guarda trayectoria completa en el workspace
    2. plot_workspace_run(run_id="mi_atractor")
       -> lee la trayectoria, infiere que es un atractor 3D (por meta["tool"]),
          grafica con mplot3d, devuelve PNG base64 + path en disco.

TIPOS DE PLOT SOPORTADOS (plot_type):
    "auto"          -> infiere segun meta["tool"] del run guardado.
    "attractor_3d"  -> trayectoria de 3 columnas, proyeccion 3D (mplot3d).
    "attractor_2d"  -> trayectoria proyectada en plano XY.
    "line"          -> serie temporal generica (cualquier array 1D o 2D).
    "scatter"       -> nube de puntos 2D generica.
    "heatmap"       -> matriz 2D como heatmap (para settlement_clusters,
                        matrices de distancia, etc. -- pendiente de datos
                        reales hasta que esos tools tengan su propio run_id).

EXTENDER A OTROS TOOLS: cuando persistent_homology_tool.py y
settlement_clusters_tool.py reciban su propio parametro run_id (mismo patron
aplicado a lyapunov_tool.py), solo hace falta agregar una entrada al dict
_AUTO_PLOT_BY_TOOL de abajo mapeando el nombre del tool de origen (meta["tool"])
al plot_type correspondiente ("persistence_diagram", "heatmap", etc.), y si
ese plot_type es nuevo, una funcion _plot_<tipo> nueva siguiendo el mismo
patron que las existentes.
"""

import base64
import io
import os
import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from workspace_tool import load_run, WORKSPACE_DIR

PLOTS_DIR = WORKSPACE_DIR / "plots"

# Mapea meta["tool"] del run guardado -> plot_type por defecto cuando plot_type="auto"
_AUTO_PLOT_BY_TOOL = {
    "compute_lyapunov_exponent": "attractor_3d",
}


def _ensure_plots_dir():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def _fig_to_result(fig, run_id: str, plot_type: str) -> dict:
    """Serializa una figura matplotlib a PNG base64 + la guarda en disco."""
    _ensure_plots_dir()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    png_bytes = buf.read()
    b64 = base64.b64encode(png_bytes).decode("ascii")

    out_path = PLOTS_DIR / f"{run_id}_{plot_type}.png"
    out_path.write_bytes(png_bytes)

    plt.close(fig)

    return {
        "run_id": run_id,
        "plot_type": plot_type,
        "image_base64": b64,
        "image_path": str(out_path),
        "mime_type": "image/png",
    }


def _plot_attractor_3d(traj: np.ndarray, run_id: str, title: str | None, meta: dict) -> dict:
    if traj.ndim != 2 or traj.shape[1] < 3:
        return {"error": f"attractor_3d requiere trayectoria con >=3 columnas, shape={traj.shape}"}

    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], linewidth=0.6, color="#2b6cb0")
    ax.scatter([traj[0, 0]], [traj[0, 1]], [traj[0, 2]], color="#38a169", s=30, label="inicio")
    ax.scatter([traj[-1, 0]], [traj[-1, 1]], [traj[-1, 2]], color="#e53e3e", s=30, label="fin")

    system = meta.get("system", "")
    lambda1 = meta.get("lambda1")
    default_title = f"Atractor {system}" + (f" (λ1={lambda1:.4f})" if lambda1 is not None else "")
    ax.set_title(title or default_title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.legend(loc="upper right", fontsize=8)

    return _fig_to_result(fig, run_id, "attractor_3d")


def _plot_attractor_2d(traj: np.ndarray, run_id: str, title: str | None, meta: dict) -> dict:
    if traj.ndim != 2 or traj.shape[1] < 2:
        return {"error": f"attractor_2d requiere trayectoria con >=2 columnas, shape={traj.shape}"}

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(traj[:, 0], traj[:, 1], linewidth=0.6, color="#2b6cb0")
    ax.scatter([traj[0, 0]], [traj[0, 1]], color="#38a169", s=30, label="inicio", zorder=5)
    ax.scatter([traj[-1, 0]], [traj[-1, 1]], color="#e53e3e", s=30, label="fin", zorder=5)

    system = meta.get("system", "")
    ax.set_title(title or f"Atractor {system} (proyeccion XY)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_aspect("equal", adjustable="datalim")

    return _fig_to_result(fig, run_id, "attractor_2d")


def _plot_line(arr: np.ndarray, run_id: str, title: str | None, meta: dict, array_name: str) -> dict:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if arr.ndim == 1:
        ax.plot(arr, linewidth=0.8, color="#2b6cb0")
    else:
        for col in range(arr.shape[1]):
            ax.plot(arr[:, col], linewidth=0.8, label=f"col {col}")
        if arr.shape[1] <= 10:
            ax.legend(fontsize=7)
    ax.set_title(title or f"{array_name} ({meta.get('tool', 'run')})")
    ax.set_xlabel("paso")
    ax.grid(alpha=0.3)

    return _fig_to_result(fig, run_id, "line")


def _plot_scatter(arr: np.ndarray, run_id: str, title: str | None, meta: dict, array_name: str) -> dict:
    if arr.ndim != 2 or arr.shape[1] < 2:
        return {"error": f"scatter requiere array 2D con >=2 columnas, shape={arr.shape}"}

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(arr[:, 0], arr[:, 1], s=8, alpha=0.6, color="#2b6cb0")
    ax.set_title(title or f"{array_name} ({meta.get('tool', 'run')})")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(alpha=0.3)

    return _fig_to_result(fig, run_id, "scatter")


def _plot_heatmap(arr: np.ndarray, run_id: str, title: str | None, meta: dict, array_name: str) -> dict:
    if arr.ndim != 2:
        return {"error": f"heatmap requiere array 2D, shape={arr.shape}"}

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(arr, aspect="auto", cmap="viridis")
    fig.colorbar(im, ax=ax)
    ax.set_title(title or f"{array_name} ({meta.get('tool', 'run')})")

    return _fig_to_result(fig, run_id, "heatmap")


def plot_run(
    run_id: str,
    plot_type: str = "auto",
    title: str | None = None,
    array_name: str | None = None,
) -> dict:
    """
    Genera un grafico a partir de un run guardado en el workspace.

    Args:
        run_id: id del run guardado previamente (ej: por compute_lyapunov con run_id).
        plot_type: "auto" (infiere segun el tool de origen), "attractor_3d",
            "attractor_2d", "line", "scatter", "heatmap".
        title: titulo custom del grafico (si se omite, se genera uno automatico).
        array_name: nombre del array dentro del run a graficar. Si se omite,
            se usa el primero disponible (o "trayectoria" si existe, por
            compatibilidad con compute_lyapunov_exponent).

    Returns:
        dict con run_id, plot_type, image_base64 (PNG), image_path (respaldo
        en disco), mime_type. O {"error": ...} si algo falla.
    """
    loaded = load_run(run_id)
    if "error" in loaded:
        return loaded

    data = loaded["data"]
    meta = loaded.get("meta", {})

    if not data:
        return {"error": f"run_id '{run_id}' no tiene arrays guardados."}

    if array_name is None:
        array_name = "trayectoria" if "trayectoria" in data else next(iter(data))
    if array_name not in data:
        return {"error": f"array '{array_name}' no existe en run_id '{run_id}'. Disponibles: {list(data)}"}

    arr = np.asarray(data[array_name])

    if plot_type == "auto":
        plot_type = _AUTO_PLOT_BY_TOOL.get(meta.get("tool"), "line" if arr.ndim == 1 else "scatter")

    if plot_type == "attractor_3d":
        return _plot_attractor_3d(arr, run_id, title, meta)
    elif plot_type == "attractor_2d":
        return _plot_attractor_2d(arr, run_id, title, meta)
    elif plot_type == "line":
        return _plot_line(arr, run_id, title, meta, array_name)
    elif plot_type == "scatter":
        return _plot_scatter(arr, run_id, title, meta, array_name)
    elif plot_type == "heatmap":
        return _plot_heatmap(arr, run_id, title, meta, array_name)
    else:
        return {"error": f"plot_type '{plot_type}' no reconocido. Opciones: auto, attractor_3d, attractor_2d, line, scatter, heatmap."}


# --- Schema para registro manual (patron types.Tool / allowlist) ---
PLOT_RUN_SCHEMA = {
    "name": "plot_workspace_run",
    "description": (
        "Genera una visualizacion (PNG) a partir de un run guardado en el "
        "workspace (ej: la trayectoria de un atractor guardada por "
        "compute_lyapunov con run_id). No recalcula nada, solo lee y grafica."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "run_id": {"type": "string"},
            "plot_type": {
                "type": "string",
                "enum": ["auto", "attractor_3d", "attractor_2d", "line", "scatter", "heatmap"],
                "default": "auto",
            },
            "title": {"type": "string"},
            "array_name": {"type": "string", "description": "Nombre del array a graficar dentro del run (opcional)."},
        },
        "required": ["run_id"],
    },
}


if __name__ == "__main__":
    # Prueba rapida standalone: requiere que exista un run con trayectoria.
    from lyapunov_tool import compute_lyapunov_exponent
    r = compute_lyapunov_exponent(system="chen_lee", n_steps=8000, run_id="_plot_selftest")
    print("lyapunov:", r.get("lambda1"), r.get("trajectory_saved"))
    p = plot_run("_plot_selftest")
    print("plot_type:", p.get("plot_type"))
    print("image_path:", p.get("image_path"))
    print("base64 len:", len(p.get("image_base64", "")))
    from workspace_tool import delete_run
    delete_run("_plot_selftest")
