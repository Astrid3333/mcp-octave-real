# octave-mcp

Servidor MCP (Model Context Protocol) que expone GNU Octave y una colección
de herramientas de cómputo numérico, matemática histórica/etnomatemática,
sistemas dinámicos y matemática pura/aplicada como tools invocables desde
Claude Desktop.

Construido con [FastMCP](https://github.com/jlowin/fastmcp). 29 tools.

## Qué hace

Cada módulo del repo es un tool independiente registrado en `server.py`.
Se agrupan en cinco grandes áreas:

### Sistemas dinámicos y cómputo numérico
- **`lyapunov_tool`** — exponente de Lyapunov máximo (λ₁) para cuantificar
  caos en sistemas como Chen-Lee, Burke-Shaw, Lorenz, Rössler, o ecuaciones
  custom.
- **`stiff_ode_tool`** — integración de EDOs rígidas/stiff con solvers
  implícitos de Octave (ode15s, ode23s, lsode). Presets: Van der Pol,
  Robertson.
- **`bifurcation_tool`** — diagramas de bifurcación para mapas iterativos 1D
  (logístico, seno, cúbico, tent, custom), con análisis de estabilidad.
- **`hilbert_tool`** — transformada de Hilbert de series temporales no
  estacionarias: envolvente, fase y frecuencia instantánea.
- **`graph_tool`** — algoritmos de grafos clásicos: Dijkstra, MST (Kruskal),
  detección de ciclos.
- **`qm_tool`** — ecuación de Schrödinger 1D independiente del tiempo por
  diferencias finitas (pozo infinito, finito, oscilador armónico, potencial
  custom).
- **`nuclear_decay_tool`** — cadenas de decaimiento nuclear (ecuaciones de
  Bateman) vía ode45. Presets: Cs-137→Ba-137m, Sr-90→Y-90.
- **`fractal_dimension_tool`** — dimensión fractal por box-counting
  (Sierpinski, Koch, Cantor con dimensión analítica de referencia, o el
  atractor caótico Chen-Lee integrado en Octave).
- **`cross_validation_tool`** — valida resultados de dimensión fractal
  corriendo el mismo sistema con dos motores numéricos independientes
  (Octave ode45 + scipy RK45).
- **`ancestral_octave_tool`** — corre métodos de cómputo ancestral
  (suanpan_add, chinese_remainder, vedic_multiply, archimedes_pi,
  quipu_encode) como funciones Octave nativas.
- **`pde_tool`** — ecuaciones de calor y onda 1D vía diferencias finitas
  explícitas, validado contra la solución analítica del primer modo
  normal. Extensión de `stiff_ode_tool` hacia EDPs.

### Matemática pura / álgebra / análisis
- **`linear_algebra_tool`** — autovalores/autovectores, SVD, PCA, análisis
  de matrices (rango, número de condición, determinante) vía Octave nativo.
- **`persistent_homology_tool`** — homología persistente (H₀, H₁) sobre
  nubes de puntos vía complejo de Vietoris-Rips y reducción de matriz de
  borde, implementado en Python puro. Validado contra la fórmula analítica
  del nacimiento/muerte de un lazo en un círculo. Conexión directa con
  TritOS (embedding de Takens + homología persistente).
- **`statistics_tool`** — regresión lineal, correlación de Pearson, t-test
  de una muestra (p-value vía `betainc` nativo de Octave), inferencia
  bayesiana conjugada beta-binomial.
- **`number_theory_tool`** — test de primalidad Miller-Rabin (detecta
  números de Carmichael), RSA de juguete (validado contra el ejemplo
  clásico del paper original), aritmética de curvas elípticas (validado
  contra Hankerson et al). Python puro, precisión arbitraria. Conecta con
  `chinese_remainder` vía la optimización RSA-CRT.
- **`symbolic_tool`** — álgebra simbólica vía sympy: simplificación,
  resolución de ecuaciones, derivadas, integrales (indefinidas y
  definidas), series de Taylor. Puente necesario porque Octave es 100%
  numérico.
- **`optimization_tool`** — programación lineal vía `glpk` nativo de
  Octave, descenso de gradiente con gradiente exacto simbólico (vía
  sympy, no diferencias finitas).

### Análisis de estructura y sistemas sin descifrar
- **`entropy_structure_tool`** — entropía de orden 0 y entropía condicional
  de orden 1 sobre secuencias de símbolos, para evaluar evidencia de
  estructura combinatoria (tipo Rao et al. 2009 sobre la escritura del
  valle del Indo) vs. ausencia de estructura (tally marks/conteo).

### Matemática musical
- **`music_math_tool`** — coma pitagórica exacta, comparación de
  intervalos justos vs. temperamento igual, serie armónica, escala de
  división ternaria de la octava (conexión con TritOS), análisis
  espectral real vía FFT en Octave.

### Etnomatemática / matemática histórica
- **`ethnomath_tool`** — maya_long_count, chinese_remainder, vedic_multiply,
  quipu_encode, greek_archimedes_pi, japanese_enri_pi.
- **`ethnomath2_tool`** — egyptian_duplation, persian_khwarizmi,
  persian_alkashi_sin1, russian_peasant, ottoman_taqi_al_din,
  norse_rune_calendar, southeast_asian_metonic.
- **`ancient_calculators_tool`** — simuladores de calculadoras históricas
  reales: suanpan, soroban, ábaco romano, yupana (hipótesis De Pasquale,
  con aviso de disputa académica).
- **`levant_tool`** — matemática cananea y de Judá/Israel: hebrew_molad,
  hebrew_gematria, canaanite_phoenician_numeral.
- **`originarios_tool`** — numeración mapuche (rakin) y aymara.
- **`filosofia_historia_mate_tool`** — referencia curada sobre filosofía e
  historia de la matemática (9 tópicos), marcando explícitamente qué está
  establecido académicamente, qué es disputado, y qué es reconstrucción
  moderna.

## Requisitos

- Python 3 + [`fastmcp`](https://pypi.org/project/fastmcp/) + `sympy`
- GNU Octave con `glpk` (nativo, sin paquetes extra)
- `scipy` (solo para `cross_validation_tool`)

```bash
pip install fastmcp sympy scipy --break-system-packages
```

## Uso con Claude Desktop

Agregar en `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "octave-mcp": {
      "command": "python3",
      "args": ["/ruta/absoluta/a/mcp_octave/server.py"]
    }
  }
}
```

Reiniciar Claude Desktop para que cargue el servidor.

## Estructura

```
mcp_octave/
├── server.py                       # registro de todos los tools MCP
├── *_tool.py                       # un módulo por tool
├── ancestral.m, ancestral2.m       # funciones Octave nativas usadas por ancestral_octave_tool
└── add_math_philosophy_tool.py     # script de instalacion puntual usado para
                                     # insertar el wrapper de math_philosophy_history
```

## Notas de diseño

- Los presets con estado académico incierto o disputado (yupana, sutras
  védicos) lo declaran explícitamente en el output en vez de presentar todo
  con el mismo nivel de certeza.
- `cross_validation_tool` y `entropy_structure_tool` comparten el mismo
  principio: nunca reportar un número aislado sin un baseline de
  comparación (otro motor numérico, o una secuencia sintética generada con
  el mismo tamaño y alfabeto).
- Los siete módulos de matemática pura/aplicada (`linear_algebra`,
  `persistent_homology`, `statistics`, `number_theory`, `symbolic`,
  `optimization`, `pde`) siguen todos el mismo patrón: cada preset se
  valida contra un resultado analítico o de libro de texto conocido antes
  de aplicarse a datos custom.
- `persistent_homology_tool` y `entropy_structure_tool` están pensados
  para poder correr sobre datos arqueológicos reales (khipu, yupana,
  corpus sin descifrar) si en algún momento se consigue el dataset.

## Autora

Astrid ([@Astrid3333](https://github.com/Astrid3333)) — Castro, Chiloé, Chile.
