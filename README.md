# octave-mcp

Servidor MCP (Model Context Protocol) que expone GNU Octave y una colección
de herramientas de cómputo numérico, matemática histórica/etnomatemática y
sistemas dinámicos como tools invocables desde Claude Desktop.

Construido con [FastMCP](https://github.com/jlowin/fastmcp). 22 tools.

## Qué hace

Cada módulo del repo es un tool independiente registrado en `server.py`.
Se agrupan en cuatro grandes áreas:

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
  (Octave ode45 + scipy RK45), para detectar cuándo no confiar en un
  resultado sin necesidad de investigar manualmente.
- **`ancestral_octave_tool`** — corre métodos de cómputo ancestral
  (suanpan_add, chinese_remainder, vedic_multiply, archimedes_pi,
  quipu_encode) como funciones Octave nativas.

### Etnomatemática / matemática histórica
- **`ethnomath_tool`** — maya_long_count, chinese_remainder, vedic_multiply,
  quipu_encode, greek_archimedes_pi, japanese_enri_pi.
- **`ethnomath2_tool`** — egyptian_duplation, persian_khwarizmi,
  persian_alkashi_sin1, russian_peasant, ottoman_taqi_al_din,
  norse_rune_calendar, southeast_asian_metonic.
- **`ancient_calculators_tool`** — simuladores de calculadoras históricas
  reales operando sus cuentas/fichas: suanpan, soroban, ábaco romano,
  yupana (hipótesis De Pasquale, con aviso de disputa académica).
- **`levant_tool`** — matemática cananea y de Judá/Israel: hebrew_molad
  (conjunción lunar media, ciclo metónico de 19 años), hebrew_gematria,
  canaanite_phoenician_numeral.
- **`originarios_tool`** — numeración de pueblos originarios:
  mapuche_numeral (rakin, decimal aditivo-multiplicativo), aymara_numeral.
- **`filosofia_historia_mate_tool`** — referencia curada sobre filosofía e
  historia de la matemática (9 tópicos: escuelas filosóficas, crisis de
  fundamentos, infinito, cero, sutras védicos, yupana, quipu,
  etnomatemática como campo, numerales del Levante antiguo), marcando
  explícitamente qué está establecido académicamente, qué es disputado, y
  qué es reconstrucción moderna.

### Análisis de estructura y sistemas sin descifrar
- **`entropy_structure_tool`** — entropía de orden 0 y entropía condicional
  de orden 1 sobre secuencias de símbolos, para evaluar evidencia de
  estructura combinatoria (compatible con codificación tipo-lenguaje) vs.
  ausencia de estructura (compatible con tally marks/conteo simple).
  Presets sintéticos validados (`random_iid`, `markov_structured`) o
  `custom` con secuencias reales (khipu, yupana, corpus sin descifrar).
  Mismo enfoque metodológico que Rao et al. 2009 (*Science*) sobre la
  escritura del valle del Indo — expone los baselines explícitamente en
  vez de dar un veredicto, ya que ese debate sigue disputado (Sproat 2010).

### Matemática musical
- **`music_math_tool`** — coma pitagórica exacta (23.46 cents), comparación
  de intervalos justos vs. temperamento igual (12-TET), serie armónica con
  desviación en cents, escala de división ternaria de la octava (3ⁿ pasos
  — conexión directa con TritOS: grafeno con 3 estados nativos -1/0/+1), y
  análisis espectral real vía FFT en Octave (detección de parciales +
  aspereza sensorial simplificada de Plomp-Levelt).

## Requisitos

- Python 3 + [`fastmcp`](https://pypi.org/project/fastmcp/)
- GNU Octave instalado y en el PATH (`octave --no-gui --no-init-file`)
- `scipy` (solo para `cross_validation_tool`, validación cruzada Octave/scipy)

```bash
pip install fastmcp --break-system-packages
pip install scipy --break-system-packages   # si vas a usar cross_validation
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
- `cross_validation_tool` existe porque un resultado de dimensión fractal
  del atractor Chen-Lee salió sesgado por submuestreo en una corrida
  anterior; el módulo automatiza la verificación con un segundo motor
  numérico para no depender de un único cálculo cuando la confianza en el
  número importa.
- `entropy_structure_tool` extiende ese mismo principio a un dominio
  distinto: en vez de comparar dos motores numéricos, compara un resultado
  real contra baselines sintéticos generados con la misma longitud y
  alfabeto, para no reportar una métrica de estructura aislada sin
  contexto de comparación.

## Autora

Astrid ([@Astrid3333](https://github.com/Astrid3333)) — Castro, Chiloé, Chile.
