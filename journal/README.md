# Paquete editorial para IEEE TDSC

Fecha de revisión: **2026-08-10**.

Esta carpeta reúne el material de preparación para enviar el Paper 1.5 a
*IEEE Transactions on Dependable and Secure Computing* (TDSC). La decisión
actual es preparar un **regular research article para la convocatoria general**.
No se ha encontrado un special issue abierto cuyo tema justifique cambiar el
claim o ampliar el alcance científico del trabajo.

## Contenido

- `guidelines.txt`: captura sin editar de las instrucciones generales de IEEE
  reunidas por el autor. Se conserva como fuente primaria local, pero no debe
  usarse sola porque mezcla requisitos generales, recomendaciones y elementos
  opcionales.
- `Computer_Society_LaTeX_template.zip`: paquete de plantilla descargado.
- `Computer_Society_LaTeX_template/`: copia descomprimida del paquete.
- `TEMPLATE_AUDIT.md`: auditoría de integridad, antigüedad y aplicabilidad de
  la plantilla.
- `TDSC_SUBMISSION_REQUIREMENTS.md`: requisitos consolidados y checklist vivo
  para el envío.
- `TDSC_EDITORIAL_MEMORY.local.md`: memoria estratégica local con la ruta de
  revistas y el protocolo posterior a un rechazo. Está ignorada de forma
  explícita por Git y no forma parte del artefacto público.

## Jerarquía de autoridad

Si dos instrucciones discrepan, usar este orden:

1. instrucciones que muestre el IEEE Author Portal para TDSC al iniciar el
   envío;
2. página oficial de información para autores de TDSC;
3. políticas vigentes de IEEE Computer Society y del IEEE Author Center;
4. selector oficial de plantillas de IEEE;
5. documentos locales de esta carpeta.

La plantilla local es útil para la conversión, pero no congela las reglas de
2026. Los PDF incluidos declaran `IEEEtran` 1.8b y fechas de 2020–2021.

## Decisión sobre special issues

Las convocatorias abiertas localizadas el 2026-08-10 se centran en seguridad,
alineamiento y responsabilidad de LLM, o en sistemas inteligentes y agénticos.
No encajan con el claim de auditabilidad de integridad condicionada al conjunto
de información. Forzar uno de esos special issues elevaría el riesgo de desk
rejection y diluiría el paper. La ruta correcta es, por tanto, **TDSC regular**.

Antes del envío debe repetirse una comprobación corta de convocatorias: sólo se
cambiará a un special issue si el manuscrito encaja sin añadir LLM, agentes,
QPU real, scheduling, multi-tenancy, provider security ni Fleet Management.

## Estado del paquete TDSC

La conversión está materializada en `publication/tdsc/`: artículo completo,
suplemento, bibliografía, figuras vectoriales, build limpio, trazabilidad y
README de reproducción. `publication/submission/` contiene ya la cover letter,
title page, disclosure y checklist específicos de TDSC. Los PDF de trabajo se
generan en `output/pdf/`.

El paquete científico está cerrado. Sólo siguen abiertos los metadatos que
requieren decisión de los autores: autoría/ORCID/CRediT, licencia, fórmula
oficial completa de financiación, declaración final de conflictos y uso de IA,
visibilidad del repositorio y Zenodo/DOI.

## Fuentes oficiales comprobadas

- TDSC, convocatoria general y scope:
  <https://www.computer.org/digital-library/journals/tq/cfp-dependable-secure-computing>
- TDSC, topics:
  <https://www.computer.org/digital-library/journals/tq/tdsc-topics>
- IEEE Computer Society, author resources:
  <https://www.computer.org/publications/author-resources>
- IEEE Computer Society, calls for papers:
  <https://www.computer.org/publications/author-resources/calls-for-papers>
- IEEE Template Selector:
  <https://template-selector.ieee.org/>
- IEEE Author Center, estructura del artículo:
  <https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/>
- IEEE Author Center, material suplementario:
  <https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/prepare-supplementary-materials/>
- IEEE, política de sharing y preprints:
  <https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE-Article-Sharing-and-Posting-Policies.pdf>
- IEEE, manual editorial vigente:
  <https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE-Editorial-Style-Manual-for-Authors.pdf>
- IEEE Open, APC vigentes:
  <https://open.ieee.org/for-authors/article-processing-charges/>
