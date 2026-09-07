# Matriz de trazabilidad ATHENA-AEGIS — contribución Deusto

Fecha de corte: 7 de septiembre de 2026 (artefacto 1.2.0)  
Artefacto científico: *Observational Indistinguishability and Integrity Blind
Regions Across the Evidence Boundaries of Hybrid Quantum-Classical Kernel
Workflows* (Paper 1.5; título anterior *Information-Set Conditional Integrity
Auditing for Hybrid Quantum-Classical Kernel Workflows*).

## Propósito y regla de lectura

Esta matriz relaciona las obligaciones científicas y técnicas del subproyecto
ATHENA-AEGIS (memoria científico-técnica, WP3 pp. 16–17 y WP5 p. 18) con
evidencia verificable del repositorio. Distingue cuatro estados:

- **Cubierto**: existe evidencia reproducible que responde directamente al requisito.
- **Parcial alto**: la contribución científica está demostrada, pero falta su cierre operacional o de producto.
- **Parcial**: existe un demostrador relevante, pero no cubre toda la capacidad descrita.
- **No cubierto**: el artefacto actual no contiene evidencia para sostener el requisito.

El estado se refiere a este repositorio y a este paper, no al avance total del
equipo Deusto. La memoria etiqueta literalmente como "Subtask 3.4.4" la última
subtarea de herramientas end-to-end, inmediatamente después de 3.3.3; se
conserva esa numeración. Ningún requisito se marca como cubierto porque el
paper lo mencione: solo cuando un revisor puede reproducir o inspeccionar la
evidencia que lo satisface. Los recuentos autoritativos (manifiestos,
salidas, ficheros, tests, páginas, hashes) están en
`publication/RELEASE_STATUS.md`, generado.

## Índice de evidencia

| ID | Evidencia | Función probatoria |
|---|---|---|
| E1 | `publication/tdsc/main.tex`, `publication/tdsc/supplement.tex` | Claim, formalización, modelo de adversario, métodos, resultados y límites integrados |
| E2 | `manuscript/FORMAL_CORE.md` | Núcleo formal completo con demostraciones (Lema 1, Proposiciones 1–6, Corolarios 1–2, contraejemplos C1–C8) |
| E3 | `src/experiments/build_q1_gate1_evidence.py` y su manifiesto | Reconstrucción estricta de Gate 1, deduplicación e inferencia clusterizada |
| E4 | `src/experiments/build_q1_expansion_evidence.py` y su manifiesto | 360 jobs, ocho entornos, 13.680 filas brutas y 11.400 observaciones únicas |
| E5 | `src/experiments/run_quantum_integrity_gate.py` y su manifiesto | 165 celdas quantum-specific y nueve controles de aceptación |
| E6 | `manuscript/figures/`, `manuscript/tables/`, `publication/tdsc/tables/` | Evidencia visual/tabular generada desde CSV manifestados (incl. macros numéricas) |
| E7 | `tests/` | Invariancias, kernel exacto, contratos, calibración por familia, capa de política, evidencia comprometida |
| E8 | `manuscript/paper15_exact_statevector_validation.md` | Equivalencia con el evaluador Qiskit de referencia y aceleración documentada |
| E9 | `Q1_REPRODUCTION.md`, `scripts/verify_datasets.py` | Instalación, fuentes oficiales de datos, hashes esperados, staging, verificación del artefacto congelado y replay completo |
| E10 | `manuscript/paper15_quantum_integrity_gate_summary.md` | Diseño, cobertura, efectos y límites del gate cuántico de simulador |
| E11 | `src/hsaas/contracts.py`, `src/hsaas/demo.py` y su manifiesto | Cuatro contratos, hash chain, decisiones fail-closed y seis escenarios |
| E12 | `src/hsaas/policy.py`, `src/integrity/family_calibration.py`, `src/experiments/build_q1_policy_evidence.py` y su manifiesto | Calibración a nivel de decisión (Gate F) y evaluación end-to-end `allow/hold/block` (Gate D), preregistradas en `manuscript/paper15_v12_policy_prereg.md` |
| E13 | `manuscript/paper15_v11_reinforcement_prereg.md`, `src/experiments/build_q1_reinforcement_evidence.py` y su manifiesto | Gates de refuerzo preregistrados (1.1.0): calibración nula por sensor, ablación de preprocesado, baselines ajustados |
| E14 | `manuscript/ADVERSARY_MODEL.md`, `manuscript/THREAT_MODEL_CARD.md` | Modelo de adversario/fallo por clase de intervención, raíces de confianza, exclusiones |
| E15 | `pyproject.toml`, `.github/workflows/tests.yml`, `manuscript/HSaaS_DEMONSTRATOR.md` | CLI instalable, CI y documentación del prototipo |
| E16 | `publication/artifact/`, `src/experiments/verify_publication_artifact.py`, `src/experiments/make_release_status.py` | Artefacto compacto con seis manifiestos, verificador fail-closed y fuente única de recuentos |

## Trazabilidad por objetivo y subtarea

| Requisito ATHENA-AEGIS | Contribución demostrada en este artefacto | Evidencia | Estado | Gap para cierre completo (Paper 2.5 salvo indicación) |
|---|---|---|---|---|
| G3.1 — mecanismos y herramientas frente a vulnerabilidades quantum-specific | Contrato multicapa de provenance, equivalencia semántica, validación algebraica, estimación repetida y monitorización de salida; el gate cuántico como instancia del mismo retículo de vistas (hash ⊐ kernel ⊐ álgebra ⊐ salida) | E1, E2, E5, E6, E10 | Parcial alto | Validación frente a compilador/scheduler malicioso, backend calibrado, multi-tenancy y QPU |
| 3.1.1 — vulnerabilidades y contramedidas en diseño | Mutaciones RZ dependientes de datos, cambio de repeticiones y common-unitary como control; hash de circuito/parámetros y probes semánticos; clase adversarial declarada | E5, E7, E10, E14 | Parcial alto | Ampliar familias de circuitos y evaluar prevención/recuperación |
| 3.1.2 — amenazas en transpilation, scheduling y post-processing | Control de transpilation semánticamente equivalente; corrupciones asimétrica, diagonal y PSD-preserving (esta última como atacante adaptativo) | E5, E6, E10, E14 | Parcial | Inyección maliciosa del compilador, layouts/seeds/optimization levels sistemáticos y scheduling real |
| 3.1.3 — vulnerabilidades y contramedidas de ejecución cuántica | Emuladores binomiales de 256/1.024 shots y repeated-estimation discrepancy; `hold` para estimación estocástica aprobada | E5, E10 | Parcial | Noise model calibrado, metadata de job, ataques de ejecución y campaña QPU |
| 3.1.4 — integridad y confidencialidad de datos | Regiones ciegas exactas del camino de etiquetas; Proposición 3 (materialidad ⇒ separabilidad en la vista conjunta); referencia item-alineada autenticada como condición de identificación exacta; Proposición 6 (sin raíz no controlada no hay garantía local) | E1, E2, E3, E4, E12 | Parcial alto en integridad | Confidencialidad, leakage y side channels no se evalúan |
| G3.2 — V&V de todos los pasos y su integración clásica | Modelo de observación (estados, vistas, refinamiento, referencias confiables) y prototipo HSaaS que enlaza datos, circuito simulado, kernel, predicción, labels y conclusión; composición contrato+política | E1, E2, E11, E12 | Parcial alto | Desplegar el servicio y vincular la cadena a evidencia autenticada de backend/proveedor |
| 3.2.1 — V&V en diseño | Clean contract, canonical OpenQASM 3 hash, parámetros y equivalencia semántica | E5, E7, E10 | Parcial alto | Especificación formal y mayor diversidad de circuitos/algoritmos |
| 3.2.2 — V&V en transpilation y scheduling | Diferencia de provenance con preservación semántica bajo transpilation benigna; clase "equivalencia aprobada" en la política | E5, E10, E12 | Parcial | Scheduling ausente; faltan layouts, hardware constraints y ataques de compiler pass |
| 3.2.3 — V&V durante ejecución | Repetición estocástica controlada y comprobación de discrepancias | E5, E10 | Parcial | Ejecución en backend sampler/noisy calibrado y QPU |
| 3.2.4 — validación end-to-end de integración híbrida | Cuatro contratos ejecutables, hash chain, política calibrada e information-aware `allow/hold/block` evaluada sobre 24.000 observaciones congeladas; composición con los seis escenarios | E1, E11, E12, E15 | Parcial alto | Endpoint desplegado, firma/autenticación, persistencia y flujo operacional QPU |
| G3.3 — métricas, identificación de amenazas y enforcement | Auditabilidad como propiedad de (clase, vista, referencias); regiones ciegas estructurales vs calibradas; **presupuesto de falsas alarmas a nivel de decisión** (Gate F: 0,061–0,079 frente a 0,125–0,259 de la unión); **coste de enforcement medido**: unsafe allows, false holds, containment por régimen y política (Gate D); modelo de adversario explícito | E1, E2, E12, E13, E14 | **Cubierto como contribución metodológica en diseño fijo y simulador** | Calibración condicionada al contexto de ejecución bajo no estacionariedad, abstención por fuera de soporte, recuperación y evaluación a nivel de servicio (Paper 2.5) |
| 3.3.1 — métricas de calidad, fiabilidad y seguridad en diseño | Cambio de conclusión con signo (incl. mejoras aparentes), impact locus, semantic kernel delta, provenance, cobertura por familia y checks algebraicos | E1, E5, E6, E12 | Cubierto en el caso de estudio | Validación externa en otras familias de algoritmos cuánticos |
| 3.3.2 — criterios para transpilation, scheduling y post-processing | Política de transpilation aprobada, semantic probes, simetría/diagonal/PSD, repeated estimation y composición `max` en el retículo `allow<hold<block` | E1, E5, E10, E12 | Parcial alto | Criterios de scheduling y calibración con umbrales operacionales en hardware |
| 3.3.3 — métodos de security assessment para QPU | Ninguna medición física; los shots son un emulador binomial explícito | E1, E10 | No cubierto | Campaña QPU reproducible con calibración, incertidumbre y provenance (Paper 2.5) |
| "3.4.4" — herramientas end-to-end desde diseño hasta interpretación | Runners, builders, manifiestos, verificador, tests, figuras/tablas generadas, paquete instalable, CLI, CI, demostrador HSaaS y capa de política | E3–E7, E11, E12, E15, E16 | Parcial alto como prototipo empaquetado | Endpoint de producción, firma, operación QPU |

## Trazabilidad por resultado contractual

| Resultado | Entregable que ya aporta el repositorio | Estado de este paper | Evidencia mínima que falta |
|---|---|---|---|
| Result 3.1 [SOFTWARE] — suite para fiabilidad y seguridad de diseño a interpretación | Kernel exacto, benchmark, gate cuántico, contratos HSaaS, calibración por familia, capa de política, CLI, CI, tests, manifiestos, verificador, artefacto archivado con DOI | Parcial alto como prototipo empaquetado | Servicio de producción, firma/autenticación, tier operacional QPU |
| Result 3.2 [REPORT] — metodologías, herramientas y métricas | Manuscrito TDSC y suplemento, núcleo formal, modelo de adversario, threat-model card, preregistros y resúmenes, esta matriz, release archivada | Parcial alto | Informe formal del proyecto que integre 1.5 y 2.5 |
| WP5 Task 5.2 — diseminación científica | Artículo completo, revisión de novedad, artefacto reproducible y paquete de envío | Cubierto al enviar/publicar | Incorporar la referencia bibliográfica y el DOI al informe de diseminación |
| WP5 Task 5.1 / Result 5.1 — caso Fleet Management | Ninguna implementación ni validación operacional de Fleet Management | No cubierto por este paper | AEGIS slice del demostrador FMS (Paper 2.5); no inferir cobertura por usar datos NIDS o el demostrador HSaaS |

## Evidencia cuantitativa que puede declararse

- Gate 1: 7.980 filas brutas, 4.560 observaciones únicas y 3.420 repeticiones SVC eliminadas tras comprobar igualdad.
- Expansión: 360/360 jobs, ocho entornos, 13.680 filas brutas y 11.400 observaciones únicas.
- Región ciega replicada: 3.600/3.600 intervenciones de etiquetas invariantes para evidencia de features+predicción; 1.800/1.800 prior-preserving también invariantes para el marginal.
- Cambio de conclusión con signo (etiquetas, expansión): 2.184 bajan, 983 no cambian, 433 suben; las 2.617 con cambio tienen evidencia conjunta item-alineada no nula (Gate 1: 1.276/105/59).
- Calibración a nivel de decisión: FPR 0,061 / 0,073 / 0,048 / 0,079 (I_X / I_XF / I_Ym / I_XFY) frente a 0,125 / 0,203 / 0,048 / 0,259 de la unión de reglas por sensor; unidad de inferencia = clúster (entorno, split).
- Evaluación end-to-end: 7.008 observaciones materiales; unsafe allows bajo política calibrada 4.494 / 4.327 / 7.008 / 4.322 (regímenes batch) y 0 bajo la referencia item-alineada confiable con 0 false holds.
- Gate cuántico de simulador: 165/165 celdas y 9/9 comprobaciones de aceptación.
- Demostrador HSaaS: 6/6 escenarios, 8/8 comprobaciones, composición con la política reproducida 6/6.
- Artefacto: seis manifiestos de evidencia, 65 salidas manifestadas, verificador fail-closed; recuento de tests y ficheros en `publication/RELEASE_STATUS.md`.

Estas cifras describen el diseño ejecutado. No son repeticiones poblacionales ni
evidencia de hardware cuántico.

## Frontera entre Paper 1.5 y Paper 2.5

**Paper 1.5 (este artefacto):** auditabilidad de integridad condicionada a la
información y a las referencias confiables, con regiones ciegas exactas y
calibradas, presupuesto de falsas alarmas a nivel de decisión, política
fail-closed calibrada y evaluada end-to-end, contratos y hash chain, todo en
diseño fijo, local y en simulador. La calibración de falsas alarmas "simple",
los contratos y la integridad por hash chain **pertenecen ya a 1.5** y no
pueden presentarse como novedad del 2.5.

**Paper 2.5 (plan en `Proyecto/PLAN_ATHENA_AEGIS_DEUSTO_ABSOLUTE_CEILING.md`):**
assurance operacional longitudinal y condicionada al contexto de ejecución
sobre ejecución real/QPU: no estacionariedad y deriva de calibración,
detección de contexto fuera de soporte y abstención, garantías operacionales
calibradas con ventanas múltiples, recuperación/fallback/rollback,
continuación insegura y time-to-recovery, evidencia de proveedor/contexto sin
confundir firma local con attestation del proveedor, deriva de scheduling, y
la AEGIS slice del demostrador FMS.

QPU, backend calibrado, scheduling, seguridad del proveedor, multi-tenancy,
despliegue HSaaS y Fleet Management operacional no son "experimentos
pendientes" del 1.5: son capacidades distintas atribuidas al 2.5 u otros
entregables del proyecto.

## Veredicto de cobertura

El paper es una contribución científica clara y diferenciada para G3.2/G3.3
(incluida la calibración a nivel de decisión y el coste de enforcement
medido), y el gate cuántico de simulador aporta contenido quantum-specific
real pero acotado para G3.1. Es defendible como paper doctoral y como
evidencia sustantiva del trabajo Deusto. En WP5 justifica diseminación
científica (Task 5.2) una vez enviado o publicado; no justifica Task
5.1/Result 5.1 ni una cobertura integral de ATHENA-AEGIS. Esta limitación de
atribución no reduce el claim científico del artículo: evita que se use para
probar trabajo operacional que no contiene.
