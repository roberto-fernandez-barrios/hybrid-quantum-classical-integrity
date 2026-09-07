# Estado del proyecto y hoja de ruta hacia el techo — actualización tras el artefacto 1.2.0

Fecha: **2026-09-07**  
Sustituye a `STATUS_AND_CEILING_ROADMAP_2026-09-06.md` (histórico).  
Alcance: Paper 1.5 (este repositorio), Paper 2.5 (plan en `Proyecto/`) y la
frontera entre ambos. Los recuentos autoritativos están en
`publication/RELEASE_STATUS.md` (generado).

## 1. Veredicto en una página

| Pieza | Estado real | Bloqueo | Trabajo restante |
|---|---|---|---|
| Paper 1.5, ciencia | **Cerrada al techo de su alcance.** Núcleo formal reconstruido (Lema 1, Prop. 1–6, Cor. 1–2, C1–C8), modelo de adversario explícito, calibración a nivel de decisión (Gate F), evaluación end-to-end de política (Gate D), estadística corregida (unidad clúster, intervalos descriptivos), hallazgo de auditoría publicado (433/59 mejoras aparentes) | Ninguno científico | Ninguno dentro del alcance |
| Paper 1.5, manuscrito TDSC | Retitulado y reorganizado; 11 páginas de artículo + 10 de suplemento; build limpio; todas las cifras de las gates nuevas por macros generadas | Re-aprobación de los autores del texto 1.2.0 y de la disclosure de IA ampliada | Envío al portal |
| Paper 1.5, release 1.2.0 | Commit, tests, verificador, artefacto y hostile review cerrados (ver §3) | **DOI de versión**: requiere un token Zenodo nuevo (no se reutiliza ninguno anterior; no hay webhook GitHub–Zenodo) | `scripts/release_pipeline.py reserve-doi → insert-doi → finalize` |
| Paper 2.5 | Solo plan, ajustado en `Proyecto/PLAN_ATHENA_AEGIS_DEUSTO_ABSOLUTE_CEILING.md` (§ "Ajuste tras 1.2.0") | Acceso QPU y decisión de arranque | §4 |
| Justificación ATHENA-AEGIS | 1.5 cubre G3.2/G3.3 como contribución metodológica en diseño fijo (incl. presupuesto de falsas alarmas a nivel de decisión y coste de enforcement medido) y parte de G3.1 en simulador. 3.1.3, 3.2.3, 3.3.3 y WP5 Task 5.1 siguen en el 2.5 | Depende del 2.5 | §4 |

## 2. Qué cambió en 1.2.0 (sin re-ejecutar ningún kernel ni sorteo)

1. **Formalización.** Auditabilidad = propiedad de (clase de intervención,
   vista, referencias confiables). Regiones ciegas estructurales vs de sensor;
   monotonía por refinamiento; cierre exacto por evidencia inyectiva sobre la
   órbita; materialidad ⇒ separabilidad en la vista conjunta; tres clases de
   auditor; unión vs familia; sin raíz no controlada no hay garantía local.
   Las Proposiciones 1–2 anteriores son corolarios.
2. **Hallazgo de auditoría (enmienda A1).** `impact_bal_acc` era la parte
   positiva del cambio; 433 filas de etiquetas de la expansión (59 en Gate 1)
   *suben* la BA. La frase "no negative impact occurs" de 1.1.1 se retira; se
   publican los recuentos con signo (2.184/983/433; 1.276/105/59) y el
   verificador los recomputa.
3. **Gate F.** Calibración por familia de cada régimen: FPR de decisión
   0,061/0,073/0,048/0,079 frente a 0,125/0,203/0,048/0,259 de la unión.
   Expectativa preregistrada ("≈0,05 en todos") cumplida solo
   aproximadamente; el exceso residual (E1, ToN-IoT) se publica como medida
   de la violación de intercambiabilidad.
4. **Gate D.** Cuatro políticas × cinco regímenes sobre 24.000 observaciones
   congeladas: los regímenes batch con evidencia de features sirven
   4.322–4.494 de 7.008 resultados materialmente cambiados (el marginal de
   etiquetas los sirve todos); la referencia item-alineada confiable sirve 0
   con 0 false holds; la política estricta no sirve nada donde la frontera de
   etiquetas no está verificada. Composición con los seis contratos: 6/6.
5. **Modelo de adversario** por clase (fault robustness / integrity
   corruption / adversarial / adaptive) con raíces no controlables.
6. **Related work** ampliado a stealth/detectability en CPS, runtime
   assurance, integrity monitoring y evaluation integrity; delimitación
   positiva en lugar de "no previous study".
7. **Documentación y reproducción**: fuente única de recuentos, rutas
   portables, hashes de datasets, borradores históricos archivados.

## 3. Comprobaciones de cierre (2026-09-07)

- Tests: suite completa en verde (recuento en `RELEASE_STATUS.md`).
- Verificador sobre `publication/artifact`: seis manifiestos, 65 salidas,
  recuentos con signo y claims de política recomputados.
- Build TDSC limpio (sin referencias rotas ni cajas desbordadas > 1 pt);
  inspección visual de todas las páginas.
- Hostile review final: `publication/TDSC_HOSTILE_REVIEW_AUDIT.md`
  (sección 1.2.0).

## 4. Paper 2.5: núcleo tras el ajuste

El 2.5 no puede vender como novedad la calibración simple de falsas alarmas,
los contratos ni la integridad por hash chain (ya en 1.5). Su núcleo queda en:

1. assurance longitudinal condicionada al contexto de ejecución (backend,
   calibración, layout, transpilación, shots, tiempo) bajo no estacionariedad;
2. detección de contexto fuera de soporte y abstención (`hold/recalibrate`);
3. garantías operacionales calibradas con verificación empírica en ≥5
   ventanas de calibración (la Proposición 5 de 1.5 dice exactamente cuándo
   deja de valer la garantía: cuando falla la intercambiabilidad; el 2.5 mide
   eso en hardware);
4. QPU real (≥2 backends si la cuenta lo permite) y tier de ruido calibrado;
5. recuperación/fallback/rollback evaluados, continuación insegura y
   time-to-recovery como endpoints;
6. evidencia de proveedor/contexto capturada por el cliente y ligada a un
   sobre firmado localmente, sin llamarlo attestation del proveedor;
7. deriva de scheduling/contexto como variable científica;
8. AEGIS slice del demostrador FMS, no "todo el FMS" salvo coordinación formal.

Ruta crítica y kill criteria: sin cambios respecto al plan (acceso QPU es el
cuello de botella de calendario; sin QPU real no se cierran 3.1.3/3.2.3/3.3.3).

## 5. Decisiones que requieren al autor

1. Re-aprobar el manuscrito 1.2.0 (título nuevo, §III–IV, §VI-B/C) y la
   disclosure de IA ampliada.
2. Generar un token Zenodo nuevo y ejecutar la pipeline de release (reserva de
   DOI, inserción, rebuild, tag, GitHub Release, publicación, commit
   documental).
3. Subir el paquete al portal de TDSC (recheck de convocatorias ese día).
4. Acceso QPU para el Paper 2.5 y fecha de arranque.
