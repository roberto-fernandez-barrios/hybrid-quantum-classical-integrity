# Requisitos consolidados de envío — IEEE TDSC

Fecha de contraste con fuentes oficiales: **2026-08-10**; estado del paquete actualizado el **2026-09-07** (artefacto 1.2.0).  
Destino: *IEEE Transactions on Dependable and Secure Computing* (TDSC).  
Tipo previsto: **regular research article, general submission**.

Este documento distingue requisitos confirmados, decisiones internas y puntos
que sólo pueden cerrarse en el IEEE Author Portal. Debe revisarse de nuevo el
día en que se cree el envío.

## 1. Encaje y claim editorial

TDSC publica fundamentos, metodologías y mecanismos para diseñar, modelar y
evaluar sistemas dependables y seguros, incluyendo monitoring, measurement,
experimental methods, software validation and verification y quantum
computing.

El manuscrito debe abrir como un paper de **integrity assurance under partial
observability**, no como un benchmark QML:

> An integrity claim is supportable only relative to the evidence available in
> the auditor's declared information set; uninstrumented boundaries induce
> explicit blind regions, and missing mandatory evidence must trigger
> fail-closed abstention rather than certification.

La carga cuántico-clásica es el sistema heterogéneo sometido a assurance. La
comparación ZZ-vs-SVC es evidencia secundaria. No se añadirán QPU real,
scheduling, multi-tenancy, provider security ni Fleet Management a este paper.

## 2. Special issue o envío regular

Decisión actual: **envío regular**.

Las convocatorias TDSC abiertas localizadas en la fecha de corte son sobre
seguridad/alineamiento de LLM y sobre sistemas inteligentes/agénticos. No
corresponden al claim del Paper 1.5. Una convocatoria de data circulation que
mencionaba auditing cerró el 2026-06-01 y tampoco era un encaje suficientemente
directo.

No se adaptará el paper a una convocatoria mediante una ampliación oportunista.
Antes de enviar se repetirá la consulta en la página de calls for papers; sólo
se elegirá un special issue si acepta el manuscrito actual sin alterar RQs,
evidencia ni limitaciones.

## 3. Formato y plantilla

Confirmado por la documentación de IEEE Computer Society y por el how-to local:

- formato US Letter y dos columnas;
- clase base esperada para Computer Society:

  ```tex
  \documentclass[10pt,journal,compsoc]{IEEEtran}
  ```

- usar la versión que entregue el IEEE Template Selector en la fecha de
  conversión;
- la plantilla sólo aproxima la producción final;
- no insertar número de volumen, número, fecha, DOI, copyright line ni running
  headers definitivos en la primera entrega;
- ecuaciones numeradas consecutivamente y todas las figuras/tablas citadas en
  orden;
- referencias numéricas IEEE, con una entrada por referencia.

### Riesgo de longitud

La política general de IEEE Computer Society fija en **12 páginas maquetadas**
el límite final de un regular paper de Transactions, incluyendo referencias y
biografías. Las páginas o fracciones por encima del límite generan un Mandatory
Overlength Page Charge de **USD 220 por página**, independiente del APC de open
access.

**Verificación 2026-09-07 (artefacto 1.3.1)**, página de autores de IEEE
Computer Society (`computer.org/publications/author-resources/authors`):
"The regular paper page length limit is defined at 12 formatted pages for
Transactions [...], including references and author biographies"; "All page
limits include abstracts, references, and author biographies"; "Any pages or
fraction thereof exceeding this limit are charged $220 per page"; para
revistas, "Author biographies are not required, and there is not a specific
style format". La misma página indica para el abstract de un regular paper
"100 to 200 words", mientras que el IEEE Author Center admite hasta 250; el
abstract de 1.3.1 tiene ≤ 250 palabras (test de CI) y se comprobará en el
portal si exige 200. Estado 1.3.1: 12 páginas sin biografías; si el editor
las exige en aceptación (≈ media página para cuatro autores) habrá que
absorberlas en camera-ready o asumir el MOPC de una página.

El límite exacto de la versión sometida puede diferir del límite de producción;
debe confirmarse en TDSC/Author Portal. Hasta entonces, el objetivo interno es
un cuerpo final de **máximo 12 páginas IEEE**. Material útil pero no esencial
para evaluar el claim debe ir al suplemento.

## 4. Front matter

- Título sin fórmulas ni símbolos innecesarios.
- Nombres y afiliaciones completos; ORCID requerido para todos los autores en
  el sistema de envío.
- Identificar corresponding author.
- Declarar financiación oficial en el primer footnote/author affiliation cuando
  el texto contractual esté confirmado. No inventar códigos ni entidades.
- Abstract de **150–250 palabras**, un único párrafo, autocontenido, sin
  referencias, footnotes, ecuaciones ni abreviaturas sin definir.
- **3–5 Index Terms** normalizados; definir abreviaturas.
- Preparar CRediT, conflictos de interés y data/code availability aunque el
  portal determine dónde se introducen.

## 5. Revisión y anonimización

La política general de IEEE Computer Society es **single-anonymous**: los
revisores conocen a los autores y los autores no conocen a los revisores. Se
solicitan al menos tres revisiones independientes. Una revisión
double-anonymous puede pedirse, pero queda a discreción del editor-in-chief.

Por defecto, por tanto:

- no anonimizar autores, repositorio o autocitas de forma artificial;
- no incluir datos personales innecesarios ni credenciales;
- si se solicita double-anonymous, generar una variante separada y anonimizar
  también supplement, repositorio y metadatos del PDF.

Todos los manuscritos se someten a controles de plagio/solapamiento.

## 6. Originalidad, trabajos relacionados y preprints

- El manuscrito no puede estar simultáneamente bajo revisión en otra revista o
  conferencia.
- Debe citar cualquier versión preliminar o trabajo propio estrechamente
  relacionado.
- Al enviar, adjuntar copias de trabajos previos relacionados y una explicación
  breve de diferencias cuando corresponda.
- IEEE permite preprints en arXiv, TechRxiv y sitios personales/institucionales.
  Tras aceptación, actualizar la copia pública con el DOI o con la versión
  aceptada y el aviso de copyright aplicable.
- La inclusión posterior del artículo en la tesis está permitida por la
  política de sharing de IEEE; la versión exacta y el aviso dependen de la ruta
  de copyright/OA elegida.

## 7. Política de uso de IA

El manual editorial vigente exige revelar en `Acknowledgment` el contenido
generado por IA, identificando el sistema, las secciones afectadas y el nivel de
uso. La edición exclusivamente gramatical queda generalmente fuera del objeto
estricto de la norma, aunque IEEE recomienda transparencia.

Antes del envío se debe acordar y fijar una declaración fiel al uso real. No se
debe confundir esta obligación de autoría con el objeto científico del paper.

## 8. Figuras y tablas

Usar preferentemente:

- PDF/EPS para gráficos vectoriales;
- al menos 300 dpi para color o grayscale;
- al menos 600 dpi para line art;
- anchura aproximada de 3.5 in para una columna o 7.16 in para dos columnas;
- fuentes incrustadas, texto legible al tamaño final y paletas accesibles;
- captions autocontenidas, sin hacer descansar el claim únicamente en color;
- tablas editables en LaTeX, evitando capturas rasterizadas.

Preflight obligatorio:

- cada figura y tabla aparece después de su primera cita razonable;
- numeración y cross-references sin huecos;
- ejes, unidades, n, intervalos e interpretación estadística explícitos;
- no duplicar en prosa todos los valores ya visibles en tablas;
- verificar legibilidad a una columna antes de usar doble columna.

## 9. Suplemento y reproducibilidad

IEEE acepta material suplementario separado. Formatos recomendados incluyen
TXT, DOC/DOCX y PDF para texto; JPG/TIF/PNG/GIF/PDF/PS/EPS/BMP para imágenes, y
formatos comunes de audio/vídeo.

Para este paper, el paquete suplementario debe contener únicamente material que
permita auditar o reproducir el estudio sin ser imprescindible para entender el
argumento principal:

- threat-model card completa;
- matriz de intervenciones/sensores y blind regions;
- especificaciones y resultados secundarios;
- detalle estadístico y sensitivity analyses;
- manifests, hashes y mapping tabla/figura → artefacto;
- instrucciones de ejecución y expected outputs.

El README del suplemento debe incluir descripción, tamaño, plataforma,
entorno/versiones, inventario, setup, comandos de ejecución, salida esperada y
contacto. Los suplementos se suben como archivos separados y se etiquetan como
supplementary material.

TDSC ofrece integración opcional con Code Ocean. El repositorio versionado y el
DOI de Zenodo siguen siendo la fuente archivística principal del artefacto; no
se migrará el workflow sólo para usar Code Ocean.

## 10. Open access, costes y acuerdos

TDSC es híbrida:

- ruta tradicional: sin APC de Gold OA;
- ruta Gold OA para artículos enviados en 2026: **USD 2,800**, antes de
  impuestos y sujeto a la tarifa/fecha efectiva del portal;
- MOPC: **USD 220 por página final** por encima de 12, también en la ruta
  tradicional y no cubierto automáticamente por el APC;
- descuentos de membresía no se aplican a overlength y no siempre son
  acumulables.

Antes de elegir OA, consultar a la biblioteca de Deusto la elegibilidad y cupo
del acuerdo institucional IEEE/CRUE. No registrar como financiación confirmada
una cobertura que todavía dependa de aprobación administrativa.

## 11. Archivos y metadatos previstos para el portal

Preparar, sin presuponer que todos serán obligatorios en la primera pantalla:

1. PDF principal en formato TDSC.
2. Fuentes LaTeX limpias, bibliografía y figuras originales.
3. Cover letter específica de TDSC.
4. Supplement y su README.
5. Title-page metadata: autores, afiliaciones, ORCID y corresponding author.
6. Abstract e Index Terms copiables como texto plano.
7. Funding statement oficial.
8. Conflict-of-interest statement.
9. Data/code availability statement y enlaces/DOI.
10. AI-use disclosure.
11. CRediT author contributions.
12. Copias de trabajos relacionados y difference statement, si aplica.
13. Suggested/opposed reviewers únicamente si el portal lo solicita, con
    conflictos revisados.

IEEE Computer Society indica un máximo de **350 MB por archivo cargado** en su
guía general. La interfaz y designaciones concretas deben comprobarse en el
IEEE Author Portal al crear el draft.

## 12. Adaptación específica del Paper 1.5

Cambios editoriales aplicados en el release candidate TDSC:

- se reemplazó el destino anterior en el paquete de envío activo;
- se creó una fuente LaTeX TDSC a partir de
  `manuscript/archive/paper15_q1_manuscript_spine_v11.md` (hoy archivado; la fuente autoritativa es `publication/tdsc/main.tex`), sin editar sobre el sample;
- se conservó como claim principal la auditabilidad de integridad condicionada
  al information set;
- se presentan `blind regions`, sensor coverage, validación multi-dataset/OOD,
  controles quantum-specific y contrato fail-closed como una contribución
  conjunta;
- no se presentan Propositions 1–2 ni ZZ-vs-SVC como novedad principal;
- se mantiene ATHENA-AEGIS como financiación/trazabilidad externa,
  no como validación científica ni como claim de cobertura completa;
- WP5 se limita a una instanciación local/AEGIS security slice cuando
  proceda, sin afirmar un Fleet Management System operacional;
- el detalle no esencial se movió al suplemento después de conservar en el
  cuerpo threat model, definiciones, métodos, endpoints, resultados
  primarios y limitaciones;
- la longitud real se compiló y midió en `compsoc`: 9 + 3 páginas en el rc1
  anónimo (2026-08-10), 11 + 6 en la release 1.1.x y los valores vigentes de
  1.2.0 están en `publication/RELEASE_STATUS.md` (generado; el artículo se
  mantiene por debajo del techo interno de 12 páginas).

## 13. Frontera con el Paper 2.5

El plan nuevo de ATHENA-AEGIS es coherente con esta separación:

- **Paper 1.5:** qué fallos de integridad son observables bajo una vista y
  unas referencias confiables declaradas; regiones ciegas estructurales y
  calibradas, presupuesto de falsas alarmas a nivel de decisión, contratos,
  hash chain y política fail-closed calibrada, todo local y en simulación.
- **Paper 2.5:** assurance operacional longitudinal y condicionada al contexto
  de ejecución sobre QPU real: no estacionariedad, contexto fuera de soporte y
  abstención, garantías operacionales calibradas en ventanas múltiples,
  recuperación/fallback/rollback, time-to-recovery, evidencia de proveedor sin
  confundir firma local con attestation, deriva de scheduling y la AEGIS slice
  del FMS.

Paper 2.5 debe heredar y citar el coverage contract, la calibración por
familia y la capa de política de Paper 1.5; no debe reclamar de nuevo la
auditabilidad condicional, la calibración de falsas alarmas simple, los
contratos ni la integridad por hash chain como novedad. Paper 1.5 no debe
absorber ningún experimento previsto para 2.5 con el fin de encajar en TDSC.

## 14. Puntos que deben verificarse dentro del portal

No se presentarán como hechos cerrados hasta crear el draft de submission:

- límite de páginas de la **versión de revisión**, si difiere del límite final;
- si el portal exige biografías y fotografías en la primera versión;
- extensiones y designaciones exactas de los source files;
- campos obligatorios de CRediT, data availability y AI disclosure;
- disponibilidad real de double-anonymous review;
- taxonomía/keywords que ofrece TDSC;
- subject/manuscript type exacto para `Regular Paper`;
- APC y acuerdo institucional efectivos para el corresponding author;
- cualquier cambio de plantilla o clase respecto a `IEEEtran` 1.8b.

## 15. Gate de submission-readiness

No enviar hasta que todos estos puntos estén cerrados:

- [x] Título, abstract y contributions pasan una lectura TDSC de desk review.
- [x] LaTeX compila desde cero sin warnings materiales ni referencias rotas.
- [x] PDF en US Letter, dos columnas, `compsoc`, visualmente inspeccionado.
- [x] El artículo se mantiene por debajo del techo interno de 12 páginas en
      todas las builds (rc1: 9; 1.1.x: 11; 1.2.0: ver
      `publication/RELEASE_STATUS.md`).
- [x] Todos los claims tienen tabla/figura o argumento formal trazable.
- [x] Supplement, tests y verificador del repositorio pasan desde el entorno
      bloqueado; el full replay conserva sus instrucciones separadas.
- [ ] Hashes, release, tag, Zenodo/DOI y versiones coinciden (1.2.0: el DOI de
      versión lo inserta `scripts/release_pipeline.py`).
- [x] Afiliaciones, ORCID y corresponding author confirmados (2026-09-06); financiación verificada; CRediT propuesto pendiente de confirmación de todos los autores.
- [ ] AI-use disclosure (ampliada 2026-09-07 para el núcleo formal, el modelo
      de adversario y las gates de política de 1.2.0) re-aprobada por todos los
      autores.
- [x] El paquete de envío activo ya no apunta a la revista objetivo anterior.
- [x] No se afirma QPU real, scheduling, multi-tenancy, provider security,
      confidentiality completa ni Fleet Management operacional.
- [x] Cover letter explica objeto protegido, threat/fault model, information
      set, blind regions y garantía fail-closed en la primera página.

## 16. Fuentes oficiales

La lista de enlaces y la jerarquía de autoridad se mantienen en `README.md`.
Los documentos externos de gran tamaño no se duplican en el repositorio: se
enlazan a su versión oficial para evitar copias obsoletas y problemas de
procedencia.
