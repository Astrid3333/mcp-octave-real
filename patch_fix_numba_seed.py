#!/usr/bin/env python3
"""
patch_fix_numba_seed.py

BUG REAL (no cosmetico): backend='numba' de ising_2d nunca fue
reproducible con la misma seed. np.random.seed(seed) llamado desde Python
normal siembra el generador legacy global de numpy, pero Numba mantiene
un generador INTERNO SEPARADO para las llamadas np.random.* que ocurren
dentro de una funcion @njit -- ese generador interno solo se puede
sembrar llamando a np.random.seed() DESDE ADENTRO de una funcion jiteada.

Confirmado empiricamente: llamar a compute_statistical_physics(...,
backend='numba') tres veces seguidas con la misma seed en el mismo
proceso da tres magnetizaciones distintas.

Esto NO invalida las validaciones fisicas que ya pasaron (magnetizacion
decrece con T, calor especifico razonable) porque esas son propiedades
estadisticas de equilibrio, no dependen de una seed exacta. Pero rompe
cualquier expectativa de reproducibilidad bit-a-bit con backend='numba'
(comparar dos corridas con la misma seed para debug, por ejemplo).

Fix: agregar una funcion @njit _seed_numba_rng(seed) minima, y llamarla
DEMAS de np.random.seed(seed) (que sigue siendo necesaria para el
np.random.choice de la config inicial, que es numpy puro, no numba).

backend='opencl' NO tiene este problema: la aleatoriedad de cada flip
viene de un xorshift determinista implementado en el propio kernel,
sembrado explicitamente con (seed, sweep_id, parity, gid) pasados como
argumentos del kernel -- no depende de ningun estado global de numpy o
numba.

Requisito: correr patch_add_numba_ising.py antes que este (y
opcionalmente patch_add_opencl_ising.py, no lo pisa).
"""

PATH = "statistical_physics_tool.py"
BACKUP = "statistical_physics_tool.py.bak_numbaseed"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

with open(BACKUP, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Backup guardado en {BACKUP}")

# ---------------------------------------------------------------------
# 1) Agregar la funcion de seed jiteada, justo despues de
#    _ising_metropolis_sweep_numba.
# ---------------------------------------------------------------------
anchor_after_numba_sweep = '''            if dE <= 0 or np.random.random() < np.exp(-beta * dE):
                spins[i, j] = -s
        return spins


def ising_2d(n=16, temperatures=None, n_equil=200, n_measure=200, seed=0, backend="numpy"):'''

assert content.count(anchor_after_numba_sweep) == 1, (
    "No se encontro el final de _ising_metropolis_sweep_numba seguido de "
    "ising_2d (se esperaba 1 ocurrencia). Revisar manualmente -- puede ser "
    "que patch_add_numba_ising.py todavia no se haya corrido, o que ya "
    "se haya aplicado este mismo patch antes."
)

new_block = '''            if dE <= 0 or np.random.random() < np.exp(-beta * dE):
                spins[i, j] = -s
        return spins

    @njit(cache=True)
    def _seed_numba_rng(seed):
        """
        Siembra el generador interno de numba usado por np.random.* dentro
        de funciones @njit. IMPORTANTE: llamar a np.random.seed(seed) desde
        Python normal (fuera de una funcion jiteada) NO afecta este estado
        -- numba mantiene su propio generador separado del de numpy. Esta
        funcion es la unica forma correcta de sembrarlo.
        """
        np.random.seed(seed)


def ising_2d(n=16, temperatures=None, n_equil=200, n_measure=200, seed=0, backend="numpy"):'''

content = content.replace(anchor_after_numba_sweep, new_block, 1)

# ---------------------------------------------------------------------
# 2) En la rama backend == "numba" de ising_2d, sembrar tambien el RNG
#    interno de numba (ademas del np.random.seed(seed) que ya estaba,
#    necesario para el np.random.choice de la config inicial).
# ---------------------------------------------------------------------
anchor_branch = '''    if backend == "numba":
        np.random.seed(seed)
        spins = np.random.choice(np.array([-1, 1]), size=(n, n)).astype(np.int64)'''

assert content.count(anchor_branch) == 1, (
    "No se encontro el inicio de la rama backend=='numba' de ising_2d "
    "(se esperaba 1 ocurrencia). Revisar manualmente."
)

new_branch = '''    if backend == "numba":
        np.random.seed(seed)  # siembra numpy puro (usado por np.random.choice abajo)
        _seed_numba_rng(seed)  # siembra el generador interno de numba (usado dentro de los sweeps)
        spins = np.random.choice(np.array([-1, 1]), size=(n, n)).astype(np.int64)'''

content = content.replace(anchor_branch, new_branch, 1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("statistical_physics_tool.py actualizado: backend='numba' ahora es reproducible con la misma seed.")
print()
print("Revisa el diff con: git diff statistical_physics_tool.py")
print("Si algo salio mal, restaura con: cp statistical_physics_tool.py.bak_numbaseed statistical_physics_tool.py")
