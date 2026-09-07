# Estado del proyecto tras el artefacto 1.3.0 — cierre científico definitivo del Paper 1.5

Fecha: **2026-09-07** (tarde)  
Sustituye a `STATUS_AND_CEILING_ROADMAP_2026-09-07.md` (estado tras 1.2.0,
histórico). Los recuentos autoritativos están en
`publication/RELEASE_STATUS.md` (generado).

## 1. Regla de reapertura

Tras la versión 1.3.0 el Paper 1.5 solo se reabre si existe un error objetivo
que invalide una claim, una exigencia editorial de TDSC o una petición de los
revisores. Toda nueva idea científica va al Paper 2.5 u otro trabajo. No hay
más iteraciones abiertas de "buscar mejoras".

## 2. Qué cerró la 1.3.0

| Bloque | Resultado |
|---|---|
| Prop. 5(b) | La regla de familia de 1.2.0 era asimétrica y su cota (α + 1/(n+1)) es falsa (contraejemplo de cinco vectores: 0,60 frente a 0,40). Sustituida por el p-valor conformal max-rank completo, nivel exacto ⌊α(n+1)⌋/(n+1) = 10/201 bajo intercambiabilidad, empates incluidos; tests exhaustivos permanentes sobre todos los órdenes débiles pequeños y el contraejemplo. |
| Enmienda A2 | Documentada antes de regenerar: qué se descubrió, qué queda invalidado, qué sigue siendo descriptivamente válido, el diagnóstico previo (0,056/0,058/0,048/0,053) revelado, expectativas fijadas; A3 aclara cómo se evalúa el check F4. |
| Gate F | Conformal 0,056 / 0,058 / 0,048 / 0,053 frente a 0,061 / 0,073 / 0,048 / 0,079 (1.2.0) y 0,125 / 0,203 / 0,048 / 0,259 (unión). Descomposición: sesgo de regla +0,005 / +0,015 / 0 / +0,025; efecto de diseño +0,006 / +0,008 / −0,003 / +0,003. Re-particiones intercambiables: 1.2.0 supera α en tres regímenes; conformal 0,036–0,044. E1 en el agregado primario y por separado (0,12); sin E1, 0,045–0,052. |
| Gate D | P2 conformal sirve 4.496 / 4.365 / 7.008 / 4.390 / 0 de 7.008; el régimen confiable no sirve nada pero interrumpe el 52 % de la variación benigna (544 hold + 85 block de 1.200). Taxonomía: P0 baseline, P1 union risk-tolerant, P2 calibrada risk-tolerant, P3 estricta fail-closed; los contratos fallan cerrados en sus invariantes; "offline end-to-end" en todo el paquete. |
| Gate A (F5) | Ejecutado y preregistrado: 240/240 jobs, réplica exacta de los controles. El atacante que preserva los cúmulos baja la detección conformal de 0,96–1,00 a 0,01–0,34 (I_X) y 0,06–0,66 (I_XF) a intensidades iguales, conservando el 83–91 % de la materialidad; P2 sirve 1.328 / 959 / 1.006 de 3.418 filas materiales; el régimen confiable las bloquea todas. L3 no ejecutado (motivo registrado). |
| Cuántico | Proposición 7: la rama cuántica como instancia del retículo (provenance refina semántica; álgebra y salidas coarsen K; ruido de shots convierte el anclaje exacto en test calibrado). ZZ-vs-SVC al suplemento. |
| Núcleo formal | Revisión enunciado a enunciado con búsqueda de contraejemplos y tests por fuerza bruta (`FORMAL_REVIEW_1.3.0.md`, `tests/test_formal_core.py`). |
| Manuscrito | Abstract, introducción, related work (conformal/Tippett/Westfall–Young), pesos de datasets explícitos, tabla de adversario con F5, figura de política a tres paneles con coste benigno, figura F5, coste de provenance visible. |

## 3. Frontera 1.5 / 2.5 tras 1.3.0

Pertenecen al 1.5 y **no** pueden venderse como novedad del 2.5: formalización
de regiones ciegas, calibración de falsas alarmas por familia (conformal),
contratos, hash chain, lógica fail-closed simple, evaluación offline de
política, atacante adaptativo que preserva el fingerprint.

El 2.5 se centra en: contexto de ejecución → validez de la calibración en el
tiempo → detección OOS → abstención → ejecución QPU real → rerun/fallback/
recovery → consecuencia a nivel de servicio (ver
`Proyecto/PLAN_ATHENA_AEGIS_DEUSTO_ABSOLUTE_CEILING.md` §23).

## 4. Confidencialidad (Subtask 3.1.4)

La memoria asigna a Deusto "Ensuring data integrity and confidentiality
(24 months)". El 1.5 cierra la integridad de datos en su alcance; no es un
paper de confidencialidad y no se le añade un experimento artificial. La
estrategia queda documentada en `ATHENA_DEUSTO_TRACEABILITY.md` §
"Confidencialidad" y en el plan del 2.5 §23.4: matriz de exposición de
metadatos por principal, controles de minimización con coste medido, y
referencia al canal temporal de Quantum Leak; lo que no sea medible con la
infraestructura disponible se documenta como entregable técnico del proyecto
(Result 3.2), no como ciencia del 2.5.

## 5. Decisiones que requieren al autor

1. Token Zenodo nuevo en `ZENODO_TOKEN` para `reserve-doi → insert-doi →
   finalize` (nunca escrito en el repositorio).
2. Subida del paquete al portal de TDSC (recheck de convocatorias ese día).
3. Acceso QPU para el Paper 2.5 y fecha de arranque.
