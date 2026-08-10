# Tools disponibles en octave-mcp

Generado automaticamente desde `server.py` el 2026-08-10 02:22 UTC por `generate_readme_tools.py`. **No editar a mano** -- correr el generador de nuevo despues de agregar o modificar un tool.

Total: 97 tools expuestos via `@mcp.tool()`.

---

## `abstract_algebra`

```python
abstract_algebra(mode: str = 'validate', params: dict = None)
```

Algebra abstracta sobre estructuras finitas chicas (orden<=8): tablas de Cayley, verificacion de axiomas de grupo/anillo/cuerpo, isomorfismos por fuerza bruta.

<sub>definido en `server.py:830`</sub>

---

## `ancestral_octave`

```python
ancestral_octave(preset: str, params: dict = None, extra_octave: str = None)
```

Corre metodos ancestrales (suanpan_add, chinese_remainder, vedic_multiply, archimedes_pi, quipu_encode) como funciones Octave NATIVAS via ancestral.m, en el mismo motor que octave_run. extra_octave permite componer con otro codigo Octave en la misma sesion.

<sub>definido en `server.py:329`</sub>

---

## `ancient_calculator`

```python
ancient_calculator(preset: str, params: dict = None)
```

Simula calculadoras historicas reales operando sus cuentas/fichas: suanpan, soroban, roman_hand_abacus, yupana_depasquale (hipotesis en disputa academica, ver advertencia en la respuesta).

<sub>definido en `server.py:322`</sub>

---

## `antibiotic_diffusion`

```python
antibiotic_diffusion(mode: str = 'validate', C0: float = 1000.0, a: float = 0.3, D: float = 5e-06, MIC: float = 1.0, t: float = 57600.0)
```

Bioensayo de difusion en disco tipo Kirby-Bauer: difusion radial 2D exacta (Carslaw & Jaeger, disco de concentracion uniforme C0 en agar homogeneo) mas la aproximacion clasica de fuente puntual de Cooper. Liberacion instantanea, sin degradacion ni consumo bacteriano -- estimacion de ordenes de magnitud, no reemplaza ensayo real. Modes: zone_prediction (radio/diametro de halo a un C0 y tiempo de incubacion dados, exacto vs aproximacion puntual), calibration_curve (barre varias dosis, ajusta diametro^2 vs ln(C0) -- ley lineal de Cooper), validate (4 chequeos: conservacion de masa, limite de fuente puntual, limite de tiempo temprano, ley de Cooper).

<sub>definido en `server.py:550`</sub>

---

## `archaeoastronomy`

```python
archaeoastronomy(mode: str, params: dict = None)
```

Calculos astronomicos para arqueoastronomia (algoritmos de Meeus): posicion solar/lunar, equinoccios/solsticios, verificacion de alineamientos arqueologicos.

<sub>definido en `server.py:815`</sub>

---

## `archaeological_simulation`

```python
archaeological_simulation(mode: str = 'malthusian_growth', r: float = 0.5, K0: float = 100.0, K_amplitude: float = 20.0, K_period: float = 20.0, x0: float = 10.0, t_max: float = 100.0, n_points: int = 60, p_innovation: float = 0.03, q_imitation: float = 0.4, M_market: float = 1000.0, settlements: list = None, gravity_exponent: float = 2.0, G_constant: float = 1.0, K_capacity: float = 200.0, a_attack: float = 0.02, h_handling: float = 0.4, e_efficiency: float = 0.6, m_mortality: float = 0.3, R0: float = 50.0, P0: float = 10.0)
```

Simulacion de dinamicas socio-demograficas arqueologicas: malthusian_growth (crecimiento logistico con capacidad de carga variable por ciclos climaticos), technology_diffusion (modelo de Bass de adopcion de innovaciones, solucion analitica cerrada), trade_network (modelo gravitacional de rutas comerciales entre asentamientos, identifica el hub por centralidad de autovector), collapse_dynamics (ciclo auge-colapso poblacion/recursos tipo Rosenzweig-MacArthur, analogo a los secular cycles de Turchin).

<sub>definido en `server.py:594`</sub>

---

## `braid_group`

```python
braid_group(mode: str = 'verify_braid_relation', sequence: str = '1,2,1', initial_state: list = None)
```

Grupos de trenzas y anyones de Fibonacci: verify_braid_relation (unitariedad + relacion de Yang-Baxter), apply_braid_sequence (aplica una secuencia de trenzas a un estado inicial, preserva la norma). Basado en Bonesteel et al 2005. Conexion con computacion cuantica topologica y con persistent_homology_tool / linear_algebra_tool.

<sub>definido en `server.py:483`</sub>

---

## `budgeting_tool`

```python
budgeting_tool(mode: str, params: dict = None)
```

Presupuestos de construccion: costo directo, analisis de precio unitario (APU), aplicacion de gastos generales/utilidad/contingencia/impuesto, escalamiento por inflacion, resumen por capitulos.

<sub>definido en `server.py:838`</sub>

---

## `cfd_tool`

```python
cfd_tool(mode: str, params: dict = None)
```

CFD 2D laminar (sin modelos de turbulencia). mode='poiseuille_flow': flujo de Stokes entre placas paralelas, validado contra la solucion analitica de Hagen-Poiseuille. mode='lid_driven_cavity': Navier-Stokes 2D via formulacion vorticidad-funcion de corriente, cavidad con tapa movil, validado contra el benchmark de Ghia, Ghia & Shin (1982) en Re=100.

<sub>definido en `server.py:911`</sub>

---

## `chemometrics`

```python
chemometrics(mode: str, params: dict = None)
```

Quimiometria: calibracion PLS y PCR, diseno de experimentos (factorial completo, Box-Behnken, hipercubo latino), validacion de recuperacion.

<sub>definido en `server.py:775`</sub>

---

## `clustering_tool`

```python
clustering_tool(mode: str, params: dict = None)
```

Fase C de estadistica: clustering y reduccion de dimensionalidad. mode='kmeans': K-means con inicializacion k-means++, devuelve labels, centroides, inertia, silhouette_score y davies_bouldin_score (params: X, k, n_init, max_iter, random_state). mode='hierarchical': clustering jerarquico via scipy (linkage single/complete/average), devuelve matriz de linkage y orden de dendrograma para math_visualization_tool; si se pasa n_clusters tambien devuelve la asignacion de clusters por corte (params: X, linkage, n_clusters). mode='pca_extended': extiende el PCA de linear_algebra_tool con biplot completo — scores, loadings y contribucion porcentual de cada variable por componente (params: X, n_components, standardize, feature_names). Validado cruzado contra sklearn (KMeans, AgglomerativeClustering via adjusted_rand_score, PCA).

<sub>definido en `server.py:929`</sub>

---

## `composite_homogenization_tool`

```python
composite_homogenization_tool(mode: str, params: dict = None)
```

Propiedades efectivas de un material compuesto de 2 fases via reglas de mezcla Voigt (cota superior, iso-deformacion) y Reuss (cota inferior, iso-esfuerzo), derivadas simbolicamente con sympy. mode='elastic_modulus' o 'thermal_conductivity'. params: f1 (fraccion de volumen de fase 1), P1, P2 (propiedad de cada fase).

<sub>definido en `server.py:899`</sub>

---

## `compute_bifurcation`

```python
compute_bifurcation(map_name: str = 'logistic', custom_expr: Optional[str] = None, r_range: Optional[list] = None, x0: Optional[float] = None, n_r_values: int = 300, n_transient: int = 500, n_keep: int = 40, stability_check_rs: Optional[list] = None)
```

Genera un diagrama de bifurcacion para un mapa iterativo 1D (x_next = f(x,r)), barriendo un rango de r y guardando los puntos del atractor tras un transitorio. Presets: logistic, sine, cubic, tent, o custom. Opcionalmente analiza estabilidad (via derivada) en valores de r especificos.

<sub>definido en `server.py:191`</sub>

---

## `compute_gradient_hessian`

```python
compute_gradient_hessian(expression: str, variables: str, order: int = 1)
```

Deriva simbolicamente (via sympy) el gradiente y, si order>=2, la matriz Hessiana de una expresion multivariable.

<sub>definido en `server.py:690`</sub>

---

## `compute_jacobian`

```python
compute_jacobian(expressions: str, variables: str)
```

Calcula la matriz Jacobiana simbolica de un sistema de 'expressions' (separadas por ;) respecto a 'variables'.

<sub>definido en `server.py:695`</sub>

---

## `compute_lyapunov`

```python
compute_lyapunov(system: str = 'chen_lee', custom_equations: Optional[str] = None, custom_params: Optional[dict] = None, y0: Optional[list] = None, dt: Optional[float] = None, n_steps: int = 20000, d0: float = 1e-08, run_id: Optional[str] = None, save_trajectory_every: int = 10)
```

Calcula el exponente de Lyapunov maximo (lambda1) de un sistema dinamico (presets: chen_lee, burke_shaw, lorenz, rossler, o ecuaciones custom) para cuantificar caos. lambda1>0 confirma comportamiento caotico. Si se indica run_id, guarda la trayectoria completa en el workspace (util para graficar el atractor despues con plot_tool).

<sub>definido en `server.py:140`</sub>

---

## `construction_scheduling_tool`

```python
construction_scheduling_tool(mode: str, params: dict = None)
```

Planificacion de obra: ruta critica (CPM), carga diaria de recursos, compresion de cronograma (crashing) por menor pendiente de costo.

<sub>definido en `server.py:843`</sub>

---

## `control_theory`

```python
control_theory(mode: str, params: dict = None)
```

Teoria de control: respuesta PID a escalon, criterio de Routh-Hurwitz, lugar de raices, control caotico OGY.

<sub>definido en `server.py:795`</sub>

---

## `cross_validation`

```python
cross_validation(system: str = 'chen_lee', params: dict = None, t_max: float = 2000, n_steps: int = 200000, transient_frac: float = 0.1, tolerance: float = 0.15)
```

Valida un resultado de dimension fractal corriendo el mismo sistema dinamico con dos motores numericos independientes (Octave ode45 y scipy RK45). Devuelve ambas dimensiones, la diferencia relativa, y un flag cross_validated. Sistemas disponibles: chen_lee.

<sub>definido en `server.py:383`</sub>

---

## `earthworks_tool`

```python
earthworks_tool(operation: str, params: dict = None)
```

Movimiento de tierras: volumen entre secciones transversales, corte/relleno sobre grilla, esponjamiento/contraccion, diagrama de masas.

<sub>definido en `server.py:848`</sub>

---

## `econometrics`

```python
econometrics(mode: str, params: dict = None)
```

Econometria: test ADF, forecast ARIMA, ajuste GARCH(1,1), cointegracion Engle-Granger, efectos fijos de panel, IV/2SLS, causalidad de Granger.

<sub>definido en `server.py:780`</sub>

---

## `entropy_structure`

```python
entropy_structure(preset: str = 'random_iid', sequence: list = None, alphabet_size: int = 5, n_symbols: int = 5000, seed: int = 1)
```

Calcula entropia de orden 0 y entropia condicional de orden 1 sobre una secuencia de simbolos, para evaluar evidencia de estructura combinatoria (compatible con codificacion tipo-lenguaje) vs. conteo simple/tally marks. Presets sinteticos validados (random_iid, markov_structured) o custom via 'sequence' con datos reales (khipu, yupana, corpus sin descifrar, etc).

<sub>definido en `server.py:392`</sub>

---

## `enzyme_kinetics`

```python
enzyme_kinetics(mode: str = 'compare', k1: float = 100.0, km1: float = 10.0, k2: float = 5.0, E0: float = 1.0, S0: float = 100.0, t_max: float = 5.0, n_points: int = 50)
```

Cinetica enzimatica: full_kinetics (E+S<->ES->E+P completo), michaelis_menten (aproximacion QSSA), compare (valida cuando la aproximacion es correcta, E0<<S0).

<sub>definido en `server.py:511`</sub>

---

## `ethnomath`

```python
ethnomath(preset: str, params: dict = None)
```

Algoritmos matematicos historicos: maya_long_count, chinese_remainder, vedic_multiply, quipu_encode, greek_archimedes_pi, japanese_enri_pi.

<sub>definido en `server.py:309`</sub>

---

## `ethnomath2`

```python
ethnomath2(preset: str, params: dict = None)
```

Segunda tanda de algoritmos matematicos historicos: egyptian_duplation, persian_khwarizmi, persian_alkashi_sin1, russian_peasant, ottoman_taqi_al_din, norse_rune_calendar, southeast_asian_metonic.

<sub>definido en `server.py:315`</sub>

---

## `financial_math`

```python
financial_math(mode: str, params: dict = None)
```

Matematica financiera: Black-Scholes, griegas de opciones, VaR (parametrico/historico), valuacion de anualidades y bonos, riesgo catastrofico.

<sub>definido en `server.py:740`</sub>

---

## `finite_element_tool`

```python
finite_element_tool(mode: str, params: dict = None)
```

Metodo de elementos finitos: barra axial 1D, viga en voladizo Euler-Bernoulli, cercha plana 2D.

<sub>definido en `server.py:853`</sub>

---

## `fractal_dimension`

```python
fractal_dimension(preset: str = 'sierpinski_triangle', points: list = None, n_points: int = 60000, order: int = 6, n_scales: int = 14, eps_min_frac: float = 0.001, eps_max_frac: float = 0.3, chen_lee_params: dict = None)
```

Dimension fractal por box-counting. Presets: sierpinski_triangle, koch_curve, cantor_set (con dimension analitica de referencia), chen_lee_attractor (integra el sistema caotico en Octave), o custom via 'points'.

<sub>definido en `server.py:289`</sub>

---

## `game_theory`

```python
game_theory(mode: str, params: dict = None)
```

Teoria de juegos: equilibrio de Nash, eliminacion de estrategias dominadas, valor de juegos de suma cero, valor de Shapley, nucleo cooperativo, dinamica evolutiva.

<sub>definido en `server.py:745`</sub>

---

## `glm_tool`

```python
glm_tool(mode: str, params: dict = None)
```

Fase B de estadistica: modelos lineales generalizados y regresion regularizada. mode='logistic_regression': regresion logistica binaria via IRLS, devuelve coeficientes, odds ratios, errores estandar y p-values de Wald. mode='poisson_regression': GLM de conteos (link log) via IRLS, devuelve incidence rate ratios. mode='ridge_lasso': Ridge (solucion cerrada) o Lasso (coordinate descent), con seleccion de lambda via validacion cruzada k-fold; params incluye method='ridge'|'lasso'. Validado cruzado contra sklearn.

<sub>definido en `server.py:923`</sub>

---

## `graph_algorithms`

```python
graph_algorithms(preset: str = 'small_weighted', edges: list = None, directed: bool = False, operation: str = 'all', source = None)
```

Corre algoritmos clasicos de grafos: Dijkstra, MST (Kruskal), deteccion de ciclos. Presets: small_weighted, disconnected, with_cycle, o custom via 'edges' [[u,v,peso],...].

<sub>definido en `server.py:238`</sub>

---

## `hilbert_transform`

```python
hilbert_transform(preset: str = 'am_chirp', signal: Optional[list] = None, fs: float = 1000.0, duration: float = 1.0, detrend: bool = True, bandpass: Optional[list] = None, n_output_points: int = 200)
```

Calcula la transformada de Hilbert de una serie temporal no estacionaria y extrae envolvente (amplitud instantanea), fase instantanea y frecuencia instantanea via la senal analitica. Incluye presets sinteticos (am_chirp, fm_chirp, noisy_am) para validar el metodo, o acepta una senal custom (ej. mediciones de campo electrico atmosferico) con bandpass opcional [f_low, f_high] en Hz.

<sub>definido en `server.py:217`</sub>

---

## `historian`

```python
historian(mode: str = 'validate', analysis_type: str = 'inflation', text_data: str = None, preset: str = None)
```

Orquestador de analisis historico: parsea numeros de texto libre via regex (sin NLP complejo), arma arrays de numpy, y ajusta el motor correspondiente segun analysis_type -- inflation/demographics (regresion log-lineal: tasa anual %, R2), trade_network (centralidad de red: fuerza entrante + autovector, identifica el hub), units_entropy (entropia de Shannon sobre unidades historicas de medida -- indice de homogeneidad 0-100%), o benford (test de bondad de ajuste chi2 contra la distribucion de Benford sobre primeros digitos -- detecta cifras redondeadas/inventadas en padrones tributarios). Con pocos datos extraidos, escala en vez de adivinar. Modes: analyze (requiere text_data o preset), validate (corre 6 casos sinteticos con verdad conocida).

<sub>definido en `server.py:533`</sub>

---

## `historical_extractor`

```python
historical_extractor(mode: str = 'validate', text_data: str = None, objetos: list = None, objeto_salario: str = None)
```

Extrae MULTIPLES series (anio, valor) de un mismo texto historico via regex por oracion (no NLP), una serie por objeto/concepto mencionado (ej: trigo, cebada, jornal). Corre tendencia por regresion log-lineal en cada serie (reusa el motor de historian), calcula salario real indexado si se indica objeto_salario, y correlacion de Pearson entre series de precios que se solapan en anios. NO interpreta causalidad historica (crisis, epidemias) -- solo tasas, indices y correlaciones. Modes: analyze (requiere text_data + objetos, opcional objeto_salario), validate (preset sintetico: trigo/cebada correlacionados, salario real cayendo).

<sub>definido en `server.py:617`</sub>

---

## `information_theory`

```python
information_theory(mode: str, params: dict = None)
```

Teoria de la informacion: entropia de Shannon, divergencia KL, informacion mutua, entropia cruzada, entropia de secuencias.

<sub>definido en `server.py:790`</sub>

---

## `integrate_stiff`

```python
integrate_stiff(system: str = 'van_der_pol', custom_equations: Optional[str] = None, custom_params: Optional[dict] = None, y0: Optional[list] = None, tspan: Optional[list] = None, solver: str = 'ode15s', n_output_points: int = 50, rel_tol: float = 1e-06, abs_tol: float = 1e-08)
```

Integra un sistema de ecuaciones diferenciales ordinarias, incluyendo sistemas rigidos/stiff, usando solvers implicitos de Octave (ode15s, ode23s) o lsode. Presets: van_der_pol (stiff clasico), robertson (cinetica quimica rigida), o custom.

<sub>definido en `server.py:165`</sub>

---

## `levant`

```python
levant(preset: str, params: dict = None)
```

Matematica cananea y de Juda/Israel: hebrew_molad (conjuncion lunar media, ciclo metonico de 19 anios), hebrew_gematria (valor numerico de palabras hebreas y su inverso), canaanite_phoenician_numeral (sistema aditivo 1/10/20/100).

<sub>definido en `server.py:368`</sub>

---

## `linear_algebra`

```python
linear_algebra(mode: str = 'eigen', preset: str = 'known_symmetric', matrix: list = None, data: list = None)
```

Algebra lineal via Octave: eigen (autovalores/autovectores), svd (descomposicion en valores singulares + verificacion), pca (componentes principales, varianza explicada), matrix_analysis (rango, condicion, determinante, inversa). Prerrequisito de persistent_homology_tool.

<sub>definido en `server.py:410`</sub>

---

## `llm_math_bridge_tool`

```python
llm_math_bridge_tool(mode: str = 'auto', params: dict = None)
```

Puente con un LLM real (Anthropic API) para el pipeline matematico. mode='interpret': decide que tool y parametros usar dada una consulta en lenguaje natural (params: query). mode='explain': explica en espanol un resultado ya calculado (params: tool_name, result, query opcional). mode='orchestrate': encadena varios tools segun haga falta (params: query, max_steps opcional). mode='auto' (default): decide heuristicamente entre las anteriores segun la dificultad de la consulta (params: query, max_steps opcional). Requiere ANTHROPIC_API_KEY en el entorno; sin ella devuelve {"error": ...} en vez de fallar.

<sub>definido en `server.py:947`</sub>

---

## `lyapunov_v2_tool`

```python
lyapunov_v2_tool(params: dict = None)
```

Exponente de Lyapunov maximo (version 2, con soporte de guardado de trayectoria en workspace via run_id): chen_lee, burke_shaw, lorenz, rossler o sistema custom.

<sub>definido en `server.py:888`</sub>

---

## `machine_learning_math`

```python
machine_learning_math(mode: str, params: dict = None)
```

Matematica de machine learning: funciones de costo, descenso de gradiente, regresion lineal/logistica, comparacion de regularizacion (ridge/lasso), PCA.

<sub>definido en `server.py:735`</sub>

---

## `math_benchmark`

```python
math_benchmark(mode: str = 'validate', params: dict = None)
```

Benchmark de metodos numericos: comparacion de metodos ODE (Euler/RK2/RK4), cuadratura (trapezoidal/Simpson/Gauss-Legendre), y busqueda de raices (biseccion/Newton/secante).

<sub>definido en `server.py:705`</sub>

---

## `math_error_analyzer`

```python
math_error_analyzer(mode: str = 'validate', params: dict = None)
```

Analisis de error numerico: numero de condicion, error de truncamiento vs redondeo, derivada analitica de referencia.

<sub>definido en `server.py:700`</sub>

---

## `math_explainer`

```python
math_explainer(source_tool: str, result: dict, level: str = 'tecnico')
```

Traduce el resultado crudo (dict) de otra herramienta matematica a una explicacion en lenguaje natural, con nivel tecnico ajustable.

<sub>definido en `server.py:730`</sub>

---

## `math_humanizer_tool`

```python
math_humanizer_tool(mode: str, params: dict = None)
```

Explicaciones divulgativas de conceptos matematicos: analogia cotidiana + conexion filosofica + nota tecnica.

<sub>definido en `server.py:858`</sub>

---

## `math_interpolation`

```python
math_interpolation(mode: str = 'validate', params: dict = None)
```

Interpolacion numerica: Lagrange (baricentrica), splines cubicos naturales, comparacion de nodos (Chebyshev vs equiespaciados).

<sub>definido en `server.py:710`</sub>

---

## `math_interpreter`

```python
math_interpreter(query: str, auto_run: bool = False)
```

Interpreta una consulta matematica en lenguaje natural (castellano) y la traduce a una llamada de herramienta.

<sub>definido en `server.py:720`</sub>

---

## `math_philosophy_history`

```python
math_philosophy_history(topic: str = '', params: dict = None)
```

Referencia sobre filosofia e historia de la matematica (8 topics).

<sub>definido en `server.py:361`</sub>

---

## `math_visualization`

```python
math_visualization(mode: str = 'function_plot', params: dict = None)
```

Visualizacion matematica: graficos de funciones, retratos de fase, campos vectoriales, diagramas de bifurcacion.

<sub>definido en `server.py:725`</sub>

---

## `mcdm_tool`

```python
mcdm_tool(mode: str, params: dict = None)
```

Decision multicriterio: AHP (ponderacion de criterios via matriz de comparacion pareada, con ratio de consistencia de Saaty), TOPSIS (ranking de alternativas por cercania a los ideales positivo/negativo), y weighted_sum (WSM/WPM: suma o producto ponderado con normalizacion min-max, params incluye method='sum'|'product'). params: pairwise_matrix/criteria_names (ahp); decision_matrix, weights, criteria_types, alternative_names (topsis/weighted_sum).

<sub>definido en `server.py:935`</sub>

---

## `multibody_dynamics_tool`

```python
multibody_dynamics_tool(mode: str, params: dict = None)
```

Dinamica de cuerpos rigidos: pendulo fisico compuesto, rotacion libre via ecuaciones de Euler, manipulador/pendulo doble planar.

<sub>definido en `server.py:863`</sub>

---

## `music_math`

```python
music_math(preset: str = 'pythagorean_comma', f0: float = 220.0, n_harmonics: int = 8, n_power: int = 2, signal: list = None, fs: float = 44100)
```

Calculos de matematica musical: pythagorean_comma, temperament_comparison, harmonic_series, ternary_scale (division de la octava en 3^n pasos, conexion con TritOS), spectral_analysis (FFT real via Octave sobre una senal).

<sub>definido en `server.py:402`</sub>

---

## `network_science`

```python
network_science(mode: str, params: dict = None)
```

Ciencia de redes: centralidad, deteccion de comunidades (Louvain), modelos de crecimiento, metricas de grafos.

<sub>definido en `server.py:755`</sub>

---

## `nuclear_decay_chain`

```python
nuclear_decay_chain(preset: str = 'cs137_ba137m', chain: list = None, t_max: float = None, n_points: int = 300, stable_last: bool = True)
```

Resuelve una cadena de decaimiento nuclear (Bateman) via ode45. Presets: cs137_ba137m, sr90_y90, o custom via 'chain'. stable_last=True no sigue la cadena mas alla del ultimo isotopo pero NUNCA anula su lambda (permite alcanzar equilibrio secular).

<sub>definido en `server.py:274`</sub>

---

## `number_theory`

```python
number_theory(mode: str = 'primality_test', preset: str = 'known_cases', n: int = None, p: int = None, q: int = None, e: int = 17, message: int = None, curve_a: int = None, curve_b: int = None, curve_p: int = None, point1: list = None, point2: list = None)
```

Teoria de numeros con aplicacion criptografica: primality_test (Miller-Rabin, detecta numeros de Carmichael), rsa_toy (genera par de claves, cifra/descifra, valida contra ejemplo clasico del paper RSA), elliptic_curve_add (suma/duplicacion de puntos, validado contra Hankerson et al). Conecta con chinese_remainder via RSA-CRT.

<sub>definido en `server.py:442`</sub>

---

## `numeral_systems_embedding`

```python
numeral_systems_embedding(method: str = 'umap', extra_systems: list = None, n_neighbors: int = None, perplexity: float = None, random_state: int = 1, run_id: str = None)
```

Vectoriza sistemas numericos antiguos (base, tipo posicional/aditivo/ fisico, presencia de cero, redundancia representacional, soporte fisico) y proyecta a 2D via UMAP o t-SNE, para explorar agrupamientos estructurales entre culturas. Dataset base: maya_long_count, suanpan, soroban, roman_hand_abacus, yupana_depasquale, quipu, ifa_binary. Extensible via extra_systems (lista de dicts con el mismo schema). Con pocos sistemas, n_neighbors/perplexity se clampean automaticamente. Si se indica run_id, guarda el embedding en el workspace para graficar despues con plot_workspace_run (plot_type=numeral_embedding).

<sub>definido en `server.py:671`</sub>

---

## `ocas_symbolic_tool`

```python
ocas_symbolic_tool(mode: str = 'symbolic', params: dict = None)
```

Algebra simbolica y teoria de numeros via oCAS (motor Rust): simplify/differentiate/integrate/substitute, primalidad, factorizacion, totient, ecuaciones diofanticas, CRT.

<sub>definido en `server.py:868`</sub>

---

## `octave_eval_expr`

```python
octave_eval_expr(expression: str, timeout: int = DEFAULT_TIMEOUT)
```

Evalua una expresion Octave con disp().

<sub>definido en `server.py:112`</sub>

---

## `octave_run`

```python
octave_run(code: str, timeout: int = DEFAULT_TIMEOUT)
```

Ejecuta codigo Octave. timeout en segundos (default 60).

<sub>definido en `server.py:106`</sub>

---

## `octave_run_script`

```python
octave_run_script(script_path: str, timeout: int = DEFAULT_TIMEOUT)
```

Ejecuta un script .m existente en disco.

<sub>definido en `server.py:120`</sub>

---

## `octave_syntax_tool`

```python
octave_syntax_tool(mode: str, params: dict = None)
```

Valida la sintaxis de un fragmento de codigo Octave sin ejecutarlo: envuelve el codigo en una definicion de funcion y la carga via source(), lo que fuerza a Octave a parsear el cuerpo completo (detectando parentesis sin cerrar, 'end'/'endfor'/'endif' faltantes o mal anidados, tokens invalidos, etc.) sin correr ninguna linea del codigo del usuario. mode='syntax_check'. params: code (el fragmento a validar), timeout (segundos, default 10). Devuelve valid=true/false y, si hay error, el mensaje crudo de Octave y la linea detectada.

<sub>definido en `server.py:941`</sub>

---

## `octave_version`

```python
octave_version()
```

Devuelve la version de Octave instalada.

<sub>definido en `server.py:129`</sub>

---

## `optimal_control`

```python
optimal_control(mode: str, params: dict = None)
```

Control optimo: regulador LQR, principio del maximo de Pontryagin (caso LQ), programacion dinamica.

<sub>definido en `server.py:800`</sub>

---

## `optimization`

```python
optimization(mode: str = 'linear_programming', preset: str = 'known_lp', sense: str = 'max', c: list = None, A_ub: list = None, b_ub: list = None, expression: str = None, start: list = None, learning_rate: float = 0.1, n_iterations: int = 200)
```

Optimizacion: linear_programming (via glpk nativo de Octave), gradient_descent (gradiente EXACTO simbolico via sympy, no diferencias finitas). Presets validados contra optimos conocidos.

<sub>definido en `server.py:464`</sub>

---

## `originarios`

```python
originarios(preset: str, params: dict = None)
```

Numeracion de pueblos originarios: mapuche_numeral (rakin, decimal aditivo-multiplicativo) y aymara_numeral (decimal con sufijo -ni, mas nota sobre vestigio quinario).

<sub>definido en `server.py:376`</sub>

---

## `paleography`

```python
paleography(mode: str = 'validate', params: dict = None)
```

Tres motores cuantitativos de paleografia/codicologia: seriation (analisis de correspondencia via SVD), feature_dating_regression (estima fecha de documentos sin fecha), letterform_classification (nearest-centroid sobre rasgos normalizados).

<sub>definido en `server.py:825`</sub>

---

## `particle_simulation_tool`

```python
particle_simulation_tool(mode: str, params: dict = None)
```

Simulacion de particulas: orbita de Kepler (dos cuerpos), colisiones elasticas en cadena 1D, caminata aleatoria y difusion.

<sub>definido en `server.py:873`</sub>

---

## `pde`

```python
pde(mode: str = 'heat_equation', preset: str = 'known_first_mode', L: float = 1.0, coefficient: float = 0.01, n_points: int = 50, t_final: float = None, initial_profile: list = None)
```

Ecuaciones en derivadas parciales via diferencias finitas explicitas en Octave: heat_equation (u_t=alpha*u_xx), wave_equation (u_tt=c^2*u_xx). Validado contra solucion analitica del primer modo normal. Extension de stiff_ode_tool hacia EDPs -- relevante para propagacion termica LIG.

<sub>definido en `server.py:473`</sub>

---

## `percolation_theory`

```python
percolation_theory(mode: str, params: dict = None)
```

Teoria de percolacion: percolacion de sitios/enlaces en reticulas, umbral critico, percolacion sobre grafos.

<sub>definido en `server.py:770`</sub>

---

## `persistent_homology`

```python
persistent_homology(preset: str = 'circle', points: list = None, max_edge_length: float = None, max_dim: int = 2, n_points: int = 20, seed: int = 1, run_id: str = None)
```

Homologia persistente (H0, H1) sobre una nube de puntos via complejo de Vietoris-Rips y reduccion de matriz de borde. Presets sinteticos validados (circle, two_clusters, random_noise) o custom via 'points' para datos reales -- por ejemplo nubes reconstruidas de un embedding de Takens (conexion directa con TritOS). Si se indica run_id, guarda points/h0_diagram/h1_diagram en el workspace para graficar despues con plot_workspace_run (plot_type=persistence_diagram).

<sub>definido en `server.py:419`</sub>

---

## `plague_sir`

```python
plague_sir(mode: str = 'validate', text_data: str = None, preset: str = None, gamma: float = 0.4, poblacion_estimada: float = 2000.0)
```

SIR inverso para brotes historicos de peste: parsea defunciones semanales de texto libre via regex, ajusta beta (tasa de contagio) con curve_fit manteniendo gamma fijo (parametro de literatura, no medido), integra SIR con RK4, y reporta R0=beta/gamma. Proxy cuantitativo cuando no hay fuente epidemiologica directa -- no corrige subregistro, migracion, ni estacionalidad. Modes: fit_beta (requiere text_data o preset='peste_demo'), validate (compara contra brote sintetico con beta/R0 conocidos).

<sub>definido en `server.py:565`</sub>

---

## `plot_workspace_run`

```python
plot_workspace_run(run_id: str, plot_type: str = 'auto', title: str = None, array_name: str = None)
```

Genera una visualizacion (PNG en base64 + guardado en disco) a partir de un run guardado en el workspace (ej: la trayectoria de un atractor guardada por compute_lyapunov con run_id). No recalcula nada, solo lee y grafica. plot_type: auto (infiere segun el tool de origen), attractor_3d, attractor_2d, line, scatter, heatmap.

<sub>definido en `server.py:662`</sub>

---

## `population_dynamics`

```python
population_dynamics(mode: str = 'lotka_volterra', a: float = 1.0, b: float = 0.1, c: float = 1.5, d: float = 0.075, x0: float = 10.0, y0: float = 5.0, r: float = 0.5, K: float = 100.0, t_max: float = 50.0, n_points: int = 50)
```

Dinamica de poblaciones: lotka_volterra (depredador-presa), logistic_growth (capacidad de carga). Relevante para cultivo de kelp en infraestructura de longline existente.

<sub>definido en `server.py:493`</sub>

---

## `population_genetics`

```python
population_genetics(mode: str, params: dict = None)
```

Genetica de poblaciones: equilibrio de Hardy-Weinberg, deriva genetica (simulacion), seleccion natural, tiempo de coalescencia, distancia genetica (Fst).

<sub>definido en `server.py:760`</sub>

---

## `qm_potential_well`

```python
qm_potential_well(preset: str = 'infinite_well', custom_potential: str = None, well_params: dict = None, x_range: list = None, n_points: int = 400, mass: float = 1.0, hbar: float = 1.0, n_states: int = 5)
```

Resuelve la ecuacion de Schrodinger 1D independiente del tiempo por diferencias finitas. Presets: infinite_well, finite_well, harmonic_oscillator, o custom via custom_potential (expresion Octave en x).

<sub>definido en `server.py:254`</sub>

---

## `quantity_takeoff_tool`

```python
quantity_takeoff_tool(operation: str, params: dict = None)
```

Cubicaciones de construccion: volumen de hormigon, area de encofrado, peso de acero de refuerzo, volumen de excavacion, conteo de albanileria, resumen BOQ.

<sub>definido en `server.py:878`</sub>

---

## `quantum_information`

```python
quantum_information(mode: str, params: dict = None)
```

Informacion cuantica: vector de Bloch, secuencias de compuertas, Deutsch-Jozsa, busqueda de Grover, entropia de entrelazamiento, codigo de correccion bit-flip.

<sub>definido en `server.py:820`</sub>

---

## `reaction_diffusion`

```python
reaction_diffusion(mode: str = 'check_turing_instability', a11: float = 1.0, a12: float = -1.0, a21: float = 2.0, a22: float = -1.5, Du: float = 1.0, Dv: float = 10.0)
```

Inestabilidad de Turing (reaccion-difusion linealizada): evalua las 4 condiciones analiticas clasicas y compara tasa de crecimiento numerica vs analitica en el numero de onda mas inestable. Mecanismo detras de patrones biologicos (rayas, manchas, morfogenesis).

<sub>definido en `server.py:502`</sub>

---

## `reaction_diffusion_real_tool`

```python
reaction_diffusion_real_tool(params: dict = None)
```

Inestabilidad de Turing (reaccion-difusion linealizada): evalua las 4 condiciones analiticas clasicas para un sistema de 2 especies.

<sub>definido en `server.py:893`</sub>

---

## `run_math_pipeline`

```python
run_math_pipeline(steps: list = None, mode: str = 'validate')
```

Ejecuta un pipeline de pasos encadenados entre distintas herramientas matematicas del servidor.

<sub>definido en `server.py:715`</sub>

---

## `settlement_clusters`

```python
settlement_clusters(mode: str = 'validate', puntos_por_periodo: list = None, periodos: list = None, radio: float = 1.0, radio_match: float = 2.0, run_id: str = None)
```

Proxy arqueologico de barrios/clusters sociales: clusteriza coordenadas de hallazgos por distancia (union-find a radio fijo) en cada periodo/estrato, y rastrea clusters entre periodos consecutivos por proximidad de centroides -- detecta nacimiento y muerte de asentamientos. No hace inferencia cronologica, el orden de periodos lo define quien llama. Modes: analyze (requiere puntos_por_periodo y periodos), validate (corre preset sintetico con migracion/fision conocida). Si se indica run_id (solo aplica en mode=analyze), guarda points_all/centroids_all en el workspace para graficar despues con plot_workspace_run (plot_type=settlement_map).

<sub>definido en `server.py:578`</sub>

---

## `spatial_statistics`

```python
spatial_statistics(mode: str, params: dict = None)
```

Estadistica espacial: I de Moran, C de Geary, semivariograma, interpolacion por kriging.

<sub>definido en `server.py:805`</sub>

---

## `statistical_physics_tool`

```python
statistical_physics_tool(mode: str, params: dict = None)
```

Fisica estadistica y sistemas complejos: modelo de Ising 2D via Monte Carlo Metropolis (magnetizacion, energia, calor especifico, estimacion de temperatura critica vs valor exacto de Onsager) y modelo de Potts de q estados para crecimiento de grano/microestructura (evolucion de numero de granos y area promedio en el tiempo). mode='ising_2d' o 'potts_grain_growth'.

<sub>definido en `server.py:905`</sub>

---

## `statistics`

```python
statistics(mode: str = 'linear_regression', preset: str = 'known_linear', x: list = None, y: list = None, sample: list = None, mu0: float = 5.0, prior_a: float = 1.0, prior_b: float = 1.0, successes: int = 7, trials: int = 10)
```

Estadistica e inferencia via Octave: linear_regression (minimos cuadrados), correlation (Pearson r), t_test (una muestra, t-stat + p-value via betainc), bayesian_beta_binomial (actualizacion conjugada Beta-Binomial). Pensado para analisis de riesgo (QGIS).

<sub>definido en `server.py:432`</sub>

---

## `statistics_extended_tool`

```python
statistics_extended_tool(mode: str, params: dict = None)
```

Fase A de estadistica: descriptiva/EDA (descriptive_stats: media, mediana, moda, cuartiles, asimetria, curtosis, outliers IQR/z-score), tablas de contingencia con chi-cuadrado (contingency_table), tests de 2 muestras parametricos y no parametricos (two_sample_tests: ttest_ind, ttest_paired, mannwhitney, wilcoxon, ks_2samp), ANOVA de 1 via con post-hoc Bonferroni (anova_oneway), tests de normalidad (normality_tests: shapiro, jarque_bera), y remuestreo (resampling: bootstrap percentil/BCa, test de permutaciones). Validado cruzado contra scipy.stats.

<sub>definido en `server.py:917`</sub>

---

## `stochastic_processes`

```python
stochastic_processes(mode: str, params: dict = None)
```

Procesos estocasticos: movimiento browniano (estandar/con drift/geometrico), proceso de Ornstein-Uhlenbeck (reversion a la media, util para variables ambientales con equilibrio), cadenas de Markov discretas (distribucion estacionaria, tiempo de primer paso), y mcmc (Metropolis-Hastings generico: target gaussiano o custom via expresion sympy, devuelve media/covarianza posterior, acceptance rate y effective sample size).

<sub>definido en `server.py:785`</sub>

---

## `structural_analysis_tool`

```python
structural_analysis_tool(mode: str, params: dict = None)
```

Analisis estructural preliminar: vigas (reacciones/corte/momento/deflexion), cerchas 2D isostaticas, propiedades de seccion, chequeo de esfuerzo admisible.

<sub>definido en `server.py:883`</sub>

---

## `symbolic`

```python
symbolic(mode: str = 'simplify', preset: str = 'known_simplify', expression: str = None, variable: str = 'x', lower_limit: str = None, upper_limit: str = None, point: str = '0', order: int = 5)
```

Algebra simbolica via sympy: simplify, solve (resolver ecuaciones), differentiate (derivada), integrate (indefinida o definida con limites), taylor_series. Puente necesario porque Octave es 100% numerico.

<sub>definido en `server.py:455`</sub>

---

## `tensor_calculus`

```python
tensor_calculus(mode: str, params: dict = None)
```

Calculo tensorial/geometria diferencial: simbolos de Christoffel, tensor de Riemann, Ricci, curvatura escalar, ecuaciones geodesicas (backend simbolico o numerico).

<sub>definido en `server.py:750`</sub>

---

## `text_analysis_math`

```python
text_analysis_math(mode: str, params: dict = None)
```

Matematica del analisis de texto: distancia de edicion, modelos n-grama, leyes de frecuencia (Zipf), estilometria.

<sub>definido en `server.py:810`</sub>

---

## `tritbraid`

```python
tritbraid(mode: str = 'validate_physics', program: str = '1,2,M,0,M,2,M', seed: int = 42, initial_state: list = None)
```

DSL TritBraid: secuencias de trenzas de Fibonacci que colapsan a un trit ternario (-1,0,+1). Tokens del programa: 0=identidad, 1=sigma1 (diagonal, no mezcla canales), 2=sigma2 (mezcla via matriz F), M=medicion (colapso proyectivo, regla de Born). Modes: run_program (ejecuta el programa dado y devuelve traza completa), validate_physics (verifica unitariedad, invariancia bajo identidad/sigma1, y mezcla bajo sigma2). Misma construccion de Bonesteel et al 2005 que braid_group_tool -- puente concreto hacia el sistema ternario de TritOS.

<sub>definido en `server.py:520`</sub>

---

## `wavelet`

```python
wavelet(mode: str, params: dict = None)
```

Analisis wavelet: transformada continua (CWT) y discreta (DWT), denoising, deteccion de transitorios.

<sub>definido en `server.py:765`</sub>

---

## `workspace_delete`

```python
workspace_delete(run_id: str)
```

Borra un run del workspace (libera espacio en disco).

<sub>definido en `server.py:657`</sub>

---

## `workspace_describe`

```python
workspace_describe(run_id: str)
```

Muestra shapes/dtypes de un run sin cargar los arrays completos a memoria (util para trayectorias largas antes de graficar).

<sub>definido en `server.py:651`</sub>

---

## `workspace_list`

```python
workspace_list(filter_tool: str = None)
```

Lista todos los runs guardados en el workspace, opcionalmente filtrados por tool de origen (ej: 'compute_lyapunov_exponent').

<sub>definido en `server.py:645`</sub>

---

## `workspace_load`

```python
workspace_load(run_id: str, keys: list = None)
```

Carga un run guardado previamente por run_id. Si keys se omite, devuelve todos los arrays (cuidado con trayectorias muy largas: usar workspace_describe primero).

<sub>definido en `server.py:638`</sub>

---

## `workspace_save`

```python
workspace_save(run_id: str = None, data: dict = None, meta: dict = None)
```

Guarda arrays/resultados de un analisis bajo un run_id para reutilizarlos despues (ej: en plot_tool) sin recalcular. Si run_id se omite, se autogenera.

<sub>definido en `server.py:632`</sub>

---
