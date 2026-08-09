"""
test_archaeological_simulation.py

Test de regresion para archaeological_simulation_tool.py. Sin dependencia de
pytest (solo asserts + print), consistente con el resto del repo que valida
por comparacion contra formulas analiticas conocidas en vez de framework de
testing. Correr con: python3 test_archaeological_simulation.py

Requiere Octave instalado (mismo requisito que el tool en produccion).
"""
import sys
from archaeological_simulation_tool import compute_archaeological_simulation

FAILURES = []


def check(label, condition, detail=""):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" -- {detail}" if detail else ""))
    if not condition:
        FAILURES.append(label)


def test_malthusian_growth():
    # amplitude=0 (via validacion interna) debe reproducir el logistico exacto
    r = compute_archaeological_simulation("malthusian_growth", K_amplitude=0.0)
    err = r["validacion_caso_K_constante"]["max_error_vs_logistico_analitico"]
    check("malthusian_growth: K_amplitude=0 ~ logistico analitico", err < 0.5,
          f"error={err}")

    # con amplitude>0 la poblacion debe oscilar (max != min != final necesariamente)
    r2 = compute_archaeological_simulation("malthusian_growth", K_amplitude=20.0)
    check("malthusian_growth: con ciclo climatico hay variacion", r2["poblacion_max"] > r2["poblacion_min"])

    # error no puede crecer sin control (regresion de estabilidad numerica)
    check("malthusian_growth: no diverge", r2["poblacion_max"] < 10 * r2["params"]["K0"],
          f"poblacion_max={r2['poblacion_max']}")


def test_technology_diffusion():
    r = compute_archaeological_simulation("technology_diffusion", p_innovation=0.03,
                                           q_imitation=0.4, M_market=1000.0, t_max=20.0)
    err_rel = r["max_error_vs_analitico"] / r["params"]["M_market"]
    check("technology_diffusion: error relativo vs analitico < 1%", err_rel < 0.01,
          f"err_rel={err_rel:.5f}")

    # t_peak analitico debe caer dentro del rango de t_max simulado si M satura
    t_peak = r["tiempo_adopcion_pico_analitico"]
    check("technology_diffusion: t_peak dentro del horizonte simulado", 0 < t_peak < 20.0,
          f"t_peak={t_peak}")

    # saturacion: con t_max grande el mercado debe casi saturarse
    check("technology_diffusion: mercado casi saturado al final", r["fraccion_mercado_saturado"] > 0.95,
          f"fraccion={r['fraccion_mercado_saturado']}")


def test_trade_network():
    r = compute_archaeological_simulation("trade_network")  # preset default
    val = r["validacion_ley_inversa_distancia"]
    check("trade_network: ley inversa al cuadrado exacta", val["coincide"] is True,
          f"ratio={val['ratio_flujo_simulado_al_duplicar_distancia']}")

    # el asentamiento con mayor poblacion del preset default debe ser el hub
    check("trade_network: hub = asentamiento_mayor (preset default)",
          r["hub_identificado"] == "asentamiento_mayor")

    # caso simetrico: dos nodos iguales a igual distancia de un tercero -> misma centralidad
    settlements = [
        {"name": "centro", "x": 0.0, "y": 0.0, "population": 500.0},
        {"name": "izq", "x": -10.0, "y": 0.0, "population": 100.0},
        {"name": "der", "x": 10.0, "y": 0.0, "population": 100.0},
    ]
    r2 = compute_archaeological_simulation("trade_network", settlements=settlements)
    cent = r2["centralidad_autovector"]
    check("trade_network: simetria exacta entre nodos identicos", abs(cent["izq"] - cent["der"]) < 1e-6,
          f"izq={cent['izq']} der={cent['der']}")


def test_collapse_dynamics():
    # K bajo -> converge (paradoja del enriquecimiento en la direccion "estable")
    r_low = compute_archaeological_simulation("collapse_dynamics", K_capacity=40.0)
    check("collapse_dynamics: K bajo converge (sin ciclo limite)", r_low["ciclo_limite_detectado"] is False)

    eq = r_low["equilibrio_analitico_nullclines"]
    prom = r_low["promedio_temporal_simulado_ultimo_tercio"]
    err_R = abs(eq["R_star"] - prom["R_mean"])
    check("collapse_dynamics: K bajo, R_mean ~ R_star", err_R < 0.5,
          f"R_star={eq['R_star']} R_mean={prom['R_mean']}")

    # K alto (default=200) -> tipicamente cicla (paradoja del enriquecimiento)
    r_high = compute_archaeological_simulation("collapse_dynamics", K_capacity=200.0)
    check("collapse_dynamics: K alto oscila (ciclo limite)", r_high["ciclo_limite_detectado"] is True)

    # promedio temporal debe seguir aproximandose al mismo equilibrio analitico (R*,P* no dependen de la trayectoria)
    eq_h = r_high["equilibrio_analitico_nullclines"]
    check("collapse_dynamics: R_star no depende de K (solo de a,e,h,m)", eq_h["R_star"] == eq["R_star"])


def test_edge_cases():
    r = compute_archaeological_simulation("no_existe")
    check("edge case: mode invalido devuelve error legible", "error" in r, str(r))

    r2 = compute_archaeological_simulation("trade_network", settlements=[{"name": "solo", "x": 0, "y": 0, "population": 100}])
    check("edge case: trade_network con 1 asentamiento devuelve error controlado", "error" in r2, str(r2))


if __name__ == "__main__":
    test_malthusian_growth()
    test_technology_diffusion()
    test_trade_network()
    test_collapse_dynamics()
    test_edge_cases()

    print()
    if FAILURES:
        print(f"{len(FAILURES)} test(s) fallaron: {FAILURES}")
        sys.exit(1)
    else:
        print("Todos los tests pasaron.")
        sys.exit(0)
