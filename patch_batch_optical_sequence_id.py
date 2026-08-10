"""
patch_batch_optical_sequence_id.py

Agrega batch_generate y batch_compare a optical_sequence_id_tool.py, y
registra el modo en el tool de server.py (docstring). Correr desde la raiz
del repo (~/mcp-octave-real):

    python3 patch_batch_optical_sequence_id.py

Es idempotente: si detecta que ya esta parcheado, no toca nada y avisa.
"""

import re
import sys

TARGET_TOOL = "optical_sequence_id_tool.py"
TARGET_SERVER = "server.py"

# ---------------------------------------------------------------------------
# 1) Insertar funciones batch en optical_sequence_id_tool.py, justo antes
#    del bloque de controles sinteticos.
# ---------------------------------------------------------------------------
ANCHOR = "# Control sintetico A: conservacion de energia (teorema de Parseval)"

BATCH_CODE = '''# ---------------------------------------------------------------------------
# Batch: parsing de FASTA / listas de secuencias
# ---------------------------------------------------------------------------
def _parse_batch_input(sequences=None, fasta=None) -> list[tuple[str, str]]:
    """
    Devuelve una lista de tuplas (id, seq) a partir de:
      - `sequences`: lista de strings (secuencia cruda, se autogenera un id
        "seq_1", "seq_2", ...) o lista de dicts {"id": ..., "seq": ...}
      - `fasta`: texto crudo en formato FASTA (">id\\nSEQ\\n...", multilinea
        por secuencia soportado)
    Si se pasan ambos, se concatenan (fasta primero, despues sequences).
    """
    items: list[tuple[str, str]] = []

    if fasta:
        current_id = None
        current_seq: list[str] = []
        for raw_line in fasta.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current_id is not None:
                    items.append((current_id, "".join(current_seq)))
                current_id = line[1:].strip() or f"seq_{len(items) + 1}"
                current_seq = []
            else:
                current_seq.append(line)
        if current_id is not None:
            items.append((current_id, "".join(current_seq)))

    if sequences:
        for s in sequences:
            if isinstance(s, dict):
                seq = s.get("seq", "")
                sid = s.get("id") or f"seq_{len(items) + 1}"
            else:
                seq = s
                sid = f"seq_{len(items) + 1}"
            items.append((sid, seq))

    if not items:
        raise ValueError(
            "batch requiere al menos uno de: `sequences` (lista de strings o "
            "de {'id':..,'seq':..}), `fasta` (texto FASTA crudo)"
        )
    return items


def _uniform_grid_size(apertures: list[np.ndarray], output_size: int) -> int:
    """
    Grilla de FFT comun para TODO el lote: el maximo entre output_size y la
    dimension mas grande entre todas las aperturas del lote. Necesario para
    que las intensidades resultantes tengan la misma forma y sean
    comparables (matriz de correlacion, ranking, etc.) -- si cada secuencia
    usara su propia grilla minima, secuencias de distinto largo caerian en
    grillas de tamano distinto y no se podrian comparar pixel a pixel.
    """
    max_dim = output_size
    for ap in apertures:
        max_dim = max(max_dim, ap.shape[0], ap.shape[1])
    return max_dim


# ---------------------------------------------------------------------------
# Modo: batch_generate
# ---------------------------------------------------------------------------
def _mode_batch_generate(mapping: str = "slit_1d", diffraction: str = "fraunhofer",
                          sequences=None, fasta=None, **params) -> dict:
    if mapping not in _VALID_MAPPINGS:
        raise ValueError(f"mapping '{mapping}' no reconocido. Validos: {_VALID_MAPPINGS}")

    items = _parse_batch_input(sequences, fasta)
    output_size = int(params.get("output_size", 128))
    hash_precision = int(params.get("hash_precision", 6))
    top_k_peaks = int(params.get("top_k_peaks", 5))
    include_pattern = bool(params.get("include_pattern", False))

    # primera pasada: transmitancia + apertura por secuencia, para poder
    # fijar una grilla comun antes de difractar
    apertures = []
    for sid, seq in items:
        t = _get_transmittance_from_seq(seq)
        apertures.append(_reshape_aperture(t, mapping))

    grid = _uniform_grid_size(apertures, output_size)
    diffract_params = dict(params)
    diffract_params["output_size"] = grid

    results = []
    for (sid, seq), aperture2d in zip(items, apertures):
        intensity = _diffract(aperture2d, diffraction, **diffract_params)
        entry = {
            "id": sid,
            "sequence_length": len(seq),
            "id_hash": _hash_intensity(intensity, hash_precision),
            "signature": _vector_signature(intensity, top_k_peaks),
        }
        if include_pattern:
            entry["intensity_pattern"] = intensity.tolist()
        results.append(entry)

    return {
        "mode": "batch_generate",
        "mapping": mapping,
        "diffraction": diffraction,
        "grid_size": grid,
        "count": len(results),
        "results": results,
    }


# ---------------------------------------------------------------------------
# Modo: batch_compare
# ---------------------------------------------------------------------------
def _mode_batch_compare(mapping: str = "slit_1d", diffraction: str = "fraunhofer",
                         sequences=None, fasta=None, query_seq=None,
                         query_id: str = "query", **params) -> dict:
    if mapping not in _VALID_MAPPINGS:
        raise ValueError(f"mapping '{mapping}' no reconocido. Validos: {_VALID_MAPPINGS}")

    items = _parse_batch_input(sequences, fasta)
    output_size = int(params.get("output_size", 128))

    all_items = list(items)
    if query_seq is not None:
        # la query va primero (indice 0) para poder aislar su fila despues
        all_items = [(query_id, query_seq)] + all_items

    apertures = []
    for sid, seq in all_items:
        t = _get_transmittance_from_seq(seq)
        apertures.append(_reshape_aperture(t, mapping))

    grid = _uniform_grid_size(apertures, output_size)
    diffract_params = dict(params)
    diffract_params["output_size"] = grid

    intensities = [
        _diffract(ap, diffraction, **diffract_params) for ap in apertures
    ]
    ids = [sid for sid, _ in all_items]

    # matriz de correlacion vectorizada: una sola llamada a np.corrcoef sobre
    # todos los patrones apilados, en vez de comparar par a par (esto ultimo
    # seria O(K^2) llamadas a corrcoef individuales, mucho mas lento para
    # lotes grandes).
    flat = np.stack([iv.ravel() for iv in intensities])  # (K, P)
    stds = flat.std(axis=1)
    with np.errstate(invalid="ignore"):
        corr_matrix = np.corrcoef(flat)  # (K, K)

    # np.corrcoef da NaN para filas/columnas con std=0 (patron constante,
    # deberia ser raro pero puede pasar con secuencias de largo 1). Se
    # resuelve igual que en mode="compare": 1.0 si son identicas, 0.0 si no.
    zero_std = np.where(stds == 0)[0]
    for i in zero_std:
        for j in range(len(intensities)):
            same = np.allclose(flat[i], flat[j])
            corr_matrix[i, j] = 1.0 if same else 0.0
            corr_matrix[j, i] = corr_matrix[i, j]

    if query_seq is not None:
        query_row = corr_matrix[0, 1:].tolist()
        ranked = sorted(
            zip(ids[1:], query_row), key=lambda kv: kv[1], reverse=True
        )
        return {
            "mode": "batch_compare",
            "mapping": mapping,
            "diffraction": diffraction,
            "grid_size": grid,
            "query_id": query_id,
            "ranked_matches": [
                {"id": sid, "pattern_correlation": corr} for sid, corr in ranked
            ],
        }

    return {
        "mode": "batch_compare",
        "mapping": mapping,
        "diffraction": diffraction,
        "grid_size": grid,
        "ids": ids,
        "correlation_matrix": corr_matrix.tolist(),
    }


'''

DISPATCH_ANCHOR = '        if mode == "validate_energy_conservation":'
DISPATCH_CODE = '''        if mode == "batch_generate":
            mapping = params.pop("mapping", "slit_1d")
            diffraction = params.pop("diffraction", "fraunhofer")
            sequences = params.pop("sequences", None)
            fasta = params.pop("fasta", None)
            return _mode_batch_generate(mapping, diffraction, sequences=sequences,
                                         fasta=fasta, **params)

        if mode == "batch_compare":
            mapping = params.pop("mapping", "slit_1d")
            diffraction = params.pop("diffraction", "fraunhofer")
            sequences = params.pop("sequences", None)
            fasta = params.pop("fasta", None)
            query_seq = params.pop("query_seq", None)
            query_id = params.pop("query_id", "query")
            return _mode_batch_compare(mapping, diffraction, sequences=sequences,
                                        fasta=fasta, query_seq=query_seq,
                                        query_id=query_id, **params)

'''

ERROR_MSG_OLD = (
    '                f"mode \'{mode}\' no reconocido. Modos validos: "\n'
    '                "generate, compare, validate_energy_conservation, "\n'
    '                "validate_translation_invariance, validate_all"\n'
)
ERROR_MSG_NEW = (
    '                f"mode \'{mode}\' no reconocido. Modos validos: "\n'
    '                "generate, compare, batch_generate, batch_compare, "\n'
    '                "validate_energy_conservation, validate_translation_invariance, "\n'
    '                "validate_all"\n'
)


def patch_tool_file():
    with open(TARGET_TOOL, "r", encoding="utf-8") as f:
        src = f.read()

    if "_mode_batch_generate" in src:
        print(f"[skip] {TARGET_TOOL} ya tiene batch_generate/batch_compare, no se toca.")
        return False

    if ANCHOR not in src:
        print(f"[ERROR] no encontre el ancla de insercion en {TARGET_TOOL}. Abortando sin tocar nada.")
        sys.exit(1)

    src = src.replace(ANCHOR, BATCH_CODE + ANCHOR, 1)

    if DISPATCH_ANCHOR not in src:
        print(f"[ERROR] no encontre el ancla de dispatch en {TARGET_TOOL}. Abortando sin tocar nada.")
        sys.exit(1)
    src = src.replace(DISPATCH_ANCHOR, DISPATCH_CODE + DISPATCH_ANCHOR, 1)

    if ERROR_MSG_OLD in src:
        src = src.replace(ERROR_MSG_OLD, ERROR_MSG_NEW, 1)
    else:
        print("[warn] no encontre el mensaje de error exacto para actualizar la lista de modos validos (no critico).")

    with open(TARGET_TOOL, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"[ok] {TARGET_TOOL} parcheado.")
    return True


def patch_server_file():
    with open(TARGET_SERVER, "r", encoding="utf-8") as f:
        src = f.read()

    marker = 'def optical_sequence_id_tool(mode: str = "generate", params: dict = None) -> dict:'
    if marker not in src:
        print(f"[ERROR] no encontre la funcion optical_sequence_id_tool en {TARGET_SERVER}. Abortando sin tocar nada.")
        sys.exit(1)

    if "batch_generate" in src:
        print(f"[skip] {TARGET_SERVER} ya menciona batch_generate en la docstring, no se toca.")
        return False

    old_docstring_fragment = "mode='compare': compara dos secuencias (params: seq_a, seq_b, + mismos params fisicos) devolviendo pattern_correlation (correlacion pixel a pixel, discrimina bien) y ambos hashes."
    new_docstring_fragment = (
        old_docstring_fragment
        + " mode='batch_generate': genera ids para muchas secuencias de una "
        "(params: sequences=lista de strings o de {id,seq}, y/o fasta=texto FASTA, "
        "+ mismos params fisicos; todas comparten una misma grilla de FFT). "
        "mode='batch_compare': matriz de correlacion NxN entre todo el lote, o "
        "ranking contra una sola secuencia si se pasa query_seq (params: sequences "
        "y/o fasta, query_seq opcional, query_id opcional)."
    )

    if old_docstring_fragment not in src:
        print(f"[ERROR] no encontre el fragmento de docstring esperado en {TARGET_SERVER}. Abortando sin tocar nada.")
        sys.exit(1)

    src = src.replace(old_docstring_fragment, new_docstring_fragment, 1)

    with open(TARGET_SERVER, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"[ok] {TARGET_SERVER} parcheado (docstring actualizada).")
    return True


if __name__ == "__main__":
    changed_tool = patch_tool_file()
    changed_server = patch_server_file()
    if changed_tool or changed_server:
        print("\nListo. Ahora corre:")
        print("  python3 -c \"import server\"   # smoke test de import")
        print("  python3 -m py_compile optical_sequence_id_tool.py server.py")
    else:
        print("\nNada que hacer, ya estaba todo parcheado.")
