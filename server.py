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
from cross_validation_tool import compute_cross_validation
from entropy_structure_tool import compute_entropy_structure
from music_math_tool import compute_music_math
from linear_algebra_tool import compute_linear_algebra
from persistent_homology_tool import compute_persistent_homology
from statistics_tool import compute_statistics
from number_theory_tool import compute_number_theory
from symbolic_tool import compute_symbolic
from optimization_tool import compute_optimization
from pde_tool import compute_pde
from braid_group_tool import compute_braid_group
from workspace_tool import save_run, load_run, list_runs, describe_run, delete_run
from plot_tool import plot_run
from numeral_systems_embedding_tool import compute_numeral_systems_embedding
from population_dynamics_tool import compute_population_dynamics
from reaction_diffusion_tool import compute_reaction_diffusion
from enzyme_kinetics_tool import compute_enzyme_kinetics
from tritbraid_tool import compute_tritbraid
from historian_tool import compute_historian
from antibiotic_diffusion import compute_antibiotic_diffusion
from plague_sir_tool import compute_plague_sir
from settlement_clusters_tool import compute_settlement_clusters
from archaeological_simulation_tool import compute_archaeological_simulation
from historical_extractor_tool import compute_historical_extractor
from ethnomath_tool import compute_ethnomath
from ethnomath2_tool import compute_ethnomath2
from ancient_calculators_tool import compute_ancient_calculator
from levant_tool import compute_levant
from originarios_tool import compute_originarios
from ancestral_octave_tool import compute_ancestral_octave
from auto_differentiation_tool import compute_gradient_hessian as _compute_gradient_hessian, compute_jacobian as _compute_jacobian
from math_error_analyzer_tool import compute_math_error_analysis
from math_benchmark_tool import compute_math_benchmark
from math_interpolation_tool import compute_math_interpolation
from math_pipeline_builder_tool import run_math_pipeline as _run_math_pipeline
from math_interpreter_tool import interpret_math_query as _interpret_math_query
from math_visualization_tool import compute_math_visualization
from math_explainer_tool import interpret_and_explain as _interpret_and_explain
from machine_learning_math_tool import compute_machine_learning_math
from financial_math_tool import compute_financial_math
from game_theory_tool import compute_game_theory
from tensor_calculus_tool import compute_tensor_calculus
from network_science_tool import compute_network_science
from population_genetics_tool import compute_population_genetics
from wavelet_tool import compute_wavelet
from percolation_theory_tool import compute_percolation_theory
from chemometrics_tool import compute_chemometrics
from econometrics_tool import compute_econometrics
from stochastic_processes_tool import compute_stochastic_processes
from information_theory_tool import compute_information_theory
from control_theory_tool import compute_control_theory
from optimal_control_tool import compute_optimal_control
from spatial_statistics_tool import compute_spatial_statistics
from text_analysis_math_tool import compute_text_analysis_math
from archaeoastronomy_tool import compute_archaeoastronomy
from quantum_information_tool import compute_quantum_information
from paleography_tool import compute_paleography
from abstract_algebra_tool import compute_abstract_algebra

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
    run_id: Optional[str] = None,
    save_trajectory_every: int = 10,
) -> dict:
    """Calcula el exponente de Lyapunov maximo (lambda1) de un sistema dinamico
    (presets: chen_lee, burke_shaw, lorenz, rossler, o ecuaciones custom) para
    cuantificar caos. lambda1>0 confirma comportamiento caotico. Si se indica
    run_id, guarda la trayectoria completa en el workspace (util para graficar
    el atractor despues con plot_tool)."""
    kwargs = {"system": system, "n_steps": n_steps, "d0": d0, "save_trajectory_every": save_trajectory_every}
    if custom_equations is not None: kwargs["custom_equations"] = custom_equations
    if custom_params is not None: kwargs["custom_params"] = custom_params
    if y0 is not None: kwargs["y0"] = y0
    if dt is not None: kwargs["dt"] = dt
    if run_id is not None: kwargs["run_id"] = run_id
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
from budgeting_tool import compute_budgeting
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
from composite_homogenization import compute_composite_homogenization


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

@mcp.tool()
def originarios(preset: str, params: dict = None) -> dict:
    """Numeracion de pueblos originarios: mapuche_numeral (rakin, decimal
    aditivo-multiplicativo) y aymara_numeral (decimal con sufijo -ni, mas
    nota sobre vestigio quinario)."""
    return compute_originarios(preset, params or {})

@mcp.tool()
def cross_validation(system: str = "chen_lee", params: dict = None, t_max: float = 2000,
                      n_steps: int = 200000, transient_frac: float = 0.1, tolerance: float = 0.15) -> dict:
    """Valida un resultado de dimension fractal corriendo el mismo sistema
    dinamico con dos motores numericos independientes (Octave ode45 y scipy
    RK45). Devuelve ambas dimensiones, la diferencia relativa, y un flag
    cross_validated. Sistemas disponibles: chen_lee."""
    return compute_cross_validation(system, params or {}, t_max, n_steps, transient_frac, tolerance)

@mcp.tool()
def entropy_structure(preset: str = "random_iid", sequence: list = None,
                       alphabet_size: int = 5, n_symbols: int = 5000, seed: int = 1) -> dict:
    """Calcula entropia de orden 0 y entropia condicional de orden 1 sobre una
    secuencia de simbolos, para evaluar evidencia de estructura combinatoria
    (compatible con codificacion tipo-lenguaje) vs. conteo simple/tally marks.
    Presets sinteticos validados (random_iid, markov_structured) o custom via
    'sequence' con datos reales (khipu, yupana, corpus sin descifrar, etc)."""
    return compute_entropy_structure(preset, sequence, alphabet_size, n_symbols, seed)

@mcp.tool()
def music_math(preset: str = "pythagorean_comma", f0: float = 220.0, n_harmonics: int = 8,
                n_power: int = 2, signal: list = None, fs: float = 44100) -> dict:
    """Calculos de matematica musical: pythagorean_comma, temperament_comparison,
    harmonic_series, ternary_scale (division de la octava en 3^n pasos, conexion
    con TritOS), spectral_analysis (FFT real via Octave sobre una senal)."""
    return compute_music_math(preset, f0, n_harmonics, n_power, signal, fs)

@mcp.tool()
def linear_algebra(mode: str = "eigen", preset: str = "known_symmetric",
                    matrix: list = None, data: list = None) -> dict:
    """Algebra lineal via Octave: eigen (autovalores/autovectores), svd
    (descomposicion en valores singulares + verificacion), pca (componentes
    principales, varianza explicada), matrix_analysis (rango, condicion,
    determinante, inversa). Prerrequisito de persistent_homology_tool."""
    return compute_linear_algebra(mode, preset, matrix, data)

@mcp.tool()
def persistent_homology(preset: str = "circle", points: list = None,
                         max_edge_length: float = None, max_dim: int = 2,
                         n_points: int = 20, seed: int = 1, run_id: str = None) -> dict:
    """Homologia persistente (H0, H1) sobre una nube de puntos via complejo
    de Vietoris-Rips y reduccion de matriz de borde. Presets sinteticos
    validados (circle, two_clusters, random_noise) o custom via 'points'
    para datos reales -- por ejemplo nubes reconstruidas de un embedding
    de Takens (conexion directa con TritOS). Si se indica run_id, guarda
    points/h0_diagram/h1_diagram en el workspace para graficar despues con
    plot_workspace_run (plot_type=persistence_diagram)."""
    return compute_persistent_homology(preset, points, max_edge_length, max_dim, n_points, seed, run_id)

@mcp.tool()
def statistics(mode: str = "linear_regression", preset: str = "known_linear",
                x: list = None, y: list = None, sample: list = None, mu0: float = 5.0,
                prior_a: float = 1.0, prior_b: float = 1.0, successes: int = 7, trials: int = 10) -> dict:
    """Estadistica e inferencia via Octave: linear_regression (minimos
    cuadrados), correlation (Pearson r), t_test (una muestra, t-stat +
    p-value via betainc), bayesian_beta_binomial (actualizacion conjugada
    Beta-Binomial). Pensado para analisis de riesgo (QGIS)."""
    return compute_statistics(mode, preset, x, y, sample, mu0, prior_a, prior_b, successes, trials)

@mcp.tool()
def number_theory(mode: str = "primality_test", preset: str = "known_cases", n: int = None,
                   p: int = None, q: int = None, e: int = 17, message: int = None,
                   curve_a: int = None, curve_b: int = None, curve_p: int = None,
                   point1: list = None, point2: list = None) -> dict:
    """Teoria de numeros con aplicacion criptografica: primality_test
    (Miller-Rabin, detecta numeros de Carmichael), rsa_toy (genera par de
    claves, cifra/descifra, valida contra ejemplo clasico del paper RSA),
    elliptic_curve_add (suma/duplicacion de puntos, validado contra
    Hankerson et al). Conecta con chinese_remainder via RSA-CRT."""
    return compute_number_theory(mode, preset, n, p, q, e, message,
                                   curve_a, curve_b, curve_p, point1, point2)

@mcp.tool()
def symbolic(mode: str = "simplify", preset: str = "known_simplify", expression: str = None,
             variable: str = "x", lower_limit: str = None, upper_limit: str = None,
             point: str = "0", order: int = 5) -> dict:
    """Algebra simbolica via sympy: simplify, solve (resolver ecuaciones),
    differentiate (derivada), integrate (indefinida o definida con limites),
    taylor_series. Puente necesario porque Octave es 100% numerico."""
    return compute_symbolic(mode, preset, expression, variable, lower_limit, upper_limit, point, order)

@mcp.tool()
def optimization(mode: str = "linear_programming", preset: str = "known_lp", sense: str = "max",
                  c: list = None, A_ub: list = None, b_ub: list = None, expression: str = None,
                  start: list = None, learning_rate: float = 0.1, n_iterations: int = 200) -> dict:
    """Optimizacion: linear_programming (via glpk nativo de Octave),
    gradient_descent (gradiente EXACTO simbolico via sympy, no diferencias
    finitas). Presets validados contra optimos conocidos."""
    return compute_optimization(mode, preset, sense, c, A_ub, b_ub, expression, start, learning_rate, n_iterations)

@mcp.tool()
def pde(mode: str = "heat_equation", preset: str = "known_first_mode", L: float = 1.0,
        coefficient: float = 0.01, n_points: int = 50, t_final: float = None,
        initial_profile: list = None) -> dict:
    """Ecuaciones en derivadas parciales via diferencias finitas explicitas
    en Octave: heat_equation (u_t=alpha*u_xx), wave_equation (u_tt=c^2*u_xx).
    Validado contra solucion analitica del primer modo normal. Extension de
    stiff_ode_tool hacia EDPs -- relevante para propagacion termica LIG."""
    return compute_pde(mode, preset, L, coefficient, n_points, t_final, initial_profile)

@mcp.tool()
def braid_group(mode: str = "verify_braid_relation", sequence: str = "1,2,1",
                 initial_state: list = None) -> dict:
    """Grupos de trenzas y anyones de Fibonacci: verify_braid_relation
    (unitariedad + relacion de Yang-Baxter), apply_braid_sequence (aplica
    una secuencia de trenzas a un estado inicial, preserva la norma).
    Basado en Bonesteel et al 2005. Conexion con computacion cuantica
    topologica y con persistent_homology_tool / linear_algebra_tool."""
    return compute_braid_group(mode, sequence, initial_state)

@mcp.tool()
def population_dynamics(mode: str = "lotka_volterra", a: float = 1.0, b: float = 0.1,
                         c: float = 1.5, d: float = 0.075, x0: float = 10.0, y0: float = 5.0,
                         r: float = 0.5, K: float = 100.0, t_max: float = 50.0, n_points: int = 50) -> dict:
    """Dinamica de poblaciones: lotka_volterra (depredador-presa),
    logistic_growth (capacidad de carga). Relevante para cultivo de kelp
    en infraestructura de longline existente."""
    return compute_population_dynamics(mode, a, b, c, d, x0, y0, r, K, t_max, n_points)

@mcp.tool()
def reaction_diffusion(mode: str = "check_turing_instability", a11: float = 1.0, a12: float = -1.0,
                        a21: float = 2.0, a22: float = -1.5, Du: float = 1.0, Dv: float = 10.0) -> dict:
    """Inestabilidad de Turing (reaccion-difusion linealizada): evalua las
    4 condiciones analiticas clasicas y compara tasa de crecimiento numerica
    vs analitica en el numero de onda mas inestable. Mecanismo detras de
    patrones biologicos (rayas, manchas, morfogenesis)."""
    return compute_reaction_diffusion(mode, a11, a12, a21, a22, Du, Dv)

@mcp.tool()
def enzyme_kinetics(mode: str = "compare", k1: float = 100.0, km1: float = 10.0, k2: float = 5.0,
                     E0: float = 1.0, S0: float = 100.0, t_max: float = 5.0, n_points: int = 50) -> dict:
    """Cinetica enzimatica: full_kinetics (E+S<->ES->E+P completo),
    michaelis_menten (aproximacion QSSA), compare (valida cuando la
    aproximacion es correcta, E0<<S0)."""
    return compute_enzyme_kinetics(mode, k1, km1, k2, E0, S0, t_max, n_points)


@mcp.tool()
def tritbraid(mode: str = "validate_physics", program: str = "1,2,M,0,M,2,M", seed: int = 42,
              initial_state: list = None) -> dict:
    """DSL TritBraid: secuencias de trenzas de Fibonacci que colapsan a un trit
    ternario (-1,0,+1). Tokens del programa: 0=identidad, 1=sigma1 (diagonal,
    no mezcla canales), 2=sigma2 (mezcla via matriz F), M=medicion (colapso
    proyectivo, regla de Born). Modes: run_program (ejecuta el programa dado
    y devuelve traza completa), validate_physics (verifica unitariedad,
    invariancia bajo identidad/sigma1, y mezcla bajo sigma2). Misma
    construccion de Bonesteel et al 2005 que braid_group_tool -- puente
    concreto hacia el sistema ternario de TritOS."""
    return compute_tritbraid(mode, program, seed, initial_state)

@mcp.tool()
def historian(mode: str = "validate", analysis_type: str = "inflation", text_data: str = None,
              preset: str = None) -> dict:
    """Orquestador de analisis historico: parsea numeros de texto libre via
    regex (sin NLP complejo), arma arrays de numpy, y ajusta el motor
    correspondiente segun analysis_type -- inflation/demographics (regresion
    log-lineal: tasa anual %, R2), trade_network (centralidad de red:
    fuerza entrante + autovector, identifica el hub), units_entropy
    (entropia de Shannon sobre unidades historicas de medida -- indice de
    homogeneidad 0-100%), o benford (test de bondad de ajuste chi2 contra
    la distribucion de Benford sobre primeros digitos -- detecta cifras
    redondeadas/inventadas en padrones tributarios). Con pocos datos
    extraidos, escala en vez de adivinar. Modes: analyze (requiere
    text_data o preset), validate (corre 6 casos sinteticos con verdad
    conocida)."""
    return compute_historian(mode, analysis_type, text_data, preset)

@mcp.tool()
def antibiotic_diffusion(mode: str = "validate", C0: float = 1000.0, a: float = 0.3,
                          D: float = 5e-6, MIC: float = 1.0, t: float = 57600.0) -> dict:
    """Bioensayo de difusion en disco tipo Kirby-Bauer: difusion radial 2D
    exacta (Carslaw & Jaeger, disco de concentracion uniforme C0 en agar
    homogeneo) mas la aproximacion clasica de fuente puntual de Cooper.
    Liberacion instantanea, sin degradacion ni consumo bacteriano --
    estimacion de ordenes de magnitud, no reemplaza ensayo real. Modes:
    zone_prediction (radio/diametro de halo a un C0 y tiempo de incubacion
    dados, exacto vs aproximacion puntual), calibration_curve (barre varias
    dosis, ajusta diametro^2 vs ln(C0) -- ley lineal de Cooper), validate
    (4 chequeos: conservacion de masa, limite de fuente puntual, limite de
    tiempo temprano, ley de Cooper)."""
    return compute_antibiotic_diffusion(mode, C0, a, D, MIC, t)

@mcp.tool()
def plague_sir(mode: str = "validate", text_data: str = None, preset: str = None,
                gamma: float = 0.4, poblacion_estimada: float = 2000.0) -> dict:
    """SIR inverso para brotes historicos de peste: parsea defunciones
    semanales de texto libre via regex, ajusta beta (tasa de contagio) con
    curve_fit manteniendo gamma fijo (parametro de literatura, no medido),
    integra SIR con RK4, y reporta R0=beta/gamma. Proxy cuantitativo cuando
    no hay fuente epidemiologica directa -- no corrige subregistro,
    migracion, ni estacionalidad. Modes: fit_beta (requiere text_data o
    preset='peste_demo'), validate (compara contra brote sintetico con
    beta/R0 conocidos)."""
    return compute_plague_sir(mode, text_data, preset, gamma, poblacion_estimada)

@mcp.tool()
def settlement_clusters(mode: str = "validate", puntos_por_periodo: list = None,
                         periodos: list = None, radio: float = 1.0,
                         radio_match: float = 2.0, run_id: str = None) -> dict:
    """Proxy arqueologico de barrios/clusters sociales: clusteriza
    coordenadas de hallazgos por distancia (union-find a radio fijo) en
    cada periodo/estrato, y rastrea clusters entre periodos consecutivos
    por proximidad de centroides -- detecta nacimiento y muerte de
    asentamientos. No hace inferencia cronologica, el orden de periodos
    lo define quien llama. Modes: analyze (requiere puntos_por_periodo y
    periodos), validate (corre preset sintetico con migracion/fision
    conocida). Si se indica run_id (solo aplica en mode=analyze), guarda
    points_all/centroids_all en el workspace para graficar despues con
    plot_workspace_run (plot_type=settlement_map)."""
    return compute_settlement_clusters(mode, puntos_por_periodo, periodos, radio, radio_match, run_id)

@mcp.tool()
def archaeological_simulation(mode: str = "malthusian_growth",
                               r: float = 0.5, K0: float = 100.0, K_amplitude: float = 20.0,
                               K_period: float = 20.0, x0: float = 10.0, t_max: float = 100.0,
                               n_points: int = 60, p_innovation: float = 0.03, q_imitation: float = 0.4,
                               M_market: float = 1000.0, settlements: list = None,
                               gravity_exponent: float = 2.0, G_constant: float = 1.0,
                               K_capacity: float = 200.0, a_attack: float = 0.02, h_handling: float = 0.4,
                               e_efficiency: float = 0.6, m_mortality: float = 0.3,
                               R0: float = 50.0, P0: float = 10.0) -> dict:
    """Simulacion de dinamicas socio-demograficas arqueologicas: malthusian_growth
    (crecimiento logistico con capacidad de carga variable por ciclos climaticos),
    technology_diffusion (modelo de Bass de adopcion de innovaciones, solucion
    analitica cerrada), trade_network (modelo gravitacional de rutas comerciales
    entre asentamientos, identifica el hub por centralidad de autovector),
    collapse_dynamics (ciclo auge-colapso poblacion/recursos tipo
    Rosenzweig-MacArthur, analogo a los secular cycles de Turchin)."""
    return compute_archaeological_simulation(mode, r, K0, K_amplitude, K_period, x0, t_max, n_points,
                                              p_innovation, q_imitation, M_market, settlements,
                                              gravity_exponent, G_constant, K_capacity, a_attack,
                                              h_handling, e_efficiency, m_mortality, R0, P0)


@mcp.tool()
def historical_extractor(mode: str = "validate", text_data: str = None,
                          objetos: list = None, objeto_salario: str = None) -> dict:
    """Extrae MULTIPLES series (anio, valor) de un mismo texto historico via
    regex por oracion (no NLP), una serie por objeto/concepto mencionado
    (ej: trigo, cebada, jornal). Corre tendencia por regresion log-lineal
    en cada serie (reusa el motor de historian), calcula salario real
    indexado si se indica objeto_salario, y correlacion de Pearson entre
    series de precios que se solapan en anios. NO interpreta causalidad
    historica (crisis, epidemias) -- solo tasas, indices y correlaciones.
    Modes: analyze (requiere text_data + objetos, opcional objeto_salario),
    validate (preset sintetico: trigo/cebada correlacionados, salario real
    cayendo)."""
    return compute_historical_extractor(mode, text_data, objetos, objeto_salario)

@mcp.tool()
def workspace_save(run_id: str = None, data: dict = None, meta: dict = None) -> dict:
    """Guarda arrays/resultados de un analisis bajo un run_id para reutilizarlos
    despues (ej: en plot_tool) sin recalcular. Si run_id se omite, se autogenera."""
    return save_run(run_id, data or {}, meta)

@mcp.tool()
def workspace_load(run_id: str, keys: list = None) -> dict:
    """Carga un run guardado previamente por run_id. Si keys se omite, devuelve
    todos los arrays (cuidado con trayectorias muy largas: usar workspace_describe
    primero)."""
    return load_run(run_id, keys)

@mcp.tool()
def workspace_list(filter_tool: str = None) -> dict:
    """Lista todos los runs guardados en el workspace, opcionalmente filtrados
    por tool de origen (ej: 'compute_lyapunov_exponent')."""
    return list_runs(filter_tool)

@mcp.tool()
def workspace_describe(run_id: str) -> dict:
    """Muestra shapes/dtypes de un run sin cargar los arrays completos a memoria
    (util para trayectorias largas antes de graficar)."""
    return describe_run(run_id)

@mcp.tool()
def workspace_delete(run_id: str) -> dict:
    """Borra un run del workspace (libera espacio en disco)."""
    return delete_run(run_id)

@mcp.tool()
def plot_workspace_run(run_id: str, plot_type: str = "auto", title: str = None, array_name: str = None) -> dict:
    """Genera una visualizacion (PNG en base64 + guardado en disco) a partir de
    un run guardado en el workspace (ej: la trayectoria de un atractor guardada
    por compute_lyapunov con run_id). No recalcula nada, solo lee y grafica.
    plot_type: auto (infiere segun el tool de origen), attractor_3d,
    attractor_2d, line, scatter, heatmap."""
    return plot_run(run_id, plot_type, title, array_name)

@mcp.tool()
def numeral_systems_embedding(method: str = "umap", extra_systems: list = None,
                               n_neighbors: int = None, perplexity: float = None,
                               random_state: int = 1, run_id: str = None) -> dict:
    """Vectoriza sistemas numericos antiguos (base, tipo posicional/aditivo/
    fisico, presencia de cero, redundancia representacional, soporte fisico)
    y proyecta a 2D via UMAP o t-SNE, para explorar agrupamientos
    estructurales entre culturas. Dataset base: maya_long_count, suanpan,
    soroban, roman_hand_abacus, yupana_depasquale, quipu, ifa_binary.
    Extensible via extra_systems (lista de dicts con el mismo schema). Con
    pocos sistemas, n_neighbors/perplexity se clampean automaticamente. Si
    se indica run_id, guarda el embedding en el workspace para graficar
    despues con plot_workspace_run (plot_type=numeral_embedding)."""
    return compute_numeral_systems_embedding(method, extra_systems, n_neighbors,
                                              perplexity, random_state, run_id)


# ==== Herramientas agregadas para paridad con octave-mcp (paso 2) ====

@mcp.tool()
def compute_gradient_hessian(expression: str, variables: str, order: int = 1) -> dict:
    """Deriva simbolicamente (via sympy) el gradiente y, si order>=2, la matriz Hessiana de una expresion multivariable."""
    return _compute_gradient_hessian(expression, variables, order)

@mcp.tool()
def compute_jacobian(expressions: str, variables: str) -> dict:
    """Calcula la matriz Jacobiana simbolica de un sistema de 'expressions' (separadas por ;) respecto a 'variables'."""
    return _compute_jacobian(expressions, variables)

@mcp.tool()
def math_error_analyzer(mode: str = "validate", params: dict = None) -> dict:
    """Analisis de error numerico: numero de condicion, error de truncamiento vs redondeo, derivada analitica de referencia."""
    return compute_math_error_analysis(mode, **(params or {}))

@mcp.tool()
def math_benchmark(mode: str = "validate", params: dict = None) -> dict:
    """Benchmark de metodos numericos: comparacion de metodos ODE (Euler/RK2/RK4), cuadratura (trapezoidal/Simpson/Gauss-Legendre), y busqueda de raices (biseccion/Newton/secante)."""
    return compute_math_benchmark(mode, **(params or {}))

@mcp.tool()
def math_interpolation(mode: str = "validate", params: dict = None) -> dict:
    """Interpolacion numerica: Lagrange (baricentrica), splines cubicos naturales, comparacion de nodos (Chebyshev vs equiespaciados)."""
    return compute_math_interpolation(mode, **(params or {}))

@mcp.tool()
def run_math_pipeline(steps: list = None, mode: str = "validate") -> dict:
    """Ejecuta un pipeline de pasos encadenados entre distintas herramientas matematicas del servidor."""
    return _run_math_pipeline(steps, mode)

@mcp.tool()
def math_interpreter(query: str, auto_run: bool = False) -> dict:
    """Interpreta una consulta matematica en lenguaje natural (castellano) y la traduce a una llamada de herramienta."""
    return _interpret_math_query(query, auto_run)

@mcp.tool()
def math_visualization(mode: str = "function_plot", params: dict = None) -> dict:
    """Visualizacion matematica: graficos de funciones, retratos de fase, campos vectoriales, diagramas de bifurcacion."""
    return compute_math_visualization(mode=mode, **(params or {}))

@mcp.tool()
def math_explainer(source_tool: str, result: dict, level: str = "tecnico") -> dict:
    """Traduce el resultado crudo (dict) de otra herramienta matematica a una explicacion en lenguaje natural, con nivel tecnico ajustable."""
    return _interpret_and_explain(source_tool, result, level)

@mcp.tool()
def machine_learning_math(mode: str, params: dict = None) -> dict:
    """Matematica de machine learning: funciones de costo, descenso de gradiente, regresion lineal/logistica, comparacion de regularizacion (ridge/lasso), PCA."""
    return compute_machine_learning_math(mode, **(params or {}))

@mcp.tool()
def financial_math(mode: str, params: dict = None) -> dict:
    """Matematica financiera: Black-Scholes, griegas de opciones, VaR (parametrico/historico), valuacion de anualidades y bonos, riesgo catastrofico."""
    return compute_financial_math(mode, **(params or {}))

@mcp.tool()
def game_theory(mode: str, params: dict = None) -> dict:
    """Teoria de juegos: equilibrio de Nash, eliminacion de estrategias dominadas, valor de juegos de suma cero, valor de Shapley, nucleo cooperativo, dinamica evolutiva."""
    return compute_game_theory(mode, **(params or {}))

@mcp.tool()
def tensor_calculus(mode: str, params: dict = None) -> dict:
    """Calculo tensorial/geometria diferencial: simbolos de Christoffel, tensor de Riemann, Ricci, curvatura escalar, ecuaciones geodesicas (backend simbolico o numerico)."""
    return compute_tensor_calculus(mode, **(params or {}))

@mcp.tool()
def network_science(mode: str, params: dict = None) -> dict:
    """Ciencia de redes: centralidad, deteccion de comunidades (Louvain), modelos de crecimiento, metricas de grafos."""
    return compute_network_science(mode, **(params or {}))

@mcp.tool()
def population_genetics(mode: str, params: dict = None) -> dict:
    """Genetica de poblaciones: equilibrio de Hardy-Weinberg, deriva genetica (simulacion), seleccion natural, tiempo de coalescencia, distancia genetica (Fst)."""
    return compute_population_genetics(mode, **(params or {}))

@mcp.tool()
def wavelet(mode: str, params: dict = None) -> dict:
    """Analisis wavelet: transformada continua (CWT) y discreta (DWT), denoising, deteccion de transitorios."""
    return compute_wavelet(mode, **(params or {}))

@mcp.tool()
def percolation_theory(mode: str, params: dict = None) -> dict:
    """Teoria de percolacion: percolacion de sitios/enlaces en reticulas, umbral critico, percolacion sobre grafos."""
    return compute_percolation_theory(mode, **(params or {}))

@mcp.tool()
def chemometrics(mode: str, params: dict = None) -> dict:
    """Quimiometria: calibracion PLS y PCR, diseno de experimentos (factorial completo, Box-Behnken, hipercubo latino), validacion de recuperacion."""
    return compute_chemometrics(mode, params or {})

@mcp.tool()
def econometrics(mode: str, params: dict = None) -> dict:
    """Econometria: test ADF, forecast ARIMA, ajuste GARCH(1,1), cointegracion Engle-Granger, efectos fijos de panel, IV/2SLS, causalidad de Granger."""
    return compute_econometrics(mode, params or {})

@mcp.tool()
def stochastic_processes(mode: str, params: dict = None) -> dict:
    """Procesos estocasticos: movimiento browniano, proceso de Ornstein-Uhlenbeck, cadenas de Markov."""
    return compute_stochastic_processes(mode, **(params or {}))

@mcp.tool()
def information_theory(mode: str, params: dict = None) -> dict:
    """Teoria de la informacion: entropia de Shannon, divergencia KL, informacion mutua, entropia cruzada, entropia de secuencias."""
    return compute_information_theory(mode, **(params or {}))

@mcp.tool()
def control_theory(mode: str, params: dict = None) -> dict:
    """Teoria de control: respuesta PID a escalon, criterio de Routh-Hurwitz, lugar de raices, control caotico OGY."""
    return compute_control_theory(mode, **(params or {}))

@mcp.tool()
def optimal_control(mode: str, params: dict = None) -> dict:
    """Control optimo: regulador LQR, principio del maximo de Pontryagin (caso LQ), programacion dinamica."""
    return compute_optimal_control(mode, **(params or {}))

@mcp.tool()
def spatial_statistics(mode: str, params: dict = None) -> dict:
    """Estadistica espacial: I de Moran, C de Geary, semivariograma, interpolacion por kriging."""
    return compute_spatial_statistics(mode, **(params or {}))

@mcp.tool()
def text_analysis_math(mode: str, params: dict = None) -> dict:
    """Matematica del analisis de texto: distancia de edicion, modelos n-grama, leyes de frecuencia (Zipf), estilometria."""
    return compute_text_analysis_math(mode, **(params or {}))

@mcp.tool()
def archaeoastronomy(mode: str, params: dict = None) -> dict:
    """Calculos astronomicos para arqueoastronomia (algoritmos de Meeus): posicion solar/lunar, equinoccios/solsticios, verificacion de alineamientos arqueologicos."""
    return compute_archaeoastronomy(mode, **(params or {}))

@mcp.tool()
def quantum_information(mode: str, params: dict = None) -> dict:
    """Informacion cuantica: vector de Bloch, secuencias de compuertas, Deutsch-Jozsa, busqueda de Grover, entropia de entrelazamiento, codigo de correccion bit-flip."""
    return compute_quantum_information(mode, **(params or {}))

@mcp.tool()
def paleography(mode: str = "validate", params: dict = None) -> dict:
    """Tres motores cuantitativos de paleografia/codicologia: seriation (analisis de correspondencia via SVD), feature_dating_regression (estima fecha de documentos sin fecha), letterform_classification (nearest-centroid sobre rasgos normalizados)."""
    return compute_paleography(mode, **(params or {}))

@mcp.tool()
def abstract_algebra(mode: str = "validate", params: dict = None) -> dict:
    """Algebra abstracta sobre estructuras finitas chicas (orden<=8): tablas de Cayley, verificacion de axiomas de grupo/anillo/cuerpo, isomorfismos por fuerza bruta."""
    return compute_abstract_algebra(mode, **(params or {}))

if __name__ == "__main__":
    mcp.run()

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


@mcp.tool()
def composite_homogenization_tool(mode: str, params: dict = None) -> dict:
    """Propiedades efectivas de un material compuesto de 2 fases via reglas de mezcla Voigt (cota superior, iso-deformacion) y Reuss (cota inferior, iso-esfuerzo), derivadas simbolicamente con sympy. mode='elastic_modulus' o 'thermal_conductivity'. params: f1 (fraccion de volumen de fase 1), P1, P2 (propiedad de cada fase)."""
    return compute_composite_homogenization(mode, **(params or {}))
