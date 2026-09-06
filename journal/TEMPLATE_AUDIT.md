# Auditoría de la plantilla IEEE Computer Society

Fecha de auditoría: **2026-08-10**.

## Veredicto

El ZIP está íntegro y la carpeta descomprimida es una copia exacta de su
contenido. Los dos PDF se renderizaron e inspeccionaron visualmente; no se
observaron páginas rotas, fuentes ausentes ni figuras omitidas.

El sample también se compiló desde cero, en dos pasadas, con MiKTeX 26.5 y la
clase instalada `IEEEtran` 1.8b. Produjo correctamente un PDF de seis páginas.
El único warning material fue `Unused global option(s): [lettersize]`; la clase
usó de todos modos papel Letter. No se copiará esa opción al manuscrito nuevo:
se usará la declaración `compsoc` que entregue el selector y se comprobará el
tamaño físico del PDF resultante.

La plantilla, sin embargo, es **genérica y antigua**. Sus documentos declaran
`IEEEtran` 1.8b y fechas de 2020–2021. Sirve como base técnica, no como evidencia
de que los requisitos de TDSC de 2026 estén congelados.

## Integridad del paquete

Contenido del ZIP y hashes SHA-256 de la copia descomprimida:

| Archivo | SHA-256 | Coincide con el ZIP |
|---|---|---:|
| `bare_jrnl_new_sample4.tex` | `a1225c6ddb0c828596fad8285d4344a654e1597d62e757d0109b07e4f579e4fc` | Sí |
| `bare_jrnl_new_sample4.pdf` | `30c9326f0f9e3a65f62d87c748add8c8c7600cc0cc13e44d4f05098c669f64c5` | Sí |
| `New_IEEEtran_how-to.tex` | `417b40378ec1c1124918f000eab2f9a27f9cc37d576ef17b77d78347e00c0cd3` | Sí |
| `New_IEEEtran_how-to.pdf` | `3ad40a6f9f6b8ac10baa9dcd3cda9d6e83dae8577d950c09fa73a5d97146ff43` | Sí |
| `fig1.png` | `966fa8e10adb05f5bc7bc32e6debc68be14e2c4cb5c7a6784cac4324472d6c8e` | Sí |

Hash del archivo original:

- `Computer_Society_LaTeX_template.zip`:
  `f1abd5e9ed440e4263d9e9c2d941eeb4d4cfcfdfece43ccfa10e87613c7bdde9`.

## Hallazgos de aplicabilidad

1. Los dos `.tex` empiezan con
   `\documentclass[lettersize,journal]{IEEEtran}`. Es el modo genérico de
   journal, no el modo específico de Computer Society.
2. El how-to incluido prescribe para un artículo de revista de IEEE Computer
   Society:

   ```tex
   \documentclass[10pt,journal,compsoc]{IEEEtran}
   ```

   Ésta debe ser la configuración inicial para TDSC, salvo que el selector
   oficial vigente entregue una variante distinta.
3. La plantilla indica expresamente que sólo aproxima el aspecto y la longitud
   final. El PDF publicado se recompone durante producción.
4. `\markboth` y la línea de copyright no son necesarios para la primera
   entrega de un artículo de Transactions.
5. El paquete no contiene `IEEEtran.cls`, un `.bst` ni una plantilla nominal de
   TDSC. La compilación depende de una distribución LaTeX actual y de la clase
   instalada.
6. Las biografías del ejemplo ilustran el formato final; su exigencia en la
   primera versión debe confirmarse en el portal. Sí cuentan para el límite de
   longitud final cuando se incorporan.

## Regla para la conversión del manuscrito

Antes de convertir el Markdown final:

1. descargar de nuevo la plantilla mediante el IEEE Template Selector;
2. comparar versión y opciones de `IEEEtran` con este paquete;
3. crear una fuente limpia del paper, no editar el archivo de ejemplo lleno de
   texto demostrativo;
4. compilar en US Letter, dos columnas, modo `compsoc`;
5. revisar el PDF página a página y comprobar fuentes, ecuaciones, tablas,
   enlaces, metadatos y texto extraíble;
6. medir la longitud real en ese formato antes de decidir qué pasa al
   suplemento.

No debe estimarse el número de páginas TDSC a partir del PDF Markdown actual.
