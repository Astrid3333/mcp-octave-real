#!/usr/bin/env python3
import subprocess, tempfile, os, sys
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lyapunov_tool import compute_lyapunov_exponent
from stiff_ode_tool import integrate_stiff_ode
from bifurcation_tool import compute_bifurcation_diagram
from hilbert_tool import compute_hilbert_transform
from graph_tool import compute_graph_algorithms
from qm_tool import compute_qm_potential_well
from nuclear_decay_tool import compute_nuclear_decay_chain
from fractal_dimension_tool import compute_fractal_dimension
from ethnomath_tool import compute_ethnomath
from ethnomath2_tool import compute_ethnomath2
from ancient_calculators_tool import compute_ancient_calculator
from levant_tool import compute_levant
from ancestral_octave_tool import compute_ancestral_octave

mcp = FastMCP(name="octave-mcp", instructions="Servidor MCP GNU Octave.")

DEFAULT_TIMEOUT = 60

def _run_octave(code, working_dir=None, timeout=DEFAULT_TIMEOUT):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".m", delete=False, dir=working_dir) as f:
        f.write(code)
        script_path = f.name
    try:
        r = subprocess.run(["octave","--no-gui","--no-init-file",script_path],
            capture_output=True, text=True, timeout=timeout,
            cwd=working_dir or os.path.expanduser("~"))
        return {"stdout": r.stdout.strip(), "stderr": r.stderr.strip(), "returncode": r.returncode}
    except subprocess.TimeoutExpired:
        return {"stdout":"","stderr":f"Timeout tras {timeout}s","returncode":-1}
    except FileNotFoundError:
        return {"stdout":"","stderr":"octave no encontrado","returncode":-2}
    finally:
        os.unlink(script_path)

def _format_result(r):
    parts = []
    if r["stdout"]:
        parts.append(r["stdout"])
    if r["stderr"]:
        parts.append("[stderr]\n" + r["stderr"])
    if r["returncode"] != 0:
        parts.append(f"[returncode: {r['returncode']}]")
    return "\n".join(parts) if parts else "(sin salida)"

@mcp.tool()
def octave_run(code: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Ejecuta codigo Octave. timeout en segundos (default 60)."""
    r = _run_octave(code, timeout=timeout)
    return _format_result(r)

@mcp.tool()
def octave_eval_expr(expression: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Evalua una expresion Octave con disp()."""
    r = _run_octave("disp(" + expression + ")", timeout=timeout)
    if r["returncode"] != 0:
        return _format_result(r)
    return r["stdout"] if r["stdout"] else "(sin salida)"

@mcp.tool()
def octave_run_script(script_path: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Ejecuta un script .m existente en disco."""
    p = Path(script_path)
    if not p.exists():
        return "Error: no existe " + script_path
    r = _run_octave(p.read_text(), working_dir=str(p.parent), timeout=timeout)
    return _format_result(r)

@mcp.tool()
def octave_version() -> str:
    """Devuelve la version de Octave instalada."""
    try:
        r = subprocess.run(["octave","--version"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Timeout consultando version de Octave"
    except FileNotFoundError:
        return "Octave no encontrado"

@mcp.tool()
def compute_lyapunov(
    system: str = "chen_lee",
    custom_equations: Optional[str] = None,
    custom_params: Optional[dict] = None,
    y0: Optional[list] = None,
    dt: Optional[float] = None,
    n_steps: int = 20000,
    d0: float = 1e-8,
) -> dict:
    """Calcula el exponente de Lyapunov maximo (lambda1) de un sistema dinamico
    (presets: chen_lee, burke_shaw, lorenz, rossler, o ecuaciones custom) para
    cuantificar caos. lambda1>0 confirma comportamiento caotico."""
    kwargs = {"system": system, "n_steps": n_steps, "d0": d0}
    if custom_equations is not None: kwargs["custom_equations"] = custom_equations
    if custom_params is not None: kwargs["custom_params"] = custom_params
    if y0 is not None: kwargs["y0"] = y0
    if dt is not None: kwargs["dt"] = dt
    return compute_lyapunov_exponent(**kwargs)

@mcp.tool()
def integrate_stiff(
    system: str = "van_der_pol",
    custom_equations: Optional[str] = None,
    custom_params: Optional[dict] = None,
    y0: Optional[list] = None,
    tspan: Optional[list] = None,
    solver: str = "ode15s",
    n_output_points: int = 50,
    rel_tol: float = 1e-6,
    abs_tol: float = 1e-8,
) -> dict:
    """Integra un sistema de ecuaciones diferenciales ordinarias, incluyendo
    sistemas rigidos/stiff, usando solvers implicitos de Octave (ode15s,
    ode23s) o lsode. Presets: van_der_pol (stiff clasico), robertson
    (cinetica quimica rigida), o custom."""
    kwargs = {
        "system": system, "solver": solver, "n_output_points": n_output_points,
        "rel_tol": rel_tol, "abs_tol": abs_tol,
    }
    if custom_equations is not None: kwargs["custom_equations"] = custom_equations
    if custom_params is not None: kwargs["custom_params"] = custom_params
    if y0 is not None: kwargs["y0"] = y0
    if tspan is not None: kwargs["tspan"] = tspan
    return integrate_stiff_ode(**kwargs)

@mcp.tool()
def compute_bifurcation(
    map_name: str = "logistic",
    custom_expr: Optional[str] = None,
    r_range: Optional[list] = None,
    x0: Optional[float] = None,
    n_r_values: int = 300,
    n_transient: int = 500,
    n_keep: int = 40,
    stability_check_rs: Optional[list] = None,
) -> dict:
    """Genera un diagrama de bifurcacion para un mapa iterativo 1D
    (x_next = f(x,r)), barriendo un rango de r y guardando los puntos del
    atractor tras un transitorio. Presets: logistic, sine, cubic, tent, o
    custom. Opcionalmente analiza estabilidad (via derivada) en valores de
    r especificos."""
    kwargs = {
        "map_name": map_name, "n_r_values": n_r_values,
        "n_transient": n_transient, "n_keep": n_keep,
    }
    if custom_expr is not None: kwargs["custom_expr"] = custom_expr
    if r_range is not None: kwargs["r_range"] = r_range
    if x0 is not None: kwargs["x0"] = x0
    if stability_check_rs is not None: kwargs["stability_check_rs"] = stability_check_rs
    return compute_bifurcation_diagram(**kwargs)

@mcp.tool()
def hilbert_transform(
    preset: str = "am_chirp",
    signal: Optional[list] = None,
    fs: float = 1000.0,
    duration: float = 1.0,
    detrend: bool = True,
    bandpass: Optional[list] = None,
    n_output_points: int = 200,
) -> dict:
    """Calcula la transformada de Hilbert de una serie temporal no
    estacionaria y extrae envolvente (amplitud instantanea), fase
    instantanea y frecuencia instantanea via la senal analitica. Incluye
    presets sinteticos (am_chirp, fm_chirp, noisy_am) para validar el
    metodo, o acepta una senal custom (ej. mediciones de campo electrico
    atmosferico) con bandpass opcional [f_low, f_high] en Hz."""
    return compute_hilbert_transform(
        preset=preset, signal=signal, fs=fs, duration=duration,
        detrend=detrend, bandpass=bandpass, n_output_points=n_output_points,
    )

@mcp.tool()
def graph_algorithms(
    preset: str = "small_weighted",
    edges: list = None,
    directed: bool = False,
    operation: str = "all",
    source=None,
) -> dict:
    """Corre algoritmos clasicos de grafos: Dijkstra, MST (Kruskal), deteccion
    de ciclos. Presets: small_weighted, disconnected, with_cycle, o custom
    via 'edges' [[u,v,peso],...]."""
    return compute_graph_algorithms(
        preset=preset, edges=edges, directed=directed,
        operation=operation, source=source,
    )

@mcp.tool()
def qm_potential_well(
    preset: str = "infinite_well",
    custom_potential: str = None,
    well_params: dict = None,
    x_range: list = None,
    n_points: int = 400,
    mass: float = 1.0,
    hbar: float = 1.0,
    n_states: int = 5,
) -> dict:
    """Resuelve la ecuacion de Schrodinger 1D independiente del tiempo por
    diferencias finitas. Presets: infinite_well, finite_well,
    harmonic_oscillator, o custom via custom_potential (expresion Octave en x)."""
    return compute_qm_potential_well(
        preset=preset, custom_potential=custom_potential, well_params=well_params,
        x_range=x_range, n_points=n_points, mass=mass, hbar=hbar, n_states=n_states,
    )


@mcp.tool()
def nuclear_decay_chain(
    preset: str = "cs137_ba137m",
    chain: list = None,
    t_max: float = None,
    n_points: int = 300,
    stable_last: bool = True,
) -> dict:
    """Resuelve una cadena de decaimiento nuclear (Bateman) via ode45.
    Presets: cs137_ba137m, sr90_y90, o custom via 'chain'. stable_last=True
    no sigue la cadena mas alla del ultimo isotopo pero NUNCA anula su
    lambda (permite alcanzar equilibrio secular)."""
    return compute_nuclear_decay_chain(preset, chain, t_max, n_points, stable_last)


@mcp.tool()
def fractal_dimension(
    preset: str = "sierpinski_triangle",
    points: list = None,
    n_points: int = 60000,
    order: int = 6,
    n_scales: int = 14,
    eps_min_frac: float = 0.001,
    eps_max_frac: float = 0.3,
    chen_lee_params: dict = None,
) -> dict:
    """Dimension fractal por box-counting. Presets: sierpinski_triangle,
    koch_curve, cantor_set (con dimension analitica de referencia),
    chen_lee_attractor (integra el sistema caotico en Octave), o custom
    via 'points'."""
    return compute_fractal_dimension(preset, points, n_points, order,
                                      n_scales, eps_min_frac, eps_max_frac,
                                      chen_lee_params)


@mcp.tool()
def ethnomath(preset: str, params: dict = None) -> dict:
    """Algoritmos matematicos historicos: maya_long_count, chinese_remainder,
    vedic_multiply, quipu_encode, greek_archimedes_pi, japanese_enri_pi."""
    return compute_ethnomath(preset, params or {})

@mcp.tool()
def ethnomath2(preset: str, params: dict = None) -> dict:
    """Segunda tanda de algoritmos matematicos historicos: egyptian_duplation,
    persian_khwarizmi, persian_alkashi_sin1, russian_peasant,
    ottoman_taqi_al_din, norse_rune_calendar, southeast_asian_metonic."""
    return compute_ethnomath2(preset, params or {})

@mcp.tool()
def ancient_calculator(preset: str, params: dict = None) -> dict:
    """Simula calculadoras historicas reales operando sus cuentas/fichas:
    suanpan, soroban, roman_hand_abacus, yupana_depasquale (hipotesis en
    disputa academica, ver advertencia en la respuesta)."""
    return compute_ancient_calculator(preset, params or {})

@mcp.tool()
def ancestral_octave(preset: str, params: dict = None, extra_octave: str = None) -> dict:
    """Corre metodos ancestrales (suanpan_add, chinese_remainder, vedic_multiply,
    archimedes_pi, quipu_encode) como funciones Octave NATIVAS via ancestral.m,
    en el mismo motor que octave_run. extra_octave permite componer con otro
    codigo Octave en la misma sesion."""
    return compute_ancestral_octave(preset, params or {}, extra_octave, _run_octave)

from filosofia_historia_mate_tool import compute_math_philosophy_history

@mcp.tool()
def math_philosophy_history(topic: str = "", params: dict = None) -> str:
    """Referencia sobre filosofia e historia de la matematica (8 topics)."""
    return compute_math_philosophy_history(topic, params)



@mcp.tool()
def levant(preset: str, params: dict = None) -> dict:
    """Matematica cananea y de Juda/Israel: hebrew_molad (conjuncion lunar
    media, ciclo metonico de 19 anios), hebrew_gematria (valor numerico de
    palabras hebreas y su inverso), canaanite_phoenician_numeral (sistema
    aditivo 1/10/20/100)."""
    return compute_levant(preset, params or {})
if __name__ == "__main__":
    mcp.run()
