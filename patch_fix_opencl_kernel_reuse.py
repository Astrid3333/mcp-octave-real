#!/usr/bin/env python3
"""
patch_fix_opencl_kernel_reuse.py

Arregla el warning de pyopencl:
  RepeatedKernelRetrieval: Kernel 'ising_checkerboard_update' has been
  retrieved more than once. Each retrieval creates a new, independent
  kernel, at possibly considerable expense.

Causa: program.ising_checkerboard_update(...) hace una busqueda por
nombre y crea un objeto Kernel nuevo CADA VEZ que se llama (una vez por
parity, por sweep, por temperatura -- miles de veces en una corrida
tipica). El fix es crear el objeto cl.Kernel una sola vez por contexto
(cacheado, igual que ya se hace con cl.Program) y reusarlo via
set_args() + enqueue_nd_range_kernel().

Solo cambia el camino interno del backend opencl; no cambia resultados
(mismo kernel, mismos argumentos, mismo orden de ejecucion), solo evita
el overhead de recompilar/re-resolver el kernel en cada llamada.

Requisito: correr patch_add_numba_ising.py y patch_add_opencl_ising.py
antes que este.
"""

PATH = "statistical_physics_tool.py"
BACKUP = "statistical_physics_tool.py.bak_openclkernelreuse"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

with open(BACKUP, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Backup guardado en {BACKUP}")

anchor = '''_ISING_CL_PROGRAM_CACHE = {}


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
    return spins_i32.astype(np.int64)'''

assert content.count(anchor) == 1, (
    "No se encontro el bloque de _get_ising_cl_program/_ising_opencl_sweep "
    "con el patron esperado (1 ocurrencia). Revisar manualmente -- puede "
    "ser que patch_add_opencl_ising.py todavia no se haya corrido."
)

new_block = '''_ISING_CL_PROGRAM_CACHE = {}
_ISING_CL_KERNEL_CACHE = {}


def _get_ising_cl_program(ctx):
    key = id(ctx)
    if key not in _ISING_CL_PROGRAM_CACHE:
        import pyopencl as cl
        _ISING_CL_PROGRAM_CACHE[key] = cl.Program(ctx, _ISING_CL_KERNEL_SOURCE).build()
    return _ISING_CL_PROGRAM_CACHE[key]


def _get_ising_cl_kernel(ctx):
    """
    Objeto cl.Kernel cacheado por contexto. Reutilizarlo (en vez de
    resolver program.<nombre_kernel> por atributo en cada llamada) evita
    el warning RepeatedKernelRetrieval de pyopencl y el overhead de crear
    un Kernel nuevo miles de veces por corrida.
    """
    key = id(ctx)
    if key not in _ISING_CL_KERNEL_CACHE:
        import pyopencl as cl
        program = _get_ising_cl_program(ctx)
        _ISING_CL_KERNEL_CACHE[key] = cl.Kernel(program, "ising_checkerboard_update")
    return _ISING_CL_KERNEL_CACHE[key]


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
    kernel = _get_ising_cl_kernel(ctx)

    spins_i32 = np.ascontiguousarray(spins, dtype=np.int32)
    mf = cl.mem_flags
    spins_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=spins_i32)

    global_size = (n * n,)
    for parity in (0, 1):
        kernel.set_args(
            spins_buf, np.int32(n), np.int32(parity), np.float32(beta),
            np.uint32(seed), np.uint32(sweep_id),
        )
        cl.enqueue_nd_range_kernel(queue, kernel, global_size, None)
    cl.enqueue_copy(queue, spins_i32, spins_buf)
    queue.finish()
    return spins_i32.astype(np.int64)'''

content = content.replace(anchor, new_block, 1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("statistical_physics_tool.py actualizado: kernel opencl ahora se cachea y reusa.")
print()
print("Revisa el diff con: git diff statistical_physics_tool.py")
print("Si algo salio mal, restaura con: cp statistical_physics_tool.py.bak_openclkernelreuse statistical_physics_tool.py")
