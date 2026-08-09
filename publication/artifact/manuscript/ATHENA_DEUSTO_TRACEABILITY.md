# Matriz de trazabilidad ATHENA-AEGIS — contribución Deusto

Fecha de corte: 9 de agosto de 2026  
Artefacto científico: *Information-Set Conditional Integrity Auditing for Hybrid Quantum-Classical Kernel Workflows*

## Propósito y regla de lectura

Esta matriz relaciona las obligaciones científicas y técnicas del subproyecto
ATHENA-AEGIS con evidencia verificable del repositorio. Distingue cuatro estados:

- **Cubierto**: existe evidencia reproducible que responde directamente al requisito.
- **Parcial alto**: la contribución científica está demostrada, pero falta su cierre operacional o de producto.
- **Parcial**: existe un demostrador relevante, pero no cubre toda la capacidad descrita.
- **No cubierto**: el artefacto actual no contiene evidencia para sostener el requisito.

El estado se refiere a este repositorio y a este paper, no al avance total del
equipo Deusto. La memoria etiqueta literalmente como “Subtask 3.4.4” la última
subtarea de herramientas end-to-end, inmediatamente después de 3.3.3; se
conserva esa numeración y se señala la aparente inconsistencia documental.

## Índice de evidencia

| ID | Evidencia | Función probatoria |
|---|---|---|
| E1 | `manuscript/paper15_q1_manuscript_spine_v11.md` | Claim, formalización, métodos, resultados y límites integrados |
| E2 | `manuscript/PAPER15_Q1_MAXIMUM_STRATEGY.md` | Posicionamiento doctoral, jerarquía de claims y gates de cierre |
| E3 | `src/experiments/build_q1_gate1_evidence.py` | Reconstrucción estricta de Gate 1, deduplicación e inferencia clusterizada |
| E4 | `src/experiments/build_q1_expansion_evidence.py` y su manifiesto | 360 jobs, ocho entornos, 13.680 filas brutas y 11.400 observaciones únicas |
| E5 | `src/experiments/run_quantum_integrity_gate.py` y su manifiesto | 165 celdas quantum-specific y nueve controles de aceptación |
| E6 | `manuscript/figures/` y `manuscript/tables/` | Evidencia visual/tabular reconstruible y copias verificadas por hash |
| E7 | `tests/` | Invariancias, equivalencia del kernel exacto, integración y blind regions |
| E8 | `manuscript/paper15_exact_statevector_validation.md` | Equivalencia con el evaluador Qiskit de referencia y aceleración documentada |
| E9 | `Q1_REPRODUCTION.md` | Instalación, reproducción, fail-closed checks y fronteras de claim |
| E10 | `manuscript/paper15_quantum_integrity_gate_summary.md` | Diseño, cobertura, efectos y límites del Gate D de simulador |
| E11 | `src/hsaas/contracts.py`, `src/hsaas/demo.py` y su manifiesto | Cuatro contratos, hash chain, decisiones fail-closed y seis escenarios |
| E12 | `pyproject.toml`, `.github/workflows/tests.yml` y `manuscript/HSaaS_DEMONSTRATOR.md` | CLI instalable, CI y documentación de Result 3.1 |

Los resultados pesados viven bajo `results/` y están vinculados por manifiestos
SHA-256. Las copias pequeñas destinadas a revisión viven en `manuscript/`.

## Trazabilidad por objetivo y subtarea

| Requisito ATHENA-AEGIS | Contribución demostrada en este artefacto | Evidencia | Estado | Gap para cierre completo |
|---|---|---|---|---|
| G3.1 — mecanismos y herramientas frente a vulnerabilidades quantum-specific | Contrato multicapa de provenance, equivalencia semántica, validación algebraica, estimación repetida y monitorización de salida | E1, E5, E6, E10 | Parcial alto | Validación contra compilador/scheduler malicioso, backend calibrado, multi-tenancy y QPU |
| 3.1.1 — vulnerabilidades y contramedidas en diseño | Mutaciones RZ dependientes de datos, cambio de repeticiones y common-unitary control; hash de circuito/parámetros y semantic probes | E5, E7, E10 | Parcial alto | Ampliar familias de circuitos y evaluar prevención/recuperación, no solo detección |
| 3.1.2 — amenazas en transpilation, scheduling y post-processing | Control de transpilation semánticamente equivalente; corrupciones asimétrica, diagonal y PSD-preserving en post-estimación | E5, E6, E10 | Parcial | Inyección maliciosa del compilador, layouts/seeds/optimization levels sistemáticos y scheduling real |
| 3.1.3 — vulnerabilidades y contramedidas de ejecución cuántica | Emuladores binomiales de 256/1.024 shots y repeated-estimation discrepancy | E5, E10 | Parcial | Noise model calibrado, metadata de job, ataques de ejecución y microbenchmark QPU |
| 3.1.4 — integridad y confidencialidad de datos | Blindness proofs para cambios de etiquetas; provenance y auditoría conjunta como controles mínimos | E1, E3, E4, E6 | Parcial alto en integridad | Confidencialidad, leakage y side channels no se evalúan |
| G3.2 — V&V de todos los pasos y su integración clásica | Protocolo de frontera/information set y demostrador HSaaS que enlazan datos, circuito simulado, kernel, predicción, labels y conclusión | E1, E3–E12 | Parcial alto | Desplegar el servicio y vincular la cadena a evidencia autenticada de backend/proveedor |
| 3.2.1 — V&V en diseño | Clean contract, canonical OpenQASM 3 hash, parámetros y equivalencia semántica | E5, E7, E10 | Parcial alto | Especificación formal y mayor diversidad de circuitos/algoritmos |
| 3.2.2 — V&V en transpilation y scheduling | Diferencia de provenance con preservación semántica bajo transpilation benigna | E5, E10 | Parcial | Scheduling ausente; faltan layouts, hardware constraints y ataques de compiler pass |
| 3.2.3 — V&V durante ejecución | Repetición estocástica controlada y comprobación de discrepancias | E5, E10 | Parcial | Ejecución en backend sampler/noisy calibrado y QPU |
| 3.2.4 — validación end-to-end de integración híbrida | Cuatro contratos ejecutables, hash chain y política `allow/hold/block` sobre seis escenarios | E1, E4–E12 | Parcial alto | Endpoint desplegado, firma/autenticación, persistencia y flujo operacional QPU |
| G3.3 — métricas, identificación de amenazas y enforcement | Auditabilidad condicional, matriz attack-to-sensor, blind regions y decisiones fail-closed ejecutables | E1, E3–E7, E11 | Cubierto como contribución metodológica | Calibrar thresholds/power/false alarms en operación y medir coste de enforcement |
| 3.3.1 — métricas de calidad, fiabilidad y seguridad en diseño | Impact locus, semantic kernel delta, provenance, cobertura por familia y checks algebraicos | E1, E5, E6 | Cubierto en el caso de estudio | Validación externa en otras familias de algoritmos cuánticos |
| 3.3.2 — criterios para transpilation, scheduling y post-processing | Política de transpilation aprobada, semantic probes, simetría/diagonal/PSD y repeated estimation | E1, E5, E10 | Parcial alto | Criterios de scheduling y calibración con umbrales operacionales |
| 3.3.3 — métodos de security assessment para QPU | Ninguna medición física; los shots son un emulador binomial explícito | E1, E10 | No cubierto | Campaña QPU reproducible con calibración, incertidumbre y provenance |
| “3.4.4” — herramientas end-to-end desde diseño hasta interpretación | Runners, builders, manifiestos, tests, figuras, paquete instalable, CLI, CI y demostrador HSaaS | E3–E12 | Parcial alto como prototipo empaquetado | Endpoint de producción, firma, operación QPU y release archivada con DOI |

## Trazabilidad por resultado contractual

| Resultado | Entregable que ya aporta el repositorio | Estado de este paper | Evidencia mínima que falta |
|---|---|---|---|
| Result 3.1 [SOFTWARE] — suite para fiabilidad y seguridad de diseño a interpretación | Kernel exacto, benchmark, Gate D, contratos HSaaS, CLI, CI, tests, políticas fail-closed y manifiestos | Parcial alto como prototipo empaquetado | Servicio de producción, firma/autenticación, release/DOI y tier operacional |
| Result 3.2 [REPORT] — metodologías, herramientas y métricas | Manuscrito V11, estrategia, notas de validación, resúmenes y esta matriz | Parcial alto | Manuscrito final en plantilla de revista, threat-model card, informe formal del proyecto y referencia a release/DOI |
| WP5 Task 5.2 — diseminación científica | Artículo completo, revisión de novedad, artefacto reproducible y paquete de envío | Cubierto al enviar/publicar | Incorporar la referencia bibliográfica y el DOI al informe de diseminación |
| WP5 Task 5.1 / Result 5.1 — caso Fleet Management | Ninguna implementación ni validación operacional de Fleet Management | No cubierto por este paper | Pertenece al trabajo coordinado/posterior; no inferir cobertura por usar datos NIDS o el demostrador HSaaS |

## Evidencia cuantitativa que puede declararse

- Gate 1: 7.980 filas brutas, 4.560 observaciones únicas y 3.420 repeticiones SVC eliminadas tras comprobar igualdad.
- Expansión: 360/360 jobs, ocho entornos, 13.680 filas brutas y 11.400 observaciones únicas.
- Blind region replicada: 3.600/3.600 perturbaciones de etiquetas invariantes para evidencia de features+predicción; 1.800/1.800 prior-preserving también invariantes para el marginal de etiquetas.
- Cierre incremental: las 2.184 observaciones label-side con impacto positivo tienen evidencia conjunta no nula.
- Gate D simulador: 165/165 celdas y 9/9 comprobaciones de aceptación superadas.
- Demostrador HSaaS: 6/6 escenarios, 8/8 comprobaciones y todas las hash chains verificadas.
- Artefacto: 15/15 tests superados y auditoría SHA-256 completa de inputs, outputs y copias publicables.

Estas cifras describen el diseño ejecutado. No son repeticiones poblacionales ni
evidencia de hardware cuántico.

## Frontera entre este paper y el trabajo posterior

Este paper se cierra con la evidencia de simulador y el prototipo local. QPU,
backend calibrado, scheduling, seguridad del proveedor, multi-tenancy,
despliegue HSaaS y Fleet Management operacional no son “experimentos pendientes”
para su envío: son capacidades distintas que deben atribuirse a un trabajo
posterior o a otros entregables del proyecto.

Para cerrar este artefacto solo son necesarios el manuscrito, el material
suplementario, la matriz de amenaza, los tests/CI, el manifiesto de release, la
atribución administrativa verificada y el archivado con DOI. Esos elementos no
amplían el alcance científico.

## Veredicto de cobertura

El paper es una contribución científica clara y diferenciada para G3.2/G3.3, y
el Gate D de simulador aporta contenido quantum-specific real pero acotado para
G3.1. Es defendible como paper doctoral y como evidencia sustantiva del trabajo
Deusto. En WP5 justifica diseminación científica (Task 5.2) una vez enviado o
publicado; no justifica Task 5.1/Result 5.1 ni una cobertura integral de
ATHENA-AEGIS. Esta limitación de atribución no reduce el claim científico del
artículo: evita que se use para probar trabajo operacional que no contiene.
