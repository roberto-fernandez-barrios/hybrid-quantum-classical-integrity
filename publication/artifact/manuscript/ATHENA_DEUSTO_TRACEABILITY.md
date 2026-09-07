# Matriz de trazabilidad ATHENA-AEGIS — contribución Deusto

Fecha de corte: 7 de septiembre de 2026 (artefacto 1.3.0, cierre científico
definitivo del Paper 1.5)  
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
| E2 | `manuscript/FORMAL_CORE.md`, `manuscript/FORMAL_REVIEW_1.3.0.md` | Núcleo formal completo con demostraciones (Lema 1, Proposiciones 1–7, Corolarios 1–3, contraejemplos C1–C9) y su revisión enunciado a enunciado con tests |
| E3 | `src/experiments/build_q1_gate1_evidence.py` y su manifiesto | Reconstrucción estricta de Gate 1, deduplicación e inferencia clusterizada |
| E4 | `src/experiments/build_q1_expansion_evidence.py` y su manifiesto | 360 jobs, ocho entornos, 13.680 filas brutas y 11.400 observaciones únicas |
| E5 | `src/experiments/run_quantum_integrity_gate.py` y su manifiesto | 165 celdas quantum-specific y nueve controles de aceptación; instancia de la Proposición 7 |
| E6 | `manuscript/figures/`, `manuscript/tables/`, `publication/tdsc/tables/` | Evidencia visual/tabular generada desde CSV manifestados (incl. macros numéricas) |
| E7 | `tests/` | Invariancias, kernel exacto, contratos, regla conformal (tests exhaustivos), núcleo formal (fuerza bruta), capa de política, evidencia comprometida |
| E8 | `manuscript/paper15_exact_statevector_validation.md` | Equivalencia con el evaluador Qiskit de referencia y aceleración documentada; réplica exacta en Gate A |
| E9 | `Q1_REPRODUCTION.md`, `scripts/verify_datasets.py` | Instalación, fuentes oficiales de datos, hashes esperados, staging, verificación del artefacto congelado y replay completo |
| E10 | `manuscript/paper15_quantum_integrity_gate_summary.md` | Diseño, cobertura, efectos y límites del gate cuántico de simulador |
| E11 | `src/hsaas/contracts.py`, `src/hsaas/demo.py` y su manifiesto | Cuatro contratos, hash chain, lógica fail-closed de los contratos y seis escenarios |
| E12 | `src/hsaas/policy.py`, `src/integrity/family_calibration.py`, `src/experiments/build_q1_policy_evidence.py` y su manifiesto | Calibración conformal a nivel de decisión (Gate F, regla 1.2.0 como comparación) y evaluación offline end-to-end `allow/hold/block` con coste benigno (Gate D), preregistradas en `paper15_v12_policy_prereg.md` + enmienda A2 en `paper15_v13_prereg.md` |
| E13 | `manuscript/paper15_v11_reinforcement_prereg.md`, `src/experiments/build_q1_reinforcement_evidence.py` y su manifiesto | Gates de refuerzo preregistrados (1.1.0): calibración nula por sensor, ablación de preprocesado, baselines ajustados |
| E14 | `manuscript/ADVERSARY_MODEL.md`, `manuscript/THREAT_MODEL_CARD.md` | Modelo de adversario/fallo por clase de intervención, raíces de confianza, exclusiones; F5 ejecutado |
| E15 | `pyproject.toml`, `.github/workflows/tests.yml`, `manuscript/HSaaS_DEMONSTRATOR.md` | CLI instalable, CI y documentación del prototipo |
| E16 | `publication/artifact/`, `src/experiments/verify_publication_artifact.py`, `src/experiments/make_release_status.py` | Artefacto compacto con siete manifiestos, verificador fail-closed y fuente única de recuentos |
| E17 | `manuscript/paper15_v13_prereg.md`, `src/attacks/cluster_preserving.py`, `src/experiments/run_v13_f5_queue.py`, `src/experiments/build_q1_adversarial_evidence.py` y su manifiesto | Gate A preregistrado: atacante adaptativo que preserva el fingerprint (240 jobs, réplica exacta de controles) |

## Trazabilidad por objetivo y subtarea

| Requisito ATHENA-AEGIS | Contribución demostrada en este artefacto | Evidencia | Estado | Gap para cierre completo (Paper 2.5 salvo indicación) |
|---|---|---|---|---|
| G3.1 — mecanismos y herramientas frente a vulnerabilidades quantum-specific | Contrato multicapa de provenance, equivalencia semántica, validación algebraica, estimación repetida y monitorización de salida; la rama cuántica formalizada como instancia del retículo de vistas (Prop. 7: provenance ⊐ semántica ⊐ álgebra ⊐ salida; ruido de shots convierte el anclaje exacto en test calibrado) | E1, E2, E5, E6, E10 | Parcial alto | Validación frente a compilador/scheduler malicioso, backend calibrado, multi-tenancy y QPU |
| 3.1.1 — vulnerabilidades y contramedidas en diseño | Mutaciones RZ dependientes de datos, cambio de repeticiones y common-unitary como control; hash de circuito/parámetros y probes semánticos; clase adversarial declarada | E5, E7, E10, E14 | Parcial alto | Ampliar familias de circuitos y evaluar prevención/recuperación |
| 3.1.2 — amenazas en transpilation, scheduling y post-processing | Control de transpilation semánticamente equivalente (clase aprobada [C]); corrupciones asimétrica, diagonal y PSD-preserving (esta última como atacante adaptativo) | E5, E6, E10, E14 | Parcial | Inyección maliciosa del compilador, layouts/seeds/optimization levels sistemáticos y scheduling real |
| 3.1.3 — vulnerabilidades y contramedidas de ejecución cuántica | Emuladores binomiales de 256/1.024 shots y repeated-estimation discrepancy; `hold` para estimación estocástica aprobada; Prop. 7(iii) explica por qué el anclaje exacto es inútil bajo ruido y hace falta un nulo calibrado | E5, E10, E2 | Parcial | Noise model calibrado, metadata de job, ataques de ejecución y campaña QPU |
| 3.1.4 — integridad y confidencialidad de datos | Regiones ciegas exactas del camino de etiquetas; Proposición 3 (materialidad ⇒ separabilidad agregada, para toda métrica función de la matriz de confusión); Corolario 3 (referencia agregada confiable para integridad de conclusión, item-alineada para identidad); Proposición 6 (sin raíz no controlada no hay autenticación local); atacante adaptativo F5 sobre el camino de features (Gate A) | E1, E2, E3, E4, E12, E17 | Parcial alto en integridad | Confidencialidad: ver estrategia más abajo |
| G3.2 — V&V de todos los pasos y su integración clásica | Modelo de observación (estados, vistas, refinamiento, referencias confiables) y prototipo HSaaS que enlaza datos, circuito simulado, kernel, predicción, labels y conclusión; composición contrato+política | E1, E2, E11, E12 | Parcial alto | Desplegar el servicio y vincular la cadena a evidencia autenticada de backend/proveedor |
| 3.2.1 — V&V en diseño | Clean contract, canonical OpenQASM 3 hash, parámetros y equivalencia semántica | E5, E7, E10 | Parcial alto | Especificación formal y mayor diversidad de circuitos/algoritmos |
| 3.2.2 — V&V en transpilation y scheduling | Diferencia de provenance con preservación semántica bajo transpilation benigna; clase "equivalencia aprobada" en la política | E5, E10, E12 | Parcial | Scheduling ausente; faltan layouts, hardware constraints y ataques de compiler pass |
| 3.2.3 — V&V durante ejecución | Repetición estocástica controlada y comprobación de discrepancias | E5, E10 | Parcial | Ejecución en backend sampler/noisy calibrado y QPU |
| 3.2.4 — validación end-to-end de integración híbrida | Cuatro contratos ejecutables, hash chain, política calibrada e information-aware `allow/hold/block` evaluada **offline** sobre 24.000 observaciones congeladas; composición con los seis escenarios | E1, E11, E12, E15 | Parcial alto | Endpoint desplegado, firma/autenticación, persistencia y flujo operacional QPU |
| G3.3 — métricas, identificación de amenazas y enforcement | Auditabilidad como propiedad de (clase, vista, referencias); regiones ciegas estructurales, calibradas y adaptativas; **nivel de falsas alarmas a nivel de decisión con premisa exacta** (regla conformal, 10/201 bajo intercambiabilidad; 0,056/0,058/0,048/0,053 en el diseño ejecutado; la regla 1.2.0 tenía una garantía falsa y su exceso era mayoritariamente sesgo de regla); **coste de enforcement medido en ambos lados**: unsafe allows, false holds, interrupción benigna (el régimen confiable interrumpe el 52 % de la variación benigna), containment por régimen y política (Gate D); **atacante adaptativo ejecutado** que evade los sensores calibrados (Gate A); modelo de adversario explícito | E1, E2, E12, E13, E14, E17 | **Cubierto como contribución metodológica en diseño fijo y simulador** | Calibración condicionada al contexto de ejecución bajo no estacionariedad, abstención por fuera de soporte, recuperación y evaluación a nivel de servicio (Paper 2.5) |
| 3.3.1 — métricas de calidad, fiabilidad y seguridad en diseño | Cambio de conclusión con signo (incl. mejoras aparentes), impact locus, semantic kernel delta, provenance, cobertura por familia, checks algebraicos, interrupción benigna y no material | E1, E5, E6, E12 | Cubierto en el caso de estudio | Validación externa en otras familias de algoritmos cuánticos |
| 3.3.2 — criterios para transpilation, scheduling y post-processing | Política de transpilation aprobada, semantic probes, simetría/diagonal/PSD, repeated estimation y composición `max` en el retículo `allow<hold<block` | E1, E5, E10, E12 | Parcial alto | Criterios de scheduling y calibración con umbrales operacionales en hardware |
| 3.3.3 — métodos de security assessment para QPU | Ninguna medición física; los shots son un emulador binomial explícito | E1, E10 | No cubierto | Campaña QPU reproducible con calibración, incertidumbre y provenance (Paper 2.5) |
| "3.4.4" — herramientas end-to-end desde diseño hasta interpretación | Runners, builders, manifiestos, verificador, tests, figuras/tablas generadas, paquete instalable, CLI, CI, demostrador HSaaS, capa de política y gate adversarial | E3–E7, E11, E12, E15, E16, E17 | Parcial alto como prototipo empaquetado | Endpoint de producción, firma, operación QPU |

## Trazabilidad por resultado contractual

| Resultado | Entregable que ya aporta el repositorio | Estado de este paper | Evidencia mínima que falta |
|---|---|---|---|
| Result 3.1 [SOFTWARE] — suite para fiabilidad y seguridad de diseño a interpretación | Kernel exacto, benchmark, gate cuántico, contratos HSaaS, calibración conformal, capa de política, suite adversarial, CLI, CI, tests, manifiestos, verificador, artefacto archivado con DOI | Parcial alto como prototipo empaquetado | Servicio de producción, firma/autenticación, tier operacional QPU |
| Result 3.2 [REPORT] — metodologías, herramientas y métricas | Manuscrito TDSC y suplemento, núcleo formal y su revisión, modelo de adversario, threat-model card, preregistros con enmiendas, resúmenes, esta matriz, release archivada | Parcial alto | Informe formal del proyecto que integre 1.5 y 2.5; sección de confidencialidad (ver abajo) |
| WP5 Task 5.2 — diseminación científica | Artículo completo, revisión de novedad, artefacto reproducible y paquete de envío | Cubierto al enviar/publicar | Incorporar la referencia bibliográfica y el DOI al informe de diseminación |
| WP5 Task 5.1 / Result 5.1 — caso Fleet Management | Ninguna implementación ni validación operacional de Fleet Management | No cubierto por este paper | AEGIS slice del demostrador FMS (Paper 2.5); no inferir cobertura por usar datos NIDS o el demostrador HSaaS |

## Confidencialidad (Subtask 3.1.4): obligación real y estrategia

La memoria asigna a Deusto la subtarea 3.1.4 "Ensuring data integrity and
confidentiality (24 months)" dentro de la Task 3.1, y el WP3 menciona
confidencialidad como una de las propiedades comprometidas por
input/output manipulation. La obligación es, por tanto, de Deusto/WP3, pero
no está formulada como una tarea experimental de canal lateral ni de
criptografía; es "ensuring", es decir, metodologías y herramientas.

Decisión: el Paper 1.5 no incorpora un experimento de confidencialidad. Su
objeto científico es la integridad de la cadena de evidencia; un experimento
de confidencialidad añadido para marcar una casilla debilitaría el artículo
sin cerrar la obligación. La estrategia queda así:

1. **Paper 2.5 (subtarea concreta, §23.4 del plan):** matriz de exposición de
   metadatos por principal (cliente, gateway, proveedor, verificador) sobre el
   `ExecutionContext` y el sobre de evidencia firmado; controles de
   minimización/redacción/bucketing con coste medido en utilidad de la
   auditoría; evaluación de la superficie de fuga de tamaño de circuito y
   problema a partir de la información observable por cada principal;
   posicionamiento frente al canal temporal de Quantum Leak. Solo lo que sea
   medible de forma ética con la infraestructura disponible.
2. **Entregable técnico del proyecto (Result 3.2, no ciencia del 2.5):** las
   partes de la confidencialidad que dependen del proveedor (aislamiento
   multi-tenant, canales laterales físicos) se documentan como threat model y
   controles de exposición, con la frontera explícita de lo no medible, en el
   informe del proyecto.
3. **Regla:** nunca declarar 3.1.4 "cubierto" en confidencialidad por usar
   HTTPS, hashes o una firma local; solo cuando exista una matriz de
   exposición verificable y controles evaluados.

## Evidencia cuantitativa que puede declararse

- Gate 1: 7.980 filas brutas, 4.560 observaciones únicas y 3.420 repeticiones SVC eliminadas tras comprobar igualdad.
- Expansión: 360/360 jobs, ocho entornos (cinco CICIDS2017, dos UNSW-NB15, uno ToN-IoT), 13.680 filas brutas y 11.400 observaciones únicas.
- Región ciega replicada: 3.600/3.600 intervenciones de etiquetas invariantes para evidencia de features+predicción; 1.800/1.800 prior-preserving también invariantes para el marginal.
- Cambio de conclusión con signo (etiquetas, expansión): 2.184 bajan, 983 no cambian, 433 suben; las 2.617 con cambio tienen evidencia conjunta item-alineada no nula (Gate 1: 1.276/105/59).
- Calibración a nivel de decisión (regla conformal, nivel exacto 10/201): FPR 0,056 / 0,058 / 0,048 / 0,053 (I_X / I_XF / I_Ym / I_XFY) frente a 0,061 / 0,073 / 0,048 / 0,079 (regla 1.2.0, garantía falsa) y 0,125 / 0,203 / 0,048 / 0,259 (unión); sesgo de regla +0,005 / +0,015 / 0 / +0,025; efecto de diseño +0,006 / +0,008 / −0,003 / +0,003; unidad de inferencia = clúster (entorno, split).
- Evaluación offline end-to-end: 7.008 observaciones materiales; unsafe allows bajo P2 conformal 4.496 / 4.365 / 7.008 / 4.390 (regímenes batch) y 0 bajo la referencia item-alineada confiable, que interrumpe 544 + 85 de 1.200 controles benignos (52 %).
- Gate A: 240/240 jobs; réplica exacta de controles; detección conformal del atacante adaptativo 0,01–0,34 (I_X) y 0,06–0,66 (I_XF) a intensidades iguales frente a 0,96–1,00; 3.418 filas materiales de 6.000; P2 sirve 1.328 / 959 / 1.006; régimen confiable 0.
- Gate cuántico de simulador: 165/165 celdas y 9/9 comprobaciones de aceptación.
- Demostrador HSaaS: 6/6 escenarios, 8/8 comprobaciones, composición con la política reproducida 6/6.
- Artefacto: siete manifiestos de evidencia, verificador fail-closed; recuento de tests, salidas y ficheros en `publication/RELEASE_STATUS.md`.

Estas cifras describen el diseño ejecutado. No son repeticiones poblacionales ni
evidencia de hardware cuántico.

## Frontera entre Paper 1.5 y Paper 2.5

**Paper 1.5 (este artefacto, cerrado en 1.3.0):** auditabilidad de integridad
condicionada a la información y a las referencias confiables, con regiones
ciegas exactas, calibradas y adaptativas; nivel de falsas alarmas a nivel de
decisión con premisa exacta (regla conformal); política calibrada y
evaluada **offline** end-to-end con su coste benigno; atacante adaptativo que
preserva el fingerprint; contratos y hash chain; rama cuántica como
instancia del retículo; todo en diseño fijo, local y en simulador. La
calibración de falsas alarmas, los contratos, la integridad por hash chain y
la formalización de regiones ciegas **pertenecen ya a 1.5** y no pueden
presentarse como novedad del 2.5.

**Paper 2.5 (plan en `Proyecto/PLAN_ATHENA_AEGIS_DEUSTO_ABSOLUTE_CEILING.md`, §22–23):**
assurance operacional longitudinal y condicionada al contexto de ejecución
sobre ejecución real/QPU: validez de la calibración en el tiempo (la
Proposición 5(b) del 1.5 dice exactamente qué premisa hay que vigilar),
detección de contexto fuera de soporte y abstención, garantías operacionales
en múltiples ventanas, recuperación/fallback/rollback, continuación insegura y
time-to-recovery, evidencia de proveedor/contexto sin confundir firma local
con attestation del proveedor, deriva de scheduling, la AEGIS slice del
demostrador FMS y la subtarea de confidencialidad.

QPU, backend calibrado, scheduling, seguridad del proveedor, multi-tenancy,
despliegue HSaaS y Fleet Management operacional no son "experimentos
pendientes" del 1.5: son capacidades distintas atribuidas al 2.5 u otros
entregables del proyecto.

## Veredicto de cobertura

El paper es una contribución científica clara y diferenciada para G3.2/G3.3
(incluida la calibración conformal a nivel de decisión, el coste de
enforcement medido en ambos lados y el atacante adaptativo ejecutado), y el
gate cuántico de simulador, ahora formalizado como instancia del retículo,
aporta contenido quantum-specific real pero acotado para G3.1. Es defendible
como paper doctoral y como evidencia sustantiva del trabajo Deusto. En WP5
justifica diseminación científica (Task 5.2) una vez enviado o publicado; no
justifica Task 5.1/Result 5.1 ni una cobertura integral de ATHENA-AEGIS.
Esta limitación de atribución no reduce el claim científico del artículo:
evita que se use para probar trabajo operacional que no contiene.
