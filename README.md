## 1. Qué queremos demostrar

Este proyecto **no** busca demostrar simplemente si un modelo cuántico es mejor o peor que uno clásico.

El objetivo real del paper es demostrar que:

> **Pueden existir perturbaciones que alteren de forma material las conclusiones experimentales, mientras los mecanismos habituales de integridad o detección de drift muestran poca o ninguna evidencia clara de lo ocurrido.**

Dicho de otra forma:

- no basta con medir **robustez**;
- también hay que medir **auditabilidad**;
- una perturbación preocupante no es solo la que degrada el rendimiento,
- sino la que lo degrada **sin dejar un rastro claro**.

El concepto central del trabajo es el **auditability gap**:

> **alto impacto + baja observabilidad**

---

## 2. Qué NO queremos hacer

Este proyecto **no** debe plantearse como:

- “cómo falsificar resultados cuánticos”;
- “cómo manipular benchmarks sin dejar rastro”;
- “cómo engañar sistemas financieros”;
- “cómo atacar bancos con algoritmos cuánticos”.

Ese no es el enfoque correcto.

La formulación correcta es:

- identificar **debilidades metodológicas reales**;
- estudiar perturbaciones que pueden comprometer la **fiabilidad de la evaluación**;
- analizar **qué señales detectan bien el problema y cuáles fallan**;
- proponer una forma de **cerrar ese hueco**.

---

## 3. Tesis del paper

La tesis que queremos defender es la siguiente:

> **La evaluación de modelos clásicos y cuánticos puede ser vulnerable a perturbaciones de alto impacto y baja observabilidad, lo que implica que un benchmark centrado solo en robustez puede inducir conclusiones incompletas o engañosas.**

Esto es especialmente relevante para:

- validación experimental de modelos;
- auditoría de pipelines de ML;
- evaluación de sistemas en contextos de alto impacto;
- futuros escenarios donde modelos cuánticos puedan integrarse en dominios sensibles.

---

## 4. Pregunta principal de investigación

**¿Qué perturbaciones pueden alterar de forma material las conclusiones de un benchmark clásico/cuántico mientras las señales estándar de integridad muestran poca o ninguna evidencia clara de lo ocurrido?**

---

## 5. Subpreguntas

1. ¿Qué perturbaciones generan mayor degradación del rendimiento?
2. ¿Qué perturbaciones son peor detectadas por las señales estándar?
3. ¿Existen perturbaciones de alto impacto y baja observabilidad?
4. ¿Ese patrón depende del modelo concreto y del feature map cuántico?
5. ¿Qué señales adicionales hacen falta para mejorar la auditabilidad del benchmark?

---

## 6. Hipótesis

### H1
No todas las perturbaciones con gran impacto generan una señal fuerte de integridad.

### H2
Las perturbaciones sobre etiquetas o sobre componentes no cubiertos por señales feature-centric presentan peor detectabilidad que muchas perturbaciones sobre features.

### H3
Los modelos cuánticos no forman un bloque homogéneo: distintos feature maps presentan perfiles diferentes de vulnerabilidad y detectabilidad.

### H4
Un benchmark centrado solo en robustez puede inducir conclusiones incompletas o engañosas si no incorpora una dimensión explícita de auditabilidad.

---

## 7. Modelos del estudio

### Baseline clásico
- `svc_rbf`

### Modelos cuánticos
- `qsvc_zz_r1`
- `qsvc_z_r1`
- `qsvc_pauli_xz_r1`
- `qsvc_pauli_xyz_r1`

**Decisión importante:** el análisis principal debe hacerse **por modelo concreto**, no colapsando todo bajo “quantum”.

Uno de los mensajes del paper es precisamente:

> **“quantum” no es una categoría homogénea.**

---

## 8. Datos y escenarios

### Dataset base
- CICIDS (subset preparado para benchmark clásico/cuántico)

### Escenarios experimentales
1. **ID controlado**
   - sirve para demostrar el fenómeno de forma limpia y controlada.

2. **OOD-by-files**
   - sirve para validar que el fenómeno no es solo un artefacto de ataques sintéticos sobre un split aleatorio.

---

## 9. Tipos de perturbaciones

Las familias de perturbaciones que nos interesan son:

- `corruption`
- `covariate_shift`
- `noise`
- `pipeline`
- `distortion`
- `target_shift`

Ejemplos concretos ya contemplados en el proyecto:

- `label_flip`
- `feature_sign_flip`
- `scaling_drift`
- `mean_shift_pf`
- `feature_dropout`
- `gaussian_noise`
- `quantization`
- `clipping`

### Ataques prioritarios para el paper
El núcleo experimental debe centrarse primero en:

- `label_flip`
- `feature_sign_flip`
- `scaling_drift`
- `mean_shift_pf`
- `feature_dropout`

El resto pueden quedar como apoyo.

---

## 10. Qué vamos a medir

## 10.1 Impacto
La métrica principal del paper debe ser:

- **balanced accuracy drop**

Métricas secundarias:

- ROC-AUC drop
- F1 drop

---

## 10.2 Detectabilidad
Las señales actuales del proyecto son:

- feature-distribution JSD
- MMD
- KS reject rate
- score-drift JSD

Estas señales son útiles, pero no suficientes.

---

## 10.3 Señales nuevas necesarias
Para que el paper sea fuerte, debemos añadir señales **label-aware**, como mínimo:

- `label_prior_shift`
- `predicted_positive_rate_shift`
- `prediction_disagreement_rate`

Opcionalmente:
- `confusion_profile_shift`

---

## 10.4 Concepto central: stealthiness / auditability gap
Tenemos que definir una métrica que combine:

- cuánto daño hace la perturbación;
- cuánto se detecta.

Idea conceptual:

> una perturbación es especialmente peligrosa cuando **daña mucho** el resultado pero **se ve poco** en las señales de auditoría.

---

## 11. Mensaje fuerte del paper

El mensaje más importante **no** debe ser:

- “el cuántico gana”;
- “el clásico gana”;
- “los modelos cuánticos son peores”.

El mensaje correcto es:

> **hay perturbaciones que pueden cambiar materialmente la lectura experimental sin generar una evidencia proporcional en las señales habituales de integridad.**

Y además:

- ese fenómeno depende del tipo de perturbación;
- depende del modelo concreto;
- depende del feature map;
- y obliga a repensar la evaluación de robustez desde una perspectiva de auditabilidad.

---

## 12. Aportaciones esperadas

### C1. Benchmark reproducible de impacto + detectabilidad
Un marco que no solo mida caída de rendimiento, sino también cuánto se detecta la perturbación.

### C2. Evidencia de un auditability gap
Identificación de perturbaciones de alto impacto y baja observabilidad.

### C3. Análisis desagregado de QML
Demostrar que distintos feature maps cuánticos presentan comportamientos diferentes, y que agruparlos todos como “quantum” oculta parte del resultado real.

### C4. Propuesta metodológica defensiva
Definir señales adicionales y una forma mejor de auditar benchmarks clásicos/cuánticos.

---

## 13. Plan experimental correcto

## Fase 1 — Refactor del análisis
Antes de lanzar más runs:

- analizar por `model`, no solo por `model_family`;
- usar severidad explícita (`attack_strength_nominal`);
- añadir señales label-aware;
- introducir métrica de `stealthiness`.

## Fase 2 — ID reducido y quirúrgico
Ejecutar un experimento controlado con:

- protocolo `id`
- dimensiones SVD: `6` y `10`
- seeds reducidas
- baseline clásico + 4 QSVC
- ataques núcleo

Objetivo:
- comprobar que la historia principal aparece de forma clara.

## Fase 3 — ID completo
Si la señal es buena:

- ampliar a `4, 6, 8, 10, 12`
- ampliar seeds
- incluir suite más amplia de perturbaciones

## Fase 4 — OOD serio
Validar el fenómeno en varios pares OOD-by-files.

## Fase 5 — Resultados finales
Extraer:

- clean performance por modelo
- drop medio por familia de ataque
- ranking de perturbaciones stealthy
- comparación ID vs OOD
- trade-off de coste computacional

---

## 14. Figuras clave del paper

1. **Impact vs detectability scatter**
2. **Heatmap de stealthiness por ataque y modelo**
3. **Clean performance by model and SVD**
4. **Comparación ID vs OOD**
5. **Time-cost by model and dimension**

---

## 15. Tablas clave del paper

1. rendimiento limpio por modelo y dimensión;
2. drop medio por familia de ataque;
3. top stealthiest perturbations;
4. comparación entre señales antiguas y nuevas;
5. ranking de feature maps cuánticos por:
   - rendimiento limpio,
   - impacto,
   - detectabilidad,
   - stealthiness.

---

## 16. Claim principal del paper

Una formulación buena sería:

> **We identify high-impact, low-observability perturbations that can materially alter benchmark conclusions while remaining weakly reflected by standard integrity signals.**

Y en español:

> **Identificamos perturbaciones de alto impacto y baja observabilidad capaces de alterar materialmente las conclusiones de un benchmark mientras las señales estándar de integridad reflejan débilmente lo ocurrido.**

---

## 17. Resumen ejecutivo

Si en algún momento hay dudas, la idea base del proyecto es esta:

> **Este paper trata sobre auditabilidad en evaluación clásica y cuántica.**
> No buscamos demostrar “ventaja cuántica”, sino estudiar qué perturbaciones pueden cambiar una conclusión experimental sin dejar una constancia clara en los mecanismos habituales de control, y proponer cómo cerrar ese hueco metodológico.

---

## 18. Regla para futuras conversaciones

Si este proyecto se retoma más adelante, asumir siempre que:

1. el foco principal es **auditability gap**, no “quantum advantage”;
2. el análisis debe ir **por modelo concreto**;
3. el objetivo es estudiar **impacto + detectabilidad**;
4. el paper debe terminar con una **propuesta metodológica defensiva**, no solo con diagnóstico;
5. la narrativa debe ser rigurosa y prudente: riesgo metodológico real hoy, con implicaciones potenciales para dominios de alto impacto en el futuro.
"""

out = Path("/mnt/data/README_AUDITABILITY_PAPER.md")
out.write_text(readme, encoding="utf-8")
print(out)
