#!/usr/bin/env python3
"""
patch_add_mcmc.py
Agrega el modo 'mcmc' (Metropolis-Hastings generico) a stochastic_processes_tool.py
como un modo nuevo dentro del dispatcher existente (no crea un modulo aparte), y
actualiza la docstring del wrapper en server.py.

Correr desde ~/mcp-octave-real:
    python3 patch_add_mcmc.py
"""
import re
from pathlib import Path

TOOL = Path("stochastic_processes_tool.py")
SERVER = Path("server.py")

assert TOOL.exists(), "Falta stochastic_processes_tool.py en el directorio actual"
assert SERVER.exists(), "Falta server.py en el directorio actual"

src = TOOL.read_text()

# --- 1. backup ---
backup = TOOL.with_suffix(".py.bak_mcmc")
backup.write_text(src)
print(f"Backup guardado en {backup}")

# --- 2. evitar doble aplicacion ---
if "def compute_mcmc" in src:
    print("compute_mcmc ya existe en el archivo, no se modifica nada.")
else:
    # --- 3. insertar compute_mcmc antes de compute_stochastic_processes ---
    MCMC_FN = '''

def compute_mcmc(target, n_samples=5000, n_burn=1000, proposal_scale=0.5, x0=None, seed=None):
    """
    Metropolis-Hastings generico con propuesta random-walk gaussiana.

    target: {"type": "gaussian", "mean": [...], "cov": [[...]]}
         o  {"type": "custom", "log_density_expr": "expresion en x0,x1,...",
             "variables": ["x0", "x1", ...]}
    La expresion custom se parsea con sympy (no eval crudo), mismo criterio
    que symbolic_tool/tensor_calculus_tool en el resto del repo.

    Devuelve media/covarianza posterior, acceptance rate, effective sample
    size (via tiempo de autocorrelacion integrado) y una traza sub-muestreada
    apta para math_visualization_tool.
    """
    ttype = target.get("type")

    if ttype == "gaussian":
        mean = np.array(target["mean"], dtype=float)
        cov = np.array(target["cov"], dtype=float)
        cov_inv = np.linalg.inv(cov)
        dim = len(mean)

        def log_density(x):
            d = x - mean
            return -0.5 * float(d @ cov_inv @ d)

    elif ttype == "custom":
        import sympy as sp
        variables = target["variables"]
        syms = sp.symbols(variables)
        if not isinstance(syms, (list, tuple)):
            syms = (syms,)
        expr = sp.sympify(target["log_density_expr"])
        f = sp.lambdify(syms, expr, "numpy")
        dim = len(variables)

        def log_density(x):
            return float(f(*x))

    else:
        raise ValueError(f"target.type desconocido: {ttype!r} (usar 'gaussian' o 'custom')")

    rng = np.random.default_rng(seed)
    x_curr = np.zeros(dim) if x0 is None else np.array(x0, dtype=float)

    n_total = n_burn + n_samples
    chain = np.zeros((n_total, dim))
    chain[0] = x_curr
    current_log_d = log_density(x_curr)
    n_accept = 0

    for i in range(1, n_total):
        proposal = chain[i - 1] + rng.normal(0.0, proposal_scale, dim)
        proposal_log_d = log_density(proposal)
        log_alpha = proposal_log_d - current_log_d
        if np.log(rng.uniform()) < log_alpha:
            chain[i] = proposal
            current_log_d = proposal_log_d
            n_accept += 1
        else:
            chain[i] = chain[i - 1]

    samples = chain[n_burn:]
    acceptance_rate = n_accept / (n_total - 1)

    posterior_mean = samples.mean(axis=0)
    if dim > 1:
        posterior_cov = np.cov(samples.T)
        posterior_std = np.sqrt(np.diag(posterior_cov))
    else:
        posterior_cov = np.array([[samples.var()]])
        posterior_std = np.array([samples.std()])

    def integrated_autocorr_time(x, max_lag=None):
        n = len(x)
        if max_lag is None:
            max_lag = min(n // 3, 1000)
        xc = x - x.mean()
        var = xc.var()
        if var == 0:
            return 1.0
        acf = np.correlate(xc, xc, mode="full")[n - 1:] / (var * n)
        tau = 1.0
        for lag in range(1, max_lag):
            if acf[lag] < 0.05:
                break
            tau += 2 * acf[lag]
        return max(tau, 1.0)

    taus = [integrated_autocorr_time(samples[:, d]) for d in range(dim)]
    tau_mean = float(np.mean(taus))
    ess = len(samples) / tau_mean

    track_every = max(1, len(samples) // 500)
    trace = samples[::track_every]

    return {
        "mode": "mcmc",
        "target_type": ttype,
        "dim": dim,
        "n_samples": n_samples,
        "n_burn": n_burn,
        "acceptance_rate": round(float(acceptance_rate), 4),
        "posterior_mean": [round(float(v), 6) for v in posterior_mean],
        "posterior_std": [round(float(v), 6) for v in posterior_std],
        "posterior_cov": [[round(float(v), 6) for v in row] for row in posterior_cov] if dim > 1 else None,
        "integrated_autocorr_time": round(tau_mean, 4),
        "effective_sample_size": round(float(ess), 2),
        "trace": [[round(float(v), 6) for v in row] for row in trace],
    }

'''

    anchor = "\ndef compute_stochastic_processes(mode, **kwargs):"
    assert anchor in src, "No se encontro el anchor 'def compute_stochastic_processes' en el archivo"
    src = src.replace(anchor, MCMC_FN + anchor, 1)

    # --- 4. agregar al dispatcher ---
    old_dispatch = '''    fns = {
        "brownian_motion": compute_brownian_motion,
        "ornstein_uhlenbeck": compute_ornstein_uhlenbeck,
        "markov_chain": compute_markov_chain,
    }'''
    new_dispatch = '''    fns = {
        "brownian_motion": compute_brownian_motion,
        "ornstein_uhlenbeck": compute_ornstein_uhlenbeck,
        "markov_chain": compute_markov_chain,
        "mcmc": compute_mcmc,
    }'''
    assert old_dispatch in src, "No se encontro el dict 'fns' del dispatcher"
    src = src.replace(old_dispatch, new_dispatch, 1)

    # --- 5. actualizar schema ---
    old_enum = '"mode": {"type": "string", "enum": ["brownian_motion", "ornstein_uhlenbeck", "markov_chain"]},'
    new_enum = '"mode": {"type": "string", "enum": ["brownian_motion", "ornstein_uhlenbeck", "markov_chain", "mcmc"]},'
    assert old_enum in src, "No se encontro la linea de enum del schema"
    src = src.replace(old_enum, new_enum, 1)

    old_props_tail = '''            "transition_matrix": {"type": "array"}, "initial_state": {"type": "integer"},
            "target_state": {"type": "integer"},
        },'''
    new_props_tail = '''            "transition_matrix": {"type": "array"}, "initial_state": {"type": "integer"},
            "target_state": {"type": "integer"},
            "target": {"type": "object"}, "n_samples": {"type": "integer"},
            "n_burn": {"type": "integer"}, "proposal_scale": {"type": "number"},
        },'''
    assert old_props_tail in src, "No se encontro el cierre de 'properties' del schema"
    src = src.replace(old_props_tail, new_props_tail, 1)

    # --- 6. actualizar descripcion del schema ---
    old_desc = '"description": "Procesos estocasticos: movimiento browniano (estandar/con drift/geometrico), proceso de Ornstein-Uhlenbeck (reversion a la media, util para variables ambientales con equilibrio), y cadenas de Markov discretas (distribucion estacionaria, tiempo de primer paso).",'
    new_desc = '"description": "Procesos estocasticos: movimiento browniano (estandar/con drift/geometrico), proceso de Ornstein-Uhlenbeck (reversion a la media, util para variables ambientales con equilibrio), cadenas de Markov discretas (distribucion estacionaria, tiempo de primer paso), y mcmc (Metropolis-Hastings generico sobre una gaussiana o una densidad custom vía sympy).",'
    assert old_desc in src, "No se encontro la linea de description del schema"
    src = src.replace(old_desc, new_desc, 1)

    # --- 7. agregar validaciones al __main__ ---
    old_main_tail = '''    r3 = compute_stochastic_processes(mode="markov_chain", transition_matrix=[[0.9, 0.1], [0.3, 0.7]], initial_state=0, n_steps=30, target_state=1)
    print(r3)'''
    new_main_tail = '''    r3 = compute_stochastic_processes(mode="markov_chain", transition_matrix=[[0.9, 0.1], [0.3, 0.7]], initial_state=0, n_steps=30, target_state=1)
    print(r3)

    # mcmc: gaussiana 2D correlacionada, verificar contra media/cov exactos
    r4 = compute_stochastic_processes(
        mode="mcmc",
        target={"type": "gaussian", "mean": [1.0, -2.0], "cov": [[1.0, 0.5], [0.5, 2.0]]},
        n_samples=20000, n_burn=2000, proposal_scale=1.0, seed=42,
    )
    print("mcmc gaussian 2D: acceptance_rate=", r4["acceptance_rate"],
          "posterior_mean=", r4["posterior_mean"], "(esperado ~[1.0, -2.0])",
          "posterior_cov=", r4["posterior_cov"], "(esperado ~[[1.0,0.5],[0.5,2.0]])",
          "ess=", r4["effective_sample_size"])

    # mcmc: Laplace(mu=1, b=1) via expresion custom con Abs, verificar media/varianza exactas
    r5 = compute_stochastic_processes(
        mode="mcmc",
        target={"type": "custom", "log_density_expr": "-Abs(x0 - 1)", "variables": ["x0"]},
        n_samples=20000, n_burn=2000, proposal_scale=1.5, seed=42,
    )
    print("mcmc laplace custom: acceptance_rate=", r5["acceptance_rate"],
          "posterior_mean=", r5["posterior_mean"], "(esperado ~1.0)",
          "posterior_var=", [s ** 2 for s in r5["posterior_std"]], "(esperado ~2.0)",
          "ess=", r5["effective_sample_size"])'''
    assert old_main_tail in src, "No se encontro el bloque final de __main__"
    src = src.replace(old_main_tail, new_main_tail, 1)

    TOOL.write_text(src)
    print("stochastic_processes_tool.py actualizado con el modo 'mcmc'.")

# --- 8. actualizar docstring del wrapper en server.py ---
server_src = SERVER.read_text()
old_doc = '"Procesos estocasticos: movimiento browniano (estandar/con drift/geometrico), proceso de Ornstein-Uhlenbeck (reversion a la media, util para variables ambientales con equilibrio), y cadenas de Markov discretas (distribucion estacionaria, tiempo de primer paso)."'
new_doc = '"Procesos estocasticos: movimiento browniano (estandar/con drift/geometrico), proceso de Ornstein-Uhlenbeck (reversion a la media, util para variables ambientales con equilibrio), cadenas de Markov discretas (distribucion estacionaria, tiempo de primer paso), y mcmc (Metropolis-Hastings generico: target gaussiano o custom vía expresion sympy, devuelve media/covarianza posterior, acceptance rate y effective sample size)."'

if old_doc in server_src:
    backup2 = SERVER.with_suffix(".py.bak_mcmc")
    backup2.write_text(server_src)
    print(f"Backup guardado en {backup2}")
    server_src = server_src.replace(old_doc, new_doc, 1)
    SERVER.write_text(server_src)
    print("Docstring de stochastic_processes_tool en server.py actualizada.")
elif new_doc in server_src:
    print("La docstring de server.py ya estaba actualizada, no se modifica nada.")
else:
    print("AVISO: no se encontro la docstring exacta esperada en server.py — revisar manualmente el wrapper de stochastic_processes_tool ahi.")

print("\nListo. Revisa los diffs con: git diff stochastic_processes_tool.py server.py")
print("Si algo salio mal, restaura con:")
print("  cp stochastic_processes_tool.py.bak_mcmc stochastic_processes_tool.py")
print("  cp server.py.bak_mcmc server.py")
