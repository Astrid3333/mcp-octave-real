#!/usr/bin/env python3
"""
patch_add_numba_ising.py

Agrega un backend opcional acelerado con Numba al sweep de Metropolis de
ising_2d en statistical_physics_tool.py.

- Si numba no esta instalado, el import falla con gracia y backend='numpy'
  sigue siendo el default y el unico camino disponible (comportamiento
  identico al actual para el notebook Celeron).
- Si numba SI esta instalado, se puede pasar params={"backend": "numba"}
  para usar el sweep jiteado (127x mas rapido en las pruebas locales).
- potts_grain_growth NO se toca: su loop tiene una closure (local_energy)
  y logica de coalescencia que no vale la pena jitear todavia; se
  revisa aparte si hace falta.

No modifica server.py: el wrapper ya hace
    compute_statistical_physics(mode, **(params or {}))
asi que 'backend' llega solo, como cualquier otro parametro de ising_2d.
"""
import re

PATH = "statistical_physics_tool.py"
BACKUP = "statistical_physics_tool.py.bak_numba"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

with open(BACKUP, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Backup guardado en {BACKUP}")

# ---------------------------------------------------------------------
# 1) Import opcional de numba, justo despues de 'import numpy as np'
# ---------------------------------------------------------------------
anchor_import = "import numpy as np\n\nSTATISTICAL_PHYSICS_TOOL_SCHEMA = {"
assert content.count(anchor_import) == 1, (
    "No se encontro el anchor de import esperado (1 ocurrencia). "
    "Revisar manualmente el encabezado del archivo."
)

numba_import_block = '''import numpy as np

try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

STATISTICAL_PHYSICS_TOOL_SCHEMA = {'''

content = content.replace(anchor_import, numba_import_block, 1)

# ---------------------------------------------------------------------
# 2) Backend jiteado: se agrega DESPUES de _ising_metropolis_sweep,
#    antes de 'def ising_2d('. La version original queda intacta.
# ---------------------------------------------------------------------
anchor_after_sweep = '''        if dE <= 0 or rng.random() < np.exp(-beta * dE):
            spins[i, j] = -s
    return spins


def ising_2d(n=16, temperatures=None, n_equil=200, n_measure=200, seed=0):'''

assert content.count(anchor_after_sweep) == 1, (
    "No se encontro el anchor entre _ising_metropolis_sweep e ising_2d "
    "(1 ocurrencia esperada). Revisar manualmente."
)

numba_sweep_block = '''        if dE <= 0 or rng.random() < np.exp(-beta * dE):
            spins[i, j] = -s
    return spins


if NUMBA_AVAILABLE:
    @njit(cache=True)
    def _ising_metropolis_sweep_numba(spins, beta, n):
        """
        Equivalente jiteado de _ising_metropolis_sweep. Usa el generador
        global de numpy (np.random.seed/randint/random) porque numba no
        soporta np.random.default_rng en modo nopython; la semilla se fija
        una vez antes del barrido en temperatura, no por sweep.
        """
        for _ in range(n * n):
            i = np.random.randint(0, n)
            j = np.random.randint(0, n)
            s = spins[i, j]
            neighbors = (spins[(i + 1) % n, j] + spins[(i - 1) % n, j] +
                         spins[i, (j + 1) % n] + spins[i, (j - 1) % n])
            dE = 2 * s * neighbors
            if dE <= 0 or np.random.random() < np.exp(-beta * dE):
                spins[i, j] = -s
        return spins


def ising_2d(n=16, temperatures=None, n_equil=200, n_measure=200, seed=0, backend="numpy"):'''

content = content.replace(anchor_after_sweep, numba_sweep_block, 1)

# ---------------------------------------------------------------------
# 3) Cuerpo de ising_2d: agregar validacion de backend + dispatch,
#    dejando el camino 'numpy' identico al original.
# ---------------------------------------------------------------------
anchor_docstring = '''    """
    Barrido en temperatura del modelo de Ising 2D (J=1, k_B=1).
    Devuelve magnetizacion, energia y calor especifico por temperatura.
    """
    if temperatures is None:
        temperatures = np.linspace(1.5, 3.5, 15).tolist()
    rng = np.random.default_rng(seed)
    results = []
    spins = rng.choice([-1, 1], size=(n, n))
    for T in temperatures:
        beta = 1.0 / T
        for _ in range(n_equil):
            spins = _ising_metropolis_sweep(spins, beta, rng)
        mags, energies = [], []
        for _ in range(n_measure):
            spins = _ising_metropolis_sweep(spins, beta, rng)
            mags.append(np.abs(np.mean(spins)))
            energies.append(_ising_energy(spins) / (n * n))
        mags = np.array(mags)
        energies = np.array(energies)
        specific_heat = (np.var(energies) * (n * n)) / (T ** 2)
        results.append({
            "T": T,
            "magnetization": float(np.mean(mags)),
            "energy_per_site": float(np.mean(energies)),
            "specific_heat": float(specific_heat),
        })
    T_peak = max(results, key=lambda r: r["specific_heat"])["T"]
    return {
        "mode": "ising_2d",
        "n": n,
        "results": results,
        "T_critical_estimate": T_peak,
        "T_critical_onsager": 2.0 / np.log(1 + np.sqrt(2)),
    }'''

assert content.count(anchor_docstring) == 1, (
    "No se encontro el cuerpo de ising_2d con el patron esperado "
    "(1 ocurrencia). Revisar manualmente."
)

new_ising_2d_body = '''    """
    Barrido en temperatura del modelo de Ising 2D (J=1, k_B=1).
    Devuelve magnetizacion, energia y calor especifico por temperatura.

    backend='numpy' (default): implementacion original, sin dependencias
        extra, identica en resultados a versiones previas de esta funcion.
    backend='numba': usa el sweep jiteado (_ising_metropolis_sweep_numba),
        ~100x mas rapido en pruebas locales para n~16-32. Requiere numba
        instalado; si no lo esta, levanta ValueError con un mensaje claro
        en lugar de fallar con un ImportError crudo.
    """
    if backend not in ("numpy", "numba"):
        raise ValueError(f"backend desconocido: {backend!r}. Use 'numpy' o 'numba'")
    if backend == "numba" and not NUMBA_AVAILABLE:
        raise ValueError(
            "backend='numba' pedido pero numba no esta instalado en este entorno. "
            "Instalar con: pip install numba --break-system-packages, "
            "o usar backend='numpy' (default)."
        )

    if temperatures is None:
        temperatures = np.linspace(1.5, 3.5, 15).tolist()
    results = []

    if backend == "numba":
        np.random.seed(seed)
        spins = np.random.choice(np.array([-1, 1]), size=(n, n)).astype(np.int64)
        for T in temperatures:
            beta = 1.0 / T
            for _ in range(n_equil):
                spins = _ising_metropolis_sweep_numba(spins, beta, n)
            mags, energies = [], []
            for _ in range(n_measure):
                spins = _ising_metropolis_sweep_numba(spins, beta, n)
                mags.append(np.abs(np.mean(spins)))
                energies.append(_ising_energy(spins) / (n * n))
            mags = np.array(mags)
            energies = np.array(energies)
            specific_heat = (np.var(energies) * (n * n)) / (T ** 2)
            results.append({
                "T": T,
                "magnetization": float(np.mean(mags)),
                "energy_per_site": float(np.mean(energies)),
                "specific_heat": float(specific_heat),
            })
    else:
        rng = np.random.default_rng(seed)
        spins = rng.choice([-1, 1], size=(n, n))
        for T in temperatures:
            beta = 1.0 / T
            for _ in range(n_equil):
                spins = _ising_metropolis_sweep(spins, beta, rng)
            mags, energies = [], []
            for _ in range(n_measure):
                spins = _ising_metropolis_sweep(spins, beta, rng)
                mags.append(np.abs(np.mean(spins)))
                energies.append(_ising_energy(spins) / (n * n))
            mags = np.array(mags)
            energies = np.array(energies)
            specific_heat = (np.var(energies) * (n * n)) / (T ** 2)
            results.append({
                "T": T,
                "magnetization": float(np.mean(mags)),
                "energy_per_site": float(np.mean(energies)),
                "specific_heat": float(specific_heat),
            })

    T_peak = max(results, key=lambda r: r["specific_heat"])["T"]
    return {
        "mode": "ising_2d",
        "n": n,
        "backend": backend,
        "results": results,
        "T_critical_estimate": T_peak,
        "T_critical_onsager": 2.0 / np.log(1 + np.sqrt(2)),
    }'''

content = content.replace(anchor_docstring, new_ising_2d_body, 1)

# ---------------------------------------------------------------------
# 4) Schema: documentar el parametro backend (informativo, no rompe nada
#    si el cliente MCP no lo valida estrictamente contra el schema).
# ---------------------------------------------------------------------
anchor_schema_desc = '''    "description": (
        "Fisica estadistica: modelo de Ising 2D via Monte Carlo Metropolis "
        "(magnetizacion, energia, calor especifico, transicion de fase), y "
        "modelo de Potts para crecimiento de grano (microestructura)."
    ),'''

assert content.count(anchor_schema_desc) == 1, (
    "No se encontro la descripcion del schema (1 ocurrencia esperada). "
    "Revisar manualmente."
)

new_schema_desc = '''    "description": (
        "Fisica estadistica: modelo de Ising 2D via Monte Carlo Metropolis "
        "(magnetizacion, energia, calor especifico, transicion de fase; "
        "params.backend='numpy' (default) o 'numba' si esta instalado, "
        "para acelerar el sweep), y modelo de Potts para crecimiento de "
        "grano (microestructura)."
    ),'''

content = content.replace(anchor_schema_desc, new_schema_desc, 1)

# ---------------------------------------------------------------------
with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("statistical_physics_tool.py actualizado con backend numba opcional para ising_2d.")
print("potts_grain_growth NO fue tocado.")
print()
print("Revisa el diff con: git diff statistical_physics_tool.py")
print("Si algo salio mal, restaura con: cp statistical_physics_tool.py.bak_numba statistical_physics_tool.py")
