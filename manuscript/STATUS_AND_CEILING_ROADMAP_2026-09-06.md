> **SUPERSEDED (2026-09-07).** Estado histórico al 6 de septiembre de 2026. El estado vigente y la hoja de ruta tras el artefacto 1.2.0 están en `STATUS_AND_CEILING_ROADMAP_2026-09-07.md`. Los recuentos citados aquí (17 tests, 4 manifiestos, 22 salidas, 96 ficheros, 9+3 páginas) son los de su fecha y no son vigentes.

# Estado del proyecto y hoja de ruta hacia el techo absoluto

Fecha de auditoría: **2026-09-06**  
Alcance: Paper 1.5 (este repositorio), Paper 2.5 (solo plan en `Proyecto/`), y
relación con los tres papers de la tesis en `../Tesis/`.

## 1. Veredicto en una página

| Pieza | Estado real | Bloqueo | Trabajo restante |
|---|---|---|---|
| Paper 1.5, ciencia | **Cerrada.** 360/360 jobs, 165/165 celdas, 6/6 escenarios, 17/17 tests, verificador OK, PDFs TDSC coinciden con `CHECKSUMS.sha256` | Ninguno científico | Refuerzo opcional (§4.3) |
| Paper 1.5, manuscrito TDSC | rc `1.1.0-tdsc-rc1` (9 pág. + 3 supl.) compilado el 2026-08-10 | Related work con corte 2026-08-10; sin autocitas a los papers de la tesis | §4.2 |
| Paper 1.5, envío | **Bloqueado por metadatos de autores**, no por ciencia | Autores/ORCID/CRediT, licencia, DOI, fórmula de financiación, disclosure de IA | §4.2 |
| Paper 1.5, control de versiones | **Toda la conversión TDSC está sin commit ni push** (`publication/tdsc/`, `journal/`, PDFs, cover letter). Último commit y tag: 2026-08-09 | Riesgo de pérdida | §4.1, hoy |
| Paper 2.5 | **Solo existe el plan** (`Proyecto/PLAN_ATHENA_AEGIS_DEUSTO_ABSOLUTE_CEILING.md`). Cero código, cero threat model operacional, sin credenciales QPU en este entorno | Acceso QPU y decisión de arranque | §5 |
| Justificación ATHENA-AEGIS | Paper 1.5 cubre G3.2/G3.3 y parte de G3.1 en simulador. **3.1.3, 3.2.3, 3.3.3 y WP5 Task 5.1 no están cubiertos** y solo los cubre Paper 2.5 | Depende de Paper 2.5 | §5 |

Conclusión: el Paper 1.5 no necesita más experimentos para enviarse; lo que
falta es administrativo más una actualización bibliográfica y de autocitas.
El "techo absoluto" del proyecto no lo alcanza el Paper 1.5 solo: lo alcanza
la pareja 1.5 + 2.5, y el 2.5 está en punto cero.

## 2. Comprobaciones ejecutadas hoy

- `pytest`: 17 passed.
- `verify_publication_artifact --root publication/artifact`: 96 ficheros, 4
  manifiestos, 22 salidas, 3.600/2.184 y 1.440/1.276 confirmados.
- SHA-256 de `output/pdf/paper15_tdsc_submission.pdf` y del suplemento
  coinciden con `publication/tdsc/CHECKSUMS.sha256`.
- Rama `paper15-q1-expansion` sincronizada con `origin` en commits, pero el
  árbol de trabajo tiene 9 ficheros modificados y 8 rutas sin seguimiento.
- Repositorio GitHub: **PÚBLICO** desde el 2026-09-06 (a primera hora de la
  sesión aún era privado). Rama por defecto `main` en el remoto = commit
  inicial `7b82cba` del 2026-04-23; la ciencia vive en
  `paper15-q1-expansion` (remoto en `b32b03f`, 2026-08-09). `publication/tdsc/`
  no existe en ningún remoto. En el remoto no hay nada sensible: `data/`,
  `results/`, `Proyecto/` y `journal/` no están subidos (260 ficheros).
- Entorno: MiKTeX 26.5 con `pdflatex`, `latexmk`, `bibtex`; PowerShell 7;
  Qiskit 2.3.0 + Aer 0.17.2 + QML 0.9.0. **No** hay `qiskit-ibm-runtime` ni
  credenciales IBM en este entorno.
- Coste de cómputo del motor exact-statevector: 360 jobs en 30 min
  (~5 s por job a 128/128). Cualquier refuerzo en simulador es barato.

## 3. Novedad: re-comprobación bibliográfica 2026-09-06

El protocolo interno exige repetir la búsqueda antes del envío. Han aparecido
dos trabajos que **no** están en `NOVELTY_REVIEW_2026-08-09.md` ni en
`references.bib` y que deben entrar en el related work y en la Tabla 1:

| Trabajo | Qué aporta | Riesgo para el claim | Distinción que debe quedar escrita |
|---|---|---|---|
| Yeniaras, *QML-PipeGuard: Drift-Aware Behavioral Fingerprinting for QML Pipeline Integrity* (arXiv:2605.25066, 24-may-2026) | Contrato de observables informacionalmente completo; distingue drift benigno de sustitución adversarial de canal; validado en IBM Heron r2 (`ibm_fez`); cota de complejidad de shots | Vecino directo del Gate D. Misma autora que QCIVET. Cubre "tolerancia calibrada en QPU real" | No modela la frontera de etiquetas/evaluación, ni provenance/hash, ni cobertura multi-entorno; su unidad es el canal cuántico, no el information set del auditor |
| Bajaj, *Evaluation Blindness: How Silent Measurement Failures Corrupt AI Systems* (arXiv:2608.02786, 3-ago-2026) | Define "evaluation blindness" (medición indistinguible de un estado sano mientras el sistema falla); taxonomía de 6 clases sobre 50 incidentes; failure budget | Vecino conceptual del claim central. Un revisor puede decir "el concepto ya existe" | Es taxonómico/cualitativo y clásico; no formaliza regímenes de información, ni deriva blind regions exactas, ni valida cobertura de sensores, ni compone respuesta fail-closed |

Para el Paper 2.5, además: Deng, *Runtime Calibration as State-Trajectory
Feedback Control in Quantum-Classical Workflows* (arXiv:2605.11860) y
*Qurator* (arXiv:2604.05505, scheduling multi-proveedor). Junto con
QML-PipeGuard, reducen la novedad del componente C2 del plan ("risk-calibrated
semantic gate") si se presenta solo. Ver §5.2.

## 4. Paper 1.5: cómo cerrarlo al techo

### 4.1 Hoy (1-2 h): asegurar el trabajo

1. Commit y push de la conversión TDSC. Antes, decidir qué **no** entra:
   - `Proyecto/ATHENA-Memoria.pdf` es la memoria del proyecto; no debe ir a
     un repositorio que se hará público. Añadir `/Proyecto/` a `.gitignore` o
     mover la carpeta fuera del repo.
   - `journal/TDSC_EDITORIAL_MEMORY.local.md` ya está ignorado en el diff
     pendiente de `.gitignore`.
   - `journal/Computer_Society_LaTeX_template.zip` (540 KB) y la carpeta
     descomprimida son material de terceros; mejor ignorarlos y dejar solo
     `TEMPLATE_AUDIT.md` con sus hashes.
2. Corregir `ATHENA_DEUSTO_TRACEABILITY.md`: dice "15/15 tests"; son 17.
3. **El repo ya es público y `main` remoto es el esqueleto de abril.** Quien
   entre hoy no ve el artefacto que sustenta el paper. Ruta de release:
   ignorar `Proyecto/` → commit TDSC en la rama científica → tests +
   verificador → merge (o fast-forward) a `main` → tag inmutable de submission
   → GitHub Release → Zenodo. Hacerlo antes de citar el repo en la cover
   letter.

### 4.2 Antes del envío (1-2 días, sin nuevos experimentos)

1. **Related work**: añadir QML-PipeGuard y Evaluation Blindness a
   `references.bib`, al texto de §II y a la Tabla 1 de posicionamiento.
   Actualizar la fecha de corte en `NOVELTY_REVIEW`. Repetir la búsqueda el
   día del envío.
2. **Autocitas y disclosure de trabajos relacionados** (IEEE lo exige y hoy el
   manuscrito no cita ninguno). Añadir un párrafo "Relation to companion
   work" en §II o §VI con esta partición:
   - *Sharp Target-Domain Certificates for Quantum-Kernel Advantage under
     Distribution Shift* (Fernández-Barrios, Pastor-López,
     González-Santocildes, García Bringas; enviado a EPJ Quantum Technology
     el 2026-09-06; artefacto Zenodo 10.5281/zenodo.21776862). Estimando:
     identificación *sharp* de la ventaja relativa con etiquetas objetivo
     parciales. Comparte UNSW-NB15/ToN-IoT, ZZ-vs-clásico y prediction-lock
     fail-closed con SHA-256. **No** estudia intervenciones sobre el workflow
     ni cobertura de sensores.
   - *Conditional validity of quantum event classifiers under collider
     systematics and quantum estimation uncertainty* (mismos autores;
     arXiv:2609.02781, 2-sep-2026; Zenodo 10.5281/zenodo.22254835). Es el
     vecino conceptual más cercano: jerarquía de información I0–I3, auditor
     fail-closed, "exact blindness" de sensores MMD a nuisances de peso. La
     diferencia que hay que escribir: allí el objeto es la validez de un
     claim científico bajo sistemáticas benignas y aleatoriedad de
     estimación; aquí es la integridad de la cadena de evidencia frente a
     intervenciones en fronteras del workflow, con provenance y respuesta
     ejecutable. Sin esta frase explícita, un revisor que vea ambos verá
     autoplagio conceptual.
   - *Candidate Comparability Before Promotion: Conditional Validation in
     Adaptive Network Intrusion Detection* (Fernández-Barrios, Pastor-López,
     Pikatza-Huerga, García Bringas; rechazado en KBS, listo para IJIS, no
     enviado; Zenodo 10.5281/zenodo.22239106). Comparte CICIDS/UNSW/ToN, los
     mismos monitores (MMD, KS, JSD, QK-MMD con ZZ) y label flips como probe
     corruption. Diferencia: unidad = decisión secuencial de promoción;
     aquí = frontera del workflow y régimen de información.
   - Reflejar la misma partición en la cover letter y en el campo de
     "related manuscripts" del portal.
3. **Disclosure de IA**: hoy dice solo "OpenAI Codex". Desde septiembre se ha
   usado también Claude Code. Actualizar `AI_USE_DISCLOSURE.md`, el
   Acknowledgment de `main.tex` y la title page.
4. **Metadatos de autoría**: los repos hermanos usan el mismo bloque de
   autores de Deusto y el ORCID 0009-0003-5312-2634 para el autor de
   correspondencia. No copiarlo por inferencia: confirmarlo por escrito y
   sustituir `Anonymous Author(s)` en `main.tex` y `supplement.tex`.
5. Licencia, visibilidad del repo, Zenodo/DOI, fórmula de financiación
   verbatim, CRediT, conflictos: checklist ya existente en
   `publication/submission/submission_checklist.md`.
6. Rebuild con `publication/tdsc/build.ps1`, regenerar `CHECKSUMS.sha256`,
   inspección visual de todas las páginas, nueva tag de submission
   (no mover `paper15-q1-v1.0.0`).

### 4.3 Refuerzo opcional antes del envío (≈1 semana; cómputo < 2 h)

Los dos audits hostiles dejan dos riesgos residuales "que no se resuelven con
más experimentos". No es exacto: ambos se pueden acotar con experimentos
baratos dentro del alcance congelado, sin tocar el claim ni robar terreno al
Paper 2.5. Recomendación: hacer (a) y (b) y llevarlos al suplemento como
análisis de sensibilidad; (c) y (d) solo si sobra tiempo.

| ID | Experimento | Objeción que neutraliza | Coste | Frontera con 2.5 |
|---|---|---|---|---|
| (a) | **Gate de calibración nula**. Diseño corregido tras revisar el runner: `IdentityAttack` produce sensores exactamente 0 (los deltas restan el baseline limpio), así que **no** genera distribución nula. Hace falta un sham nuevo `clean_resample` que extraiga un subconjunto limpio independiente del pool de evaluación (mismo tamaño) por semilla: ~medio día de código en `run_benchmark.py`. Protocolo: (1) `clean_resample` con semillas de calibración → nulo y umbral por sensor a α=0.05; (2) `tiny_gaussian` y `tiny_scaling` → especificidad frente a variación benigna; (3) aplicar los umbrales congelados a `paper_core` con semillas distintas → FPR empírico, potencia por intervención y cobertura por régimen. Nunca ajustar umbrales con datos de ataque | "Respuesta no nula no es poder de detección" | < 1 h de cómputo; 2-3 días de código e integración (manifiesto, tabla, figura, verificador, artefacto 1.1.0) | Sensibilidad en diseño fijo y simulador. No es calibración condicionada al contexto ni conformal: eso sigue siendo 2.5 |
| (b) | **Ablación de preprocesado simétrico**: el runner admite `none|standard|minmax01|minmax2pi` en cada rama. Dos controles emparejados sobre el gate CICIDS ID 128/128: A = `standard`/`standard`, B = `minmax2pi`/`minmax2pi`, más la configuración original como referencia. Argumento adicional: el paper VBC de la tesis demuestra que la propiedad del preprocesado cambia conclusiones; dejar el confound abierto aquí sería incoherente | "ZZ > SVC está confundido por el preprocesado" (riesgo residual reconocido en ambos audits) | < 30 min de cómputo | Ninguna |
| (c) | Sensibilidad a baseline ajustado: SVC hoy usa `C=1.0`, `gamma="scale"`. CV de C/γ solo con datos de entrenamiento en CICIDS ID y un OOD representativo. Si el perfil ZZ-SVC se contrae, se publica: "el resultado primario no cambia aunque el efecto secundario se reduzca con un baseline clásico más fuerte" | "El baseline clásico está sin ajustar" | < 30 min | Ninguna |
| (d) | Suite `paper_support` (ruido gaussiano, cuantización, clipping; 9 condiciones) para completar la matriz de cobertura | Completitud de la matriz ataque-sensor | < 30 min | Ninguna |

Regla: si el resultado de (b) o (c) reduce el perfil ZZ-SVC, se publica igual.
El claim primario no depende de ese perfil. Recomendación final tras la
segunda opinión (ChatGPT, 2026-09-06): hacer (a), (b) y (c) antes del envío;
(d) solo si no retrasa.

Matiz sobre autocitas: IEEE no obliga a citar todo trabajo propio; obliga a
declarar trabajo propio estrechamente relacionado y a evitar publicación
redundante. Aquí los tres papers hermanos comparten datasets, monitores o
formalismo, así que citarlos y explicitar la diferencia es la forma correcta
de cumplirlo, no una opción.

Si se decide **no** hacer el refuerzo, dejar (a) y (b) preparados como
respuesta a la primera ronda de revisión.

## 5. Paper 2.5: el verdadero hueco para "justificar todo el proyecto"

### 5.1 Estado

No hay nada más que el plan. Ni `src/assurance`, ni `src/fleet`, ni threat
model operacional, ni esquema de contexto, ni piloto de calibración, ni acceso
QPU configurado aquí. Los repos hermanos (`qevc`, `target_domain_certificates`)
sí ejecutaron jobs en IBM Quantum plan Open (`ibm_marrakesh`, Heron r2), así
que existe una cuenta con ~10 min/mes de QPU.

### 5.2 Ajuste de novedad antes de escribir una línea de código

QCIVET (hash chain + contrato semántico + IBM) y ahora QML-PipeGuard
(tolerancia calibrada que absorbe drift benigno + detección de sustitución de
canal + IBM Heron) ocupan la casilla "gate semántico calibrado en QPU real".
El Paper 2.5 solo tiene techo Q1 si su novedad se apoya en lo que ninguno hace:

1. decisión condicionada al **contexto de ejecución** con abstención por
   contexto fuera de soporte (`hold/recalibrate`), no solo tolerancia;
2. **presupuesto de falsas alarmas** con garantía finite-sample (conformal
   estratificado) y verificación empírica longitudinal (≥5 ventanas de
   calibración);
3. **enforcement evaluado**: `rerun/fallback/rollback` con coste, frente a
   baselines serve-always, provenance-only, umbral global, política local
   del Paper 1.5 y contrato tipo QCIVET/PipeGuard;
4. **dos workloads** (kernel como regresión + routing/QAOA) y la
   instanciación **AEGIS del Fleet Management System** (WP5).

La Tabla de related work del plan debe añadir una fila para QML-PipeGuard y
otra para el trabajo de runtime calibration de Deng.

### 5.3 Ruta crítica realista

| Fase | Contenido | Depende de hardware | Duración estimada |
|---|---|---|---|
| A | Revisión bibliográfica profunda y congelación de RQs/claims (Gate A del plan) | No | 1 semana |
| B | Threat model operacional + `ExecutionContext` schema + evidence envelope firmado (Gates B-C) | No | 2-3 semanas |
| C | FMS slice local + workload QAOA con oráculo clásico + kernel workload heredado (Gate H parcial) | No | 3-4 semanas |
| D | Piloto de calibración y método (conformal estratificado, regla OOS) en simulador ideal y ruidoso calibrado con snapshots reales (Tier 1-2, Gate D) | Solo snapshots de calibración (gratis) | 2-3 semanas |
| E | Campaña QPU longitudinal: jobs pequeños semanales, ≥5 ventanas, ≥2 backends si la cuenta lo permite (Gate F) | **Sí**: 10 min/mes del plan Open es justo; pedir acceso institucional o presupuesto | 6-8 semanas de calendario |
| F | Suite de fallos, ablación de enforcement, estadística, figuras, trazabilidad, manuscrito, release/DOI | No | 4-6 semanas |

Total realista: 4-6 meses, con la campaña QPU como cuello de botella de
calendario, no de cómputo. La decisión que solo puede tomar el autor: pedir ya
acceso QPU ampliado (IBM Quantum Network vía Deusto/ATHENA, o pago por uso en
IBM/Braket). Sin QPU real se activa el kill criterion KC1 del plan: el
trabajo sería bueno pero no cerraría 3.1.3/3.2.3/3.3.3.

## 6. Coherencia de la tesis y citas cruzadas

Narrativa: claim (certificates) → evidence (1.5) → decision (VBC) →
execution (2.5), con el paper de colisionador como transferencia de la idea
"information-conditional" a física. Estado de las citas cruzadas hoy:

| Repo | Cita a | Falta |
|---|---|---|
| target_domain_certificates | qevc (arXiv:2609.02781) | 1.5 y VBC |
| qevc | target_domain_certificates (Zenodo) | 1.5 y VBC |
| validate-before-commit | nadie (stub `fernandez_paper1` vacío) | rellenar con target_domain_certificates; añadir 1.5 |
| Paper 1.5 | nadie | los tres (§4.2) |

Cuando el Paper 1.5 tenga preprint o DOI, propagar la cita a los otros tres.

## 7. Decisiones que requieren al autor

1. ¿Refuerzo (a)+(b) antes del envío a TDSC, o envío inmediato tras §4.1-4.2?
2. Lista de autores, orden y CRediT del Paper 1.5.
3. Licencia del artefacto y momento de hacer público el repo.
4. Acceso QPU para el Paper 2.5 y fecha de arranque.
5. Dónde vive `Proyecto/` (memoria confidencial) respecto al repo público.

## 8. Ejecución del 2026-09-06 (tarde): decisiones y estado

Decisiones del autor (con segunda opinión externa): ejecutar los tres
refuerzos antes del envío; commit de checkpoint sin tag definitivo; autoría =
equipo del paper *Candidate Comparability Before Promotion* (Fernández-Barrios,
Pastor-López, Pikatza-Huerga, García Bringas); tag/release/Zenodo solo tras
cerrar refuerzos y aprobación de todos los autores.

Hecho:

1. Checkpoint `9ad8b5d` en `paper15-q1-expansion`, subido; `origin/main`
   alineado con la ciencia; `Proyecto/` y plantillas de terceros ignorados.
2. Protocolo preregistrado en `paper15_v11_reinforcement_prereg.md` (rejillas,
   α=0.05, particiones, regla del OOD → E8 UNSW temporal) con una enmienda A1
   documentada (sensores item-alineados indefinidos en lotes nulos no alineados;
   dos modos de auditor).
3. Código: `CleanResample` (pool limpio disjunto), suite `paper_null`,
   `--svc-tune/--qsvc-tune` con CV 5-fold en entrenamiento, fingerprint
   retrocompatible (361/361 JSON congelados intactos; un job congelado se
   regenera bit a bit con un hilo BLAS), cola `run_v11_reinforcement_queue`
   (390 jobs), constructor fail-closed `build_q1_reinforcement_evidence`,
   figura `make_q1_reinforcement_figures`, ensamblador
   `assemble_publication_artifact`, verificador a cinco manifiestos, 9 tests
   nuevos (26 en total).
4. Manuscrito rc2: bloque de autores y financiación, PipeGuard y Evaluation
   Blindness en §II y Tabla 1, §II-C *Relation to Companion Work*, disclosure de
   IA (Codex + Claude Code), sección del suplemento con el diseño de los gates;
   cover letter, title page, checklist, notas de release, trazabilidad de
   claims, README, guía de reproducción y plantillas Zenodo/CITATION con autores.
5. Hallazgo metodológico durante la prueba en seco: las features proyectadas
   están dominadas por cúmulos estrechos (70–87 % de las filas dentro de 0.01
   SD en alguna feature), por lo que el KS detecta cualquier perturbación in
   situ ≥1e-3 aunque no reaccione a lotes limpios nuevos. Queda medido en
   `null_mass_point_profile.csv` y debe explicarse en el suplemento.

Cierre (misma tarde): cola 390/390 sin fallos en 42 min; constructor con
14/14 checks de aceptación y 22 tablas; figura `fig_q1_calibrated_coverage`;
7 tablas LaTeX generadas desde CSV (`publication/tdsc/tables/`); `main.tex` con
§5.5 *Calibrated Coverage and Sensitivity Gates*, Fig. 4, abstract (214
palabras), limitaciones y conclusión actualizadas; suplemento con §8 y tablas
5–11; build limpio de 10 + 6 páginas; checksums regenerados; artefacto 1.1.0
ensamblado (134 ficheros, 5 manifiestos, 44 salidas, 40 MB) y verificado; 26
tests en verde. Resumen numérico en
`manuscript/paper15_v11_reinforcement_result_summary.md`.

Resultados en una línea cada uno:

- FPR por sensor 0.029–0.069 (nominal 0.05) sobre 12.000 lotes limpios
  disjuntos; uniones de régimen 0.125 / 0.203 / 0.048 / 0.259.
- Regiones ciegas exactas intactas bajo calibración: 0 disparos de I_X, I_XF
  e I_Ym en 3.600 filas de etiquetas; auditor item-alineado 2.184/2.184;
  auditor batch-level I_XFY solo 1.8 %.
- KS detecta mean shift y scaling drift al 100 % y también los shams de 0.001
  (71–88 %) por los cúmulos de las features proyectadas; dropout casi
  invisible a nivel de lote (0–6 %) pero cambia predicciones en 49–76 %.
- Perfil ZZ−SVC: dirección estable (5/5 clusters en todo), magnitud
  condicional: estandarizar la rama cuántica lo reduce a ~1/3; tuning lo
  amplía en CICIDS ID (ZZ gana margen limpio) y no lo cambia en UNSW OOD.

**Release (misma noche, tras la aprobación de todos los autores).** Se aplicaron
las tres correcciones de la segunda opinión (abstract: "nominal 5% per-sensor
false-alarm target"; disclosure de IA con sistemas, secciones y nivel de uso;
title page sin contradicciones), se añadió el licenciamiento mixto (Apache-2.0
código, CC BY 4.0 evidencia/documentación, manuscrito excluido), se reservó el
DOI en Zenodo antes de publicar y se insertó en todo el paquete, se recompiló
(11 + 6 páginas), se reensambló y verificó el artefacto, y se cerró con el
commit de release `10a2a52`, el tag `paper15-q1-v1.1.0`, la GitHub Release y
la publicación en Zenodo: DOI de versión `10.5281/zenodo.22550853`, DOI de
concepto `10.5281/zenodo.22550852`.

**Versión editorial 1.1.1 (misma noche).** La guía de publicidad de la AEI
(v09, 5-feb-2026) prescribe para «Generación de Conocimiento» 2021–2025 la
fórmula `MICIU/AEI/10.13039/501100011033 y por FEDER, UE` (acrónimos en
español; en inglés `funded by MICIU/AEI/10.13039/501100011033 and by
ERDF/EU`). La frase de financiación pasó a: *This work is part of grant
PID2024-155693NB-C43, ATHENA-AEGIS (…), funded by MICIU/AEI/10.13039/501100011033
and by ERDF/EU*, conservando el acrónimo y el código que pidió el IP. Sin
ningún cambio científico (manifiestos de evidencia byte-idénticos). Release
`d765a67`, tag `paper15-q1-v1.1.1`, GitHub Release y nueva versión Zenodo
`10.5281/zenodo.22552643` bajo el mismo DOI de concepto. La 1.1.0 queda
intacta. Queda únicamente la acción humana de subir el paquete al portal de
TDSC (y el recheck de convocatorias ese día).
