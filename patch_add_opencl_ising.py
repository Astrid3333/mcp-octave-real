#!/usr/bin/env python3
"""
patch_add_opencl_ising.py

Agrega un backend opcional 'opencl' a ising_2d en statistical_physics_tool.py,
ademas de los backends 'numpy' (default) y 'numba' ya existentes.

IMPORTANTE -- esto NO es un port paralelo literal del sweep secuencial:
_ising_metropolis_sweep (numpy) y _ising_metropolis_sweep_numba (numba)
recorren sitios en orden aleatorio, uno a la vez, y cada flip depende del
estado post-flip del sitio anterior -- es inherentemente serial.

El backend opencl usa el esquema estandar de Metropolis en tablero de
ajedrez (checkerboard / red-black): se separan los sitios en dos colores
segun (i+j)%2; dentro de un mismo color ningun sitio es vecino de otro
(los vecinos de un sitio "negro" son todos "blancos"), asi que todos los
sitios de un color se pueden actualizar en paralelo sin condiciones de
carrera. Un sweep completo = 1 pasada de cada color. Este esquema es un
algoritmo de Metropolis igualmente valido (Gibbs/checkerboard sampling) y
converge a la misma distribucion de equilibrio, pero el camino
sample-by-sample NO coincide con backend='numpy'/'numba' con la misma
seed. Por eso este backend se valida por estadisticas de equilibrio
(magnetizacion, energia, ubicacion del pico de calor especifico), no por
igualdad exacta de resultados.

Requiere pyopencl instalado + un dispositivo OpenCL disponible (GPU o CPU
con ICD configurado). Si no estan disponibles, backend='opencl' levanta
ValueError con mensaje claro -- el import es completamente opcional via
opencl_utils.py (OPENCL_AVAILABLE=False en su ausencia), asi que el
notebook sin GPU nunca se entera de que este codigo existe.

Requisito: correr primero patch_add_numba_ising.py (este patch asume que
el backend numba ya esta aplicado y usa sus mismos anchors de backend).
Tambien requiere que opencl_utils.py este en el mismo directorio que
statistical_physics_tool.py (se importa como modulo hermano).
"""

PATH = "statistical_physics_tool.py"
BACKUP = "statistical_physics_tool.py.bak_opencl"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

with open(BACKUP, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Backup guardado en {BACKUP}")

# ---------------------------------------------------------------------
# 1) Import opcional de opencl_utils + kernel + wrapper de sweep,
#    despues del bloque de import de numba (asume patch_add_numba_ising.py
#    ya aplicado).
# ---------------------------------------------------------------------
anchor_after_numba_import = """try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

STATISTICAL_PHYSICS_TOOL_SCHEMA = {"""

assert content.count(anchor_after_numba_import) == 1, (
    "No se encontro el bloque de import de numba (se esperaba 1 ocurrencia). "
    "Este patch requiere haber corrido patch_add_numba_ising.py primero. "
    "Revisar manualmente."
)

opencl_import_block = '''try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

try:
    from opencl_utils import OPENCL_AVAILABLE, get_opencl_context, opencl_device_info
except ImportError:
    OPENCL_AVAILABLE = False

    def opencl_device_info():
        return None

_ISING_CL_KERNEL_SOURCE = """
inline float _xorshift_float(uint *state) {
    uint x = *state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return (x & 0x00FFFFFF) / (float)0x01000000;  // uniforme en [0,1)
}

__kernel void ising_checkerboard_update(
    __global int *spins,
    const int n,
    const int parity,
    const float beta,
    const uint seed,
    const uint sweep_id)
{
    int gid = get_global_id(0);
    int i = gid / n;
    int j = gid % n;
    if (i >= n) return;
    if ((i + j) % 2 != parity) return;

    int s = spins[i * n + j];
    int up    = spins[((i - 1 + n) % n) * n + j];
    int down  = spins[((i + 1) % n) * n + j];
    int left  = spins[i * n + ((j - 1 + n) % n)];
    int right = spins[i * n + ((j + 1) % n)];
    int neighbors = up + down + left + right;
    int dE = 2 * s * neighbors;

    // seed independiente por celda + sweep + color, no correlacionada
    // entre celdas vecinas (evita artefactos por RNGs correlacionados
    // dentro de la misma pasada de checkerboard)
    uint state = seed ^ ((uint)gid * 2654435761u) ^ ((uint)sweep_id * 40503u)
                 ^ ((uint)parity * 97u);
    _xorshift_float(&state);
    _xorshift_float(&state);
    float r = _xorshift_float(&state);

    if (dE <= 0 || r < exp(-beta * (float)dE)) {
        spins[i * n + j] = -s;
    }
}
"""

_ISING_CL_PROGRAM_CACHE = {}


def _get_ising_cl_program(ctx):
    key = id(ctx)
    if key not in _ISING_CL_PROGRAM_CACHE:
        import pyopencl as cl
        _ISING_CL_PROGRAM_CACHE[key] = cl.Program(ctx, _ISING_CL_KERNEL_SOURCE).build()
    return _ISING_CL_PROGRAM_CACHE[key]


def _ising_opencl_sweep(spins, beta, n, seed, sweep_id):
    """
    Un sweep completo (ambos colores del tablero de ajedrez) via kernel
    OpenCL. Ver docstring del modulo (o del patch que agrego esto) para la
    diferencia algoritmica con los backends numpy/numba -- no son
    trayectoria-equivalentes, solo equilibrio-equivalentes.
    """
    import pyopencl as cl
    import numpy as np

    ctx, queue = get_opencl_context()
    program = _get_ising_cl_program(ctx)

    spins_i32 = np.ascontiguousarray(spins, dtype=np.int32)
    mf = cl.mem_flags
    spins_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=spins_i32)

    global_size = (n * n,)
    for parity in (0, 1):
        program.ising_checkerboard_update(
            queue, global_size, None,
            spins_buf, np.int32(n), np.int32(parity), np.float32(beta),
            np.uint32(seed), np.uint32(sweep_id),
        )
    cl.enqueue_copy(queue, spins_i32, spins_buf)
    queue.finish()
    return spins_i32.astype(np.int64)


STATISTICAL_PHYSICS_TOOL_SCHEMA = {'''

content = content.replace(anchor_after_numba_import, opencl_import_block, 1)

# ---------------------------------------------------------------------
# 2) Firma de ising_2d: agregar 'opencl' a los backends validos.
# ---------------------------------------------------------------------
anchor_signature = 'def ising_2d(n=16, temperatures=None, n_equil=200, n_measure=200, seed=0, backend="numpy"):'
assert content.count(anchor_signature) == 1, (
    "No se encontro la firma de ising_2d con backend numba ya aplicado "
    "(se esperaba 1 ocurrencia). Revisar manualmente."
)
# La firma no cambia (backend sigue siendo un string libre), solo cambia
# la validacion mas abajo -- no se necesita reemplazo aca.

anchor_validation = '''    if backend not in ("numpy", "numba"):
        raise ValueError(f"backend desconocido: {backend!r}. Use 'numpy' o 'numba'")
    if backend == "numba" and not NUMBA_AVAILABLE:
        raise ValueError(
            "backend='numba' pedido pero numba no esta instalado en este entorno. "
            "Instalar con: pip install numba --break-system-packages, "
            "o usar backend='numpy' (default)."
        )'''

assert content.count(anchor_validation) == 1, (
    "No se encontro el bloque de validacion de backend (numpy/numba) "
    "(se esperaba 1 ocurrencia). Revisar manualmente."
)

new_validation = '''    if backend not in ("numpy", "numba", "opencl"):
        raise ValueError(f"backend desconocido: {backend!r}. Use 'numpy', 'numba' u 'opencl'")
    if backend == "numba" and not NUMBA_AVAILABLE:
        raise ValueError(
            "backend='numba' pedido pero numba no esta instalado en este entorno. "
            "Instalar con: pip install numba --break-system-packages, "
            "o usar backend='numpy' (default)."
        )
    if backend == "opencl" and not OPENCL_AVAILABLE:
        raise ValueError(
            "backend='opencl' pedido pero no hay pyopencl + dispositivo OpenCL "
            "disponible en este entorno (no instalado, sin GPU, o sin ICD "
            "configurado). Instalar con: pip install pyopencl --break-system-packages "
            "(requiere ademas los drivers/ICD del fabricante de la GPU), "
            "o usar backend='numpy' (default) / 'numba'."
        )'''

content = content.replace(anchor_validation, new_validation, 1)

# ---------------------------------------------------------------------
# 3) Cuerpo de ising_2d: agregar la rama backend == "opencl", como
#    tercer camino junto a "numba" y numpy (else).
# ---------------------------------------------------------------------
anchor_numba_branch_end = '''            results.append({
                "T": T,
                "magnetization": float(np.mean(mags)),
                "energy_per_site": float(np.mean(energies)),
                "specific_heat": float(specific_heat),
            })
    else:
        rng = np.random.default_rng(seed)'''

assert content.count(anchor_numba_branch_end) == 1, (
    "No se encontro el limite entre la rama numba y la rama numpy (else) "
    "(se esperaba 1 ocurrencia). Revisar manualmente."
)

new_branch_block = '''            results.append({
                "T": T,
                "magnetization": float(np.mean(mags)),
                "energy_per_site": float(np.mean(energies)),
                "specific_heat": float(specific_heat),
            })
    elif backend == "opencl":
        np.random.seed(seed)
        spins = np.random.choice(np.array([-1, 1]), size=(n, n)).astype(np.int64)
        sweep_counter = 0
        for T in temperatures:
            beta = 1.0 / T
            for _ in range(n_equil):
                spins = _ising_opencl_sweep(spins, beta, n, seed, sweep_counter)
                sweep_counter += 1
            mags, energies = [], []
            for _ in range(n_measure):
                spins = _ising_opencl_sweep(spins, beta, n, seed, sweep_counter)
                sweep_counter += 1
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
        rng = np.random.default_rng(seed)'''

content = content.replace(anchor_numba_branch_end, new_branch_block, 1)

# ---------------------------------------------------------------------
# 4) Return dict: agregar opencl_device cuando backend == "opencl"
#    (informativo, None en cualquier otro backend).
# ---------------------------------------------------------------------
anchor_return = '''    T_peak = max(results, key=lambda r: r["specific_heat"])["T"]
    return {
        "mode": "ising_2d",
        "n": n,
        "backend": backend,
        "results": results,
        "T_critical_estimate": T_peak,
        "T_critical_onsager": 2.0 / np.log(1 + np.sqrt(2)),
    }'''

assert content.count(anchor_return) == 1, (
    "No se encontro el return final de ising_2d (se esperaba 1 ocurrencia). "
    "Revisar manualmente."
)

new_return = '''    T_peak = max(results, key=lambda r: r["specific_heat"])["T"]
    return {
        "mode": "ising_2d",
        "n": n,
        "backend": backend,
        "opencl_device": opencl_device_info() if backend == "opencl" else None,
        "results": results,
        "T_critical_estimate": T_peak,
        "T_critical_onsager": 2.0 / np.log(1 + np.sqrt(2)),
    }'''

content = content.replace(anchor_return, new_return, 1)

# ---------------------------------------------------------------------
# 5) Schema: mencionar el backend opencl.
# ---------------------------------------------------------------------
anchor_schema_desc = '''    "description": (
        "Fisica estadistica: modelo de Ising 2D via Monte Carlo Metropolis "
        "(magnetizacion, energia, calor especifico, transicion de fase; "
        "params.backend='numpy' (default) o 'numba' si esta instalado, "
        "para acelerar el sweep), y modelo de Potts para crecimiento de "
        "grano (microestructura)."
    ),'''

assert content.count(anchor_schema_desc) == 1, (
    "No se encontro la descripcion del schema (se esperaba 1 ocurrencia). "
    "Revisar manualmente."
)

new_schema_desc = '''    "description": (
        "Fisica estadistica: modelo de Ising 2D via Monte Carlo Metropolis "
        "(magnetizacion, energia, calor especifico, transicion de fase; "
        "params.backend='numpy' (default), 'numba' si esta instalado, u "
        "'opencl' si hay pyopencl+GPU (usa checkerboard/red-black paralelo, "
        "equilibrio-equivalente pero no trayectoria-equivalente a los otros "
        "backends), para acelerar el sweep), y modelo de Potts para "
        "crecimiento de grano (microestructura)."
    ),'''

content = content.replace(anchor_schema_desc, new_schema_desc, 1)

# ---------------------------------------------------------------------
with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("statistical_physics_tool.py actualizado con backend opcional 'opencl' para ising_2d.")
print("potts_grain_growth sigue sin tocar.")
print()
print("IMPORTANTE: este backend usa checkerboard (red-black) Metropolis, no es")
print("trayectoria-equivalente a numpy/numba con la misma seed -- valida por")
print("estadisticas de equilibrio (magnetizacion/energia/pico de calor especifico).")
print()
print("Revisa el diff con: git diff statistical_physics_tool.py")
print("Si algo salio mal, restaura con: cp statistical_physics_tool.py.bak_opencl statistical_physics_tool.py")
