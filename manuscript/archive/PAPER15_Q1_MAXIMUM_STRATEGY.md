# Estrategia de techo Q1 para Paper 1.5

## Veredicto ejecutivo

El manuscrito V10 partia de un alcance workshop: un unico benchmark derivado de CICIDS, muestras de 128/128, simulacion de kernels de fidelidad, una sola pareja OOD y una metrica de *stealth* heuristica. La expansion ya resuelve estabilidad, escala y validez externa sobre casos de estudio fijados, pero todavia no cubre el ciclo cuantico completo de seguridad de ATHENA-AEGIS.

El techo cientifico no consiste en presentar "QSVC-ZZ es mas vulnerable" como claim central. Ese resultado depende del benchmark, del preprocesado, de la suite y del feature map. El salto Q1 consiste en convertir el trabajo en una teoria y un protocolo de **auditabilidad condicionada al conjunto de informacion** para flujos hibridos clasico-cuanticos, y usar la comparacion de kernels como demostrador controlado.

La tesis fuerte propuesta es:

> A perturbation is not observable or stealthy in the abstract; its auditability is conditional on the information available at each classical-quantum workflow boundary. Consequently, integrity claims require an explicit sensor-information contract and coverage evidence, not only robustness scores.

El caso mas claro ya esta en los datos. Una perturbacion que solo modifica las etiquetas de evaluacion y conserva `X` deja invariantes todas las estadisticas que dependen unicamente de `X` y, para un predictor determinista fijo, tambien las que dependen de `(X, f(X))`. Si ademas conserva la prevalencia, deja invariantes las estadisticas que solo ven el marginal de `y`. Para detectarla hace falta informacion conjunta etiqueta-prediccion o una auditoria de procedencia/verdad de referencia. Esta es una frontera estructural de observabilidad, no una correlacion empirica.

## Estado de ejecucion al 9 de agosto de 2026

Los Gates B y C ya no son trabajo pendiente. La cola exact-statevector completo 360/360 jobs sin fallos: CICIDS 256/256, cuatro pares temporales CICIDS OOD, UNSW-NB15 ID/OOD y ToN-IoT ID. El paquete estricto contiene 13.680 filas brutas y 11.400 observaciones unicas tras eliminar 2.280 repeticiones SVC verificadas.

La replicacion mas fuerte no es el ranking de modelos: las 3.600 observaciones de perturbacion de etiquetas son exactamente ciegas para `X` y `X+prediccion`; las 1.800 prior-preserving tambien lo son para el marginal de `y`; y las 2.184 con impacto positivo tienen evidencia conjunta no nula. Este resultado se reproduce en los ocho entornos de expansion.

El perfil ZZ-SVC es positivo en 7/8 entornos a dimension 8 y 8/8 a dimensiones 10 y 12, pero heterogeneo y correlacionado con el rendimiento limpio. Debe seguir siendo evidencia secundaria, no una afirmacion universal sobre vulnerabilidad cuantica.

Estado honesto del techo: Gates A-C, el nivel simulador de Gate D y el prototipo local de Gate E estan completados; el nivel operacional/QPU de Gate D y el cierre editorial/release de Gate F siguen abiertos. El paper ya combina base multi-dataset/OOD, evidencia quantum-specific y un contrato HSaaS fail-closed ejecutable, pero aun no justifica una afirmacion de seguridad cuantica operacional completa para todo ATHENA-AEGIS.

## Identidad cientifica del paper

### Titulo recomendado

**Information-Set Conditional Integrity Auditing for Hybrid Quantum-Classical Kernel Workflows**

Alternativa mas cercana al manuscrito actual:

**Auditability Gaps in Hybrid Quantum-Classical Kernel Workflows: An Information-Set and Sensor-Coverage Analysis**

### Pregunta principal

Given a structured perturbation at a hybrid workflow boundary, which integrity claims are identifiable from feature-only, prediction-aware, label-marginal, joint-outcome, and quantum-execution evidence?

### Preguntas secundarias

1. Que perturbaciones producen impacto en la conclusion del benchmark y cuales cambian realmente la salida del modelo?
2. Que clases de sensores son estructuralmente ciegas a cada perturbacion?
3. Cual es la cobertura incremental obtenida al ampliar el contrato de observacion?
4. Cambian estos perfiles entre kernels clasicos y feature maps cuanticos?
5. Persisten los resultados al aumentar semillas, tamano muestral, datasets y escenarios OOD?
6. Que controles preventivos y detectivos cierran cada frontera de observabilidad?

## Claims y jerarquia de evidencia

### Claim primario, teorico-metodologico

La auditabilidad es relativa al conjunto de informacion del auditor. Para una transformacion pura de etiquetas `T_y` que mantiene `X` fijo y un predictor determinista fijo `f`, todo estadistico medible con respecto a `X` o `(X, f(X))` es invariante. Si `T_y` preserva el histograma de clases, los estadisticos del marginal empirico de `y` tambien son invariantes. La deteccion requiere informacion conjunta `(y, f(X))`, procedencia de etiquetas o evidencia externa.

### Claim empirico principal actual

En el benchmark ID derivado de CICIDS, las perturbaciones de etiquetas son exactamente ciegas para el bloque feature-plus-prediction y producen impacto positivo en la metrica reportada. Las prior-preserving label flips tambien son ciegas para el bloque label-marginal. El locus causal es la ruta de evaluacion/etiquetas: las predicciones no cambian.

### Claim empirico secundario actual

QSVC-ZZ muestra el mayor impacto medio de la suite ID entre los kernels evaluados. Frente a SVC-RBF, los ratios de impacto son 2.524, 3.094 y 3.323 en dimensiones 8, 10 y 12. Las diferencias medias ZZ-SVC son 0.02427, 0.03289 y 0.03855.

La inferencia primaria debe usar cinco clusters de split, promediando dentro de cada split las cuatro semillas de modelo/perturbacion. Los IC95 clusterizados son:

| Dimension | Diferencia de impacto ZZ-SVC | IC95 clusterizado | Clusters positivos |
|---:|---:|---:|---:|
| 8 | 0.02427 | [0.01200, 0.03654] | 5/5 |
| 10 | 0.03289 | [0.01998, 0.04580] | 5/5 |
| 12 | 0.03855 | [0.02773, 0.04937] | 5/5 |

Las 20 combinaciones split-model-seed se conservan como analisis de sensibilidad, no como 20 unidades externas independientes.

### Claims que no deben hacerse todavia

- que los modelos cuanticos sean universalmente menos robustos o menos auditables;
- que los emuladores binomiales describan ruido calibrado de backend, hardware cuantico o ejecucion QPU;
- que una `stealth score` agregada sea una medida absoluta de ocultacion;
- que modificar etiquetas de evaluacion degrade el modelo: degrada o altera la medicion, no sus predicciones;
- que una sola pareja temporal OOD demuestre generalizacion;
- que este unico paper, en su estado actual, cubra por completo ATHENA-AEGIS G3.1-G3.3.

## Separacion limpia respecto a la tesis

| Trabajo | Objeto cientifico | Pregunta | Unidad de decision | No solapamiento con Paper 1.5 |
|---|---|---|---|---|
| Paper 1 | Certificacion de ventaja predictiva bajo shift | Cuanta ventaja sobre una familia clasica sigue siendo posible con etiquetas objetivo parciales o ausentes | Candidato fijo frente a familia de referencia en un batch objetivo | Identificabilidad de ventaja y adquisicion de etiquetas; no estudia cobertura de sensores frente a perturbaciones del workflow |
| Paper 1.5 | Integridad y auditabilidad del workflow | Que perturbaciones son observables desde cada contrato de informacion y que controles cierran los huecos | Frontera del pipeline y regimen de sensores | No intenta probar ventaja cuantica ni decidir promociones adaptativas |
| Paper 2 | Comparabilidad y promocion adaptativa | Cuando debe un challenger sustituir al incumbent despues de una alarma | Propuesta de actualizacion en un stream | Decision secuencial de despliegue; Paper 1.5 termina en evidencia de integridad, no en politica de promocion |

La secuencia doctoral queda coherente:

1. **identificabilidad de la ventaja**;
2. **integridad de la evidencia y de las fronteras del workflow**;
3. **gobernanza de la decision adaptativa**.

## Correspondencia con ATHENA-AEGIS

La memoria define para Deusto un marco de seguridad, fiabilidad e integridad a lo largo del workflow cuantico-clasico, con herramientas, metodologias y metricas. La cobertura honesta es:

| ATHENA-AEGIS | Evidencia actual | Cobertura actual | Extension necesaria para cierre |
|---|---|---:|---|
| G3.1 / T3.1: vulnerabilidades y contramedidas quantum-specific | 165 celdas con controles de transpilation, mutacion de circuito/parametros, corrupcion de kernel, emuladores de shots y contrato multicapa | Media-alta en simulador; nula en QPU real | Ataques de compilador/scheduler, backend ruidoso calibrado, multi-tenancy y microbenchmark QPU |
| G3.2 / T3.2.4: validacion end-to-end de la integracion hibrida | Suite reproducible desde datos y labels hasta circuito simulado, kernel, prediccion y conclusion | Alta en el artefacto simulado; abierta en operacion | Vincular contratos a scheduling, calibracion, identidad de backend y manifiesto autenticado de proveedor |
| G3.3 / T3.3.1 y “Subtask 3.4.4” (numeracion literal de la memoria): metricas y herramientas end-to-end | Impacto, familias de sensores, tabla de cobertura, manifiestos y analisis reproducible | Alta como prototipo | Sustituir el ranking escalar como evidencia primaria por cobertura calibrada y controles de procedencia |
| Result 3.1 [SOFTWARE] | Runner, ataques, senales, agregacion y manifiestos | Parcial | Empaquetar CLI estable, tests, versionado, ejemplo HSaaS y documentacion de contramedidas |
| Result 3.2 [REPORT] | Manuscrito y notas metodologicas | Parcial | Informe explicito de amenazas, metricas, controles, alcance y trazabilidad a G3.1-G3.3 |
| WP5 case study | NIDS como caso de uso de alto impacto | Parcial | Encapsular clasificador clasico/cuantico como servicio hibrido con contratos de entrada, kernel, salida y auditoria |

Conclusion administrativa: la expansion multi-dataset y Gate D-simulador sostienen el resultado cientifico central de G3.2-G3.3 y una contribucion demostrable a G3.1, pero **todavia no justifican por si solos todo el paquete Deusto**. Para cobertura total faltan el artefacto software empaquetado, el informe formal de trazabilidad y el nivel operacional quantum-specific en scheduling, backend calibrado, multi-tenancy y QPU.

## Correcciones metodologicas ya aplicadas

1. Gate 1 esta completo: 240 CSV y 240 JSON esperados.
2. Se han identificado 7.980 filas brutas y 4.560 observaciones unicas.
3. Se han eliminado analiticamente 3.420 repeticiones exactas de SVC generadas por `qnone`, ZZ, Z y PauliXYZ.
4. La unidad primaria de inferencia cambia de 20 combinaciones a 5 clusters de split.
5. Los seis contrastes primarios de impacto/stealth ZZ-SVC mantienen IC95 positivos bajo el analisis clusterizado.
6. Las perturbaciones label-only se separan causalmente de las perturbaciones que cambian la prediccion.
7. La auditabilidad se reporta por regimen de informacion; el promedio de once senales queda como diagnostico secundario.

Los artefactos nuevos se generan con:

```powershell
.\.venv\Scripts\python.exe -m src.experiments.build_q1_gate1_evidence
```

## Programa experimental para alcanzar el techo

### Gate A - Congelar la contribucion y la taxonomia

Estado: listo para congelar.

- Definir las fronteras: datos, preprocesado, construccion del kernel, ejecucion/estimacion del kernel, postprocesado, etiquetas/evaluacion y reporte.
- Separar impacto sobre salida del modelo de impacto sobre la medicion.
- Congelar los regimenes de observacion y las reglas de cobertura antes de nuevas ejecuciones.
- Declarar el `stealth` min-max como sensibilidad descriptiva, no endpoint primario.

### Gate B - Estabilidad interna y tamano muestral

Estado: completado. Gate 1 y el control 256/256 tienen evidencia cuantica completa.

- Gate 1: 5 splits x 4 model seeds, 128/128, tres dimensiones y tres perfiles cuanticos unicos.
- Gate 2: 30/30 ejecuciones exact-statevector completas a 256/256.
- Resultado: diferencia ZZ-SVC positiva en 5/5 splits para las tres dimensiones; se reporta la magnitud sin exigir conservar un ratio exacto.

### Gate C - Validez externa

Estado: completado para los casos de estudio fijados; la generalizacion poblacional sigue fuera de alcance.

- ID: UNSW-NB15 y ToN-IoT con SVC, ZZ, Z y PauliXYZ.
- OOD: varias parejas CICIDS y una pareja UNSW.
- Unidad externa: dataset/regimen, no semilla.
- Analisis: modelo jerarquico o resumen por dataset con leave-one-dataset-out; nunca presentar miles de filas como replicas externas.
- Criterio: la frontera estructural de sensores debe replicar por construccion; el ranking ZZ puede variar y se reportara como heterogeneidad.

### Gate D - Capa quantum-specific

Estado: nivel simulador completado; nivel operacional/QPU pendiente.

Nivel simulador completado:

1. 165 celdas: cinco splits, dimensiones 4/6/8 y once condiciones;
2. controles de transpilation y reescritura unitaria semanticamente equivalentes;
3. mutaciones RZ dependientes de datos y cambio de repeticiones del feature map;
4. corrupciones asimetricas, de diagonal y PSD-preserving del kernel;
5. emuladores binomiales de 256/1.024 shots y discrepancia entre estimaciones;
6. provenance hashes, comparacion semantica, chequeos algebraicos y monitor de salida;
7. nueve comprobaciones de aceptacion superadas y manifiesto con hashes.

Nivel operacional pendiente:

- ataques o fallos de compilador y scheduler bajo distintas configuraciones fisicas;
- al menos un backend ruidoso calibrado y un microbenchmark QPU;
- manipulacion de metadata de proveedor, interferencia multi-tenant y side channels;
- manifiesto autenticado que vincule circuito, transpilation, calibracion, job y resultado.

Contrato preventivo/detectivo instanciado:

- provenance de circuito, parametros y kernel con adjudicacion de equivalencia;
- semantic probe kernels y politica de transpilation aprobada;
- chequeos algebraicos y reparacion PSD tratada como contencion, no certificacion;
- replicas de estimacion con cotas de incertidumbre;
- politica fail-closed y trazabilidad hasta tabla/figura.

### Gate E - Demostrador HSaaS

Estado: prototipo local completado; despliegue y autenticacion operacional pendientes.

El paquete `src.hsaas` implementa cuatro contratos auditables:

1. `input/preprocessing contract`;
2. `kernel/circuit contract`;
3. `execution/result contract`;
4. `evaluation/report contract`.

Los contratos forman una cadena SHA-256 verificable y aplican `allow`, `hold` o
`block`. Seis escenarios fijados demuestran que el flujo limpio y la
transpilation aprobada pasan; la mutacion de circuito, la sustitucion de kernel
PSD-preserving y la corrupcion de etiquetas prior-preserving se bloquean; y la
estimacion estocastica aprobada queda retenida para adjudicacion. Las ocho
comprobaciones de aceptacion pasan.

Esto convierte los scripts y sensores en un prototipo de `Result 3.1 [SOFTWARE]`.
Para cierre de producto faltan endpoint de servicio,
autenticacion/firma, persistencia, respuesta a incidentes y evidencia de backend.

### Gate F - Paquete de publicacion

Estado: parcialmente completado; release/DOI y adaptacion final a revista pendientes.

- protocolo congelado y machine-readable;
- tests unitarios de ataques, invariancias, seeds y deduplicacion;
- manifiesto final con hashes y conteos esperados;
- figuras reconstruibles desde CSV, sin valores copiados a mano;
- statement de financiacion ATHENA y tabla de trazabilidad en material suplementario;
- version Zenodo exacta y DOI conceptual;
- checklist de reproducibilidad y threat-model card.

## Figuras y tablas del paper Q1

### Figuras principales

1. **Workflow y auditability lattice**: fronteras, informacion observable y sensores.
2. **Attack-to-sensor coverage matrix**: celdas estructuralmente ciegas, empiricamente activas y no aplicables.
3. **Impact locus plot**: impacto de conclusion frente a cambio de prediccion; separa ruta del modelo y ruta de evaluacion.
4. **Clustered model effects**: diferencias por split con IC95, sin pseudorreplicacion.
5. **External validation**: forest plot por dataset/regimen.
6. **Quantum-specific integrity**: impacto frente a deteccion en circuito/kernel/backend.

### Tablas principales

1. Threat model por frontera, capacidad del adversario y activo protegido.
2. Contrato de informacion por sensor: requiere `X`, scores, predicciones, `y`, circuito, transpilation o backend.
3. Resultados primarios clusterizados.
4. Replicacion por dataset y OOD.
5. Contramedida, coste, cobertura y fallo residual.
6. Trazabilidad ATHENA G3.1-G3.3 y artefacto reproducible.

## Riesgos de rechazo y respuesta preventiva

| Riesgo | Respuesta |
|---|---|
| Un unico dataset pequeno | Tres datasets, varias parejas OOD y n=256 |
| Simulacion presentada como evidencia cuantica operacional | Capa quantum-specific y microbenchmark; limitar claims si no hay hardware |
| Preprocesado distinto SVC/QSVC confunde causalidad | Presentar pipelines completos y anadir control de preprocesado simetrico/ablation |
| `stealth` ad hoc y sensible a min-max | Sensor coverage como endpoint; stealth solo sensibilidad |
| Mezcla label corruption con model robustness | Separar locus de impacto y usar terminologia de evaluation integrity |
| Pseudorreplicacion por seeds | Split-cluster inference y unidad externa dataset/regimen |
| Ataques benignos llamados ataques adversarios | Hablar de perturbaciones salvo amenaza y capacidad explicitamente modeladas |
| ATHENA sobreafirmado | Matriz de trazabilidad, capa quantum-specific y limites explicitos |
| Solapamiento con Papers 1 y 2 | Secuencia identificabilidad -> integridad -> gobernanza |

## Regla de decision editorial

El paper puede enviarse como Q1 fuerte cuando se cumplan simultaneamente:

1. contribucion teorica de observabilidad formalizada;
2. inferencia clusterizada y deduplicada;
3. al menos tres datasets o regimenes externos con analisis a su nivel;
4. una capa quantum-specific que no sea solo cambiar `X`;
5. al menos una contramedida evaluada, no solo diagnostico;
6. artefacto end-to-end con contratos y manifiestos;
7. claims limitados a la evidencia y diferenciados de Papers 1 y 2.

Con Gates A-C, el nivel simulador de Gate D y el prototipo de Gate E completos, el trabajo ya tiene una contribucion quantum-specific y una contramedida ejecutable defendibles para competir como paper Q1 de seguridad/fiabilidad de sistemas hibridos sin desplazar a los papers nucleares de la tesis. El cierre de Gate D operacional y de Gate F es el techo necesario para convertir ese paper en justificacion integral del paquete Deusto, no una condicion para ocultar las limitaciones actuales.
