# ADICIO → GoHighLevel: rescate de la ronda 4 de Opus

Corte del 27/11/2026, hora argentina. Se reconstruyó el estado desde los avisos, checkpoints, mediciones del verificador y pruebas del compilador y del lienzo guardadas antes del 429. **No hubo publicación ni nuevos cambios en GHL en este rescate.** Las referencias a `fiel/…` y a los avisos son del expediente local `41-adicio-sitio/pasaje-ghl`, no de este repositorio. No se copian los registros brutos ni datos de la cuenta.

## Estado comprobado sobre los borradores reales

La isla v4 quedó guardada en las 14 páginas (M06 → C10, `isla_ok.py todas`: 14/14). La tanda r4c de 14:34–15:17 terminó (`r4c-fin.log`), y los 14 `datos.json` tienen `valida: true`. Se recupera esa tanda por encima del tablero intermedio. No se encontró un aviso V20 de cierre ni un «PASA ENTERA» para la tanda. Las mediciones de la tanda anterior, 14:19–14:31, fueron invalidadas (V19).

P1 = imagen; P2 = texto, cajas y líneas; P3 = contraste; P4 = movimiento muestreado; P5 = navegación; P8 = integridad/SEO. P1/P2/P3/P5/P8 a 1920/768/390. **P4 usó el muestreador base** a 1920 y 390, más 390 con movimiento reducido. No equivale a cobertura total del inventario. P6/P7 (lienzo y edición nativa reversible) no se midieron en ningún borrador de esta tanda.

En la tabla, todo lo no listado en «fallas» pasó **en esa corrida y dentro de su cobertura**, no en versiones posteriores. Carpeta de evidencia: `fiel/verificar/<página>/<corrida>/REPORTE.md` y `datos.json`.

| Página | Fallas en borrador real | Corrida r4c |
|---|---|---|
| Home | P1 ×5, P2 ×9, P3 ×3 (falso identificado, I11) | `20261127-145003` |
| Gestión | P1 ×3 (mapa) | `20261127-143958` |
| Adaptación | P1 ×1, P2 ×1 | `20261127-144002` |
| Cuidadores | P1 ×3 (mapa), P3 ×16 (cierre), P8 ×3 (el mismo sufijo `· ADICIO` faltante en el título SEO en los tres anchos) | `20261127-145218` |
| Sobre ADICIO | P2 ×9 | `20261127-144432` |
| Kit Bienestar | P1 ×11, P4 ×1 (ola a 1920) | `20261127-144920` |
| Tensiómetro | Ninguna en preview con el muestreador base | `20261127-150209` |
| Oxímetro | P2 ×1 (`≤ 90 %`, ancho −2,7 px a 1920) | `20261127-145843` |
| Reloj SOS | P2 ×1 (salto de línea a 390) | `20261127-150014` |
| Termómetro | Ninguna en preview con el muestreador base | `20261127-150850` |
| Gracias Gestión | P1 ×2 | `20261127-143456` |
| Gracias Cuidadores | P1 ×3 | `20261127-144002` |
| Gracias Adaptación | P1 ×3 | `20261127-143456` |
| Gracias Kit | P1 ×7 | `20261127-143456` |

**Totales del corte:** P1 5/14, P2 9/14, P3 12/14 tal como salió del verificador (la falla de Home es falsa, no se editó el resultado histórico), P4 13/14 con cobertura parcial, P5 14/14 (el verificador distingue enlaces heredados rotos), P8 13/14. Pasan todas las puertas de preview **medidas** solamente Tensiómetro y Termómetro: **2/14**. Cierre completo de migración: **0/14 verificado**.

## Hallazgos de preview y movimiento

| Aviso / dueño | Problema y causa | Evidencia y paso pendiente |
|---|---|---|
| M06 / I09 / C10 · Movimiento | Títulos estilizados con `display:contents` devuelven caja vacía; `hilo.js` omitía figuras a 390 y corría adornos a 1920. Medir solo el texto con `Range` dejaba un caso roto en reducido. | Usar la caja del envoltorio equivalente cuando contiene solo ese texto. En página de prueba: Gracias Gestión y Tensiómetro pasan P4; fuente contra fuente 0 y mutación de título sin caja falla. Guardado real en 14 y confirmado en r4c para lo que se muestreó. I09 también midió 19/19 figuras iguales en 5 páginas con el parche en memoria. |
| I08 / C11 · Compilador | La fila del calendario pinta por encima de la sombra de la tarjeta anterior en las páginas de gracias. El primer selector compilado perdía por especificidad. | Sonda de franja: en Gracias Gestión a 390, 2.752 píxeles distintos → 0 con inyección en memoria; también dio 0 en otras muestras, pero en Gracias Kit quedó un residual. El selector corregido debe ganar al puente que impone `position:static` sin cambiar el orden de otras capas. No hay cierre de la familia en los borradores. |
| I10 / I15 · Movimiento + Compilador | Los widgets de Gracias Kit y Home alteran la posición fraccional de lo que viene abajo: se rasteriza distinto aunque las cajas y fuentes coincidan. | CSS inyectado: compensación de 0,203 px en Gracias Kit, y 0,407 px en el pie de Home (768/390), llevó las franjas medidas a 0. Pendiente un ajuste robusto que siga el tamaño real del widget y preserve la fracción de altura de la fuente; confirmar también a 1920. No convertir los números de la sonda en constantes globales. |
| I12 / C11 · Compilador | Home: el widget más alto centra el texto del newsletter 36 px abajo; al reemplazar la maqueta del contacto se pierde el mínimo de 362 px de la columna a 390 (−12 px). | `d7b` y `d7min` dieron P2 pasa en la página de prueba (`r4h/home`, 14:59). P1 todavía tiene 3 diferencias ahí. Acotar la regla de ancho a su breakpoint: sin ese límite rompe escritorio. No confirmado en borrador. |
| I13 · Movimiento | En Cuidadores, el calendario estira la placa azul del cierre y el degradé aclara el fondo bajo textos que están fuera de la banda excluida. Es una falla real de contraste, no el falso positivo de Home. | Compensar el alto del widget dividiendo y recortando la placa; con la prueba en memoria, el delta de color bajo los textos bajó de hasta 26 a ≤4 a 768 y de hasta 9 a ≤4 a 1920. Falta integrar y volver a medir P1/P3 en los tres anchos. |
| I14 · Compilador | En Gestión y Cuidadores, la traducción de `.fila-zona h2+p` deja que la regla salte entre columnas hermanas, aplica margen de 16 px donde no va y desplaza la nota y el botón del mapa. | El CSS de control restituye posiciones en 6/6 combinaciones. Limitar el envoltorio del combinador `+`/`~` a envoltorios de texto, no filas/columnas: el censo en 14 previews, a 1920 y 390, solo quitó los dos nodos indebidos; no agregó ninguno. Probar compilado en página de prueba y luego en borrador. |
| C10/C11 · Compilador | `wrap`: GHL corta palabras que la fuente no corta. `urange`: los subconjuntos de Google Fonts dejan glifos en la fuente de respaldo que el archivo completo sustituye. `hijo`: la traducción de `>` captura nodos de la animación del Kit y desarma su aura. | En página de prueba (`r4n`, sin P4), Kit, Reloj SOS, Adaptación y Sobre ADICIO pasaron P1/P2/P3/P5 a los tres anchos. El SEO vacío de esa página de prueba no prueba P8. El parche para el glifo de oxímetro pasó la prueba controlada de caja (116,6 → 114,5 → 116,6); falta cierre aislado del producto. No extender todos los flags en bloque. |
| C11 / `r4h/gestion` · Compilador | La página de prueba de Gestión empeoró en el bloque 3 (íconos y posición del texto), pese a que el borrador r4c tenía P2 verde. | Causa pendiente: el compilador sospechó del estado hover o una interacción con `hijo`. Repetir la misma versión sola, puntero fuera del bloque, y comparar con/sin `hijo`. No promover esa compilación. |
| C11 · Movimiento + Verificador | En la página de prueba, Oxímetro a 1920 terminó en el paso 02, no 04, **con y sin** `hijo`. El estado depende del recorrido de scroll y el observador de intersección. | No atribuirlo a `hijo` ni a la isla sin comparar trayectorias equivalentes. El borrador real r4c no reprodujo el fallo de P1/P4; solo falló el glifo de P2. Probar el recorrido de `sonda_recorrido.py` y el mismo estado activo en ambos lados. |
| r4c P4 Kit · Movimiento | A 1920, una muestra de la ola del Kit (`--r6-ola-y`, scroll con retardo) dio −31,43 vs −78,29 en `s9.3+900`. A 390 normal y reducido pasó. | Evidencia `fiel/verificar/kit/20261127-144920/p4/REPORTE.md`. Se había visto inestabilidad antes; no clasificar como falso ni como corregido. Repetir aislado con el mismo reloj/recorrido y comprobar la trayectoria además del valor final. |

### Falsos positivos y alcance del verificador

- **V19, P2/P8:** la isla v4 cambió lo que veía la sonda de visibilidad de los títulos. Dio «faltan textos» y «sin H1» aunque los títulos estaban. El verificador pasó a usar los métodos de geometría nativos capturados antes de cargar la página. Se comprobó en Gracias Gestión a 1920/390 (pasan P2/P8, control fuente contra sí misma = 0, mutación detectada). No reutilizar el lote invalidado.
- **I11, P3 Home:** se cruzaba el label «Email» del newsletter (oscuro sobre menta) con el título «Email» del contacto (blanco sobre azul). Emparejar primero por bloque y texto, luego permitir coincidencias sueltas solo dentro de la misma clase (maqueta/widget o texto normal). Sobre medidas guardadas, pares cruzados 1 → 0 en los tres anchos; no cambian los conteos de pares ni dos páginas de control. Documentado como propuesta probada, no como arreglo publicado en el verificador de r4c. Conservar la prueba de contraste real de Cuidadores.
- **V17, cobertura P4:** se preparó `fiel/movimiento/muestrear_r4.py` para ampliar las familias medidas. La tanda oficial usó el muestreador anterior (sello `c284f6f531`), no el ampliado. Falta probar este último con fuente contra sí misma y mutaciones por familia, certificar el inventario por página (hover/foco, menú, acordeones, puntero, canvas, GSAP, contadores, capas, etc.) y publicar el cambio antes de re-medir. No confundir un efecto montado con el mismo movimiento.

## Editor: listo en prueba, no en los borradores

- **L04, 4 gracias:** P6a sin fallas y P7 pasa en la página de pruebas de Lienzo (`gg-16`, `gc-2`, `ga-3`, `gk-2`). El editor partía las palabras dentro del enlace por CSS de TipTap; perdía variables inline como `--n:2` (una grilla terminaba con 3 columnas) y se comía el margen del `©`. Se corrigió bajo `#previewer` (Lienzo L6 + Átomos A3). Contra la compilación sin ese agregado: `sections`, `trackingCode` y CSS de preview iguales; el aislamiento dinámico de Gracias Gestión comprobó que ninguna de las 776 reglas adicionales aplica a la preview a 1920/768/390. C11 comprobó que lo que faltaba guardar en los cuatro borradores era solo CSS de lienzo. **Pendiente:** repasar después de liberar turno, marcar «listo P6/P7» y probar cada borrador real con el verificador independiente.
- **Termómetro:** 260 → 232 al corregir el pie, → 214 al corregir el FAQ, → **211** en `te-6` (69 escritorio, 81 tablet, 61 móvil) después de ajustar la especificidad de los enlaces. **P7 no medido** en `te-6`; su lista vacía no significa que pasó. El remanente incluye textos ausentes, de más, unidos y cajas corridas. Separar el defecto de estructura del de CSS antes de extenderlo al resto de fichas.
- **D13, piezas nativas:** TipTap une texto principal y secundario cuando recibe átomos (CTA con `<b>` + `<small>`, chips, precios, KPIs). No ocultar el problema en el verificador aceptando texto concatenado. Inventario de Gestión: 31 átomos (`fiel/compilar/inv_atomos.py` y checkpoint del compilador); se exploró botón nativo con subtexto o un elemento por pieza. No se encontró cierre de D13 en página de prueba/borrador; primero probar con Gestión y verificar que P1–P5/P8 y el movimiento no retrocedan. Después, edición real, reapertura y restauración exacta.

## Orden para retomar

1. Tomar r4c como base recuperada, publicar su estado y asignar turno explícito de escritura. No medir mientras se guarda ni cambiar de muestreador a mitad de tanda (K23/K24/K26). Registrar versión, inicio/fin, sello de borrador y hash del muestreador. Repetir controles pesados de forma aislada: la contención dio falsos positivos (K25). Usar turnos de hasta 15 min en la página de prueba compartida y anotar el checkpoint al terminar cada hallazgo (K27).
2. **Primero la preview:** priorizar los arreglos de prueba que desbloquean Kit, Reloj SOS, Adaptación y Sobre ADICIO; aislar las regresiones de Gestión y Oxímetro; después resolver sombra/fase, mapa, Home y contraste/SEO de Cuidadores. Aplicar y verificar el emparejamiento de I11 antes de volver a fallar Home por el contraste. Medir el compilado exacto antes y después; respetar calendarios y formularios ya conectados.
3. Certificar el inventario de movimiento con el muestreador ampliado y verificar la ola del Kit. No dar por hecho que un resultado de preview estático cubre las animaciones.
4. Repasar las 4 gracias con CSS de lienzo L6/A3; repetir P6/P7 en sus borradores. En paralelo, validar D13 primero en Gestión y retomar Termómetro, que ya pasó la preview medida pero tiene 211 diferencias de editor. Para cerrar D17, todas las puertas deben pasar en **la misma versión del borrador real**, con cobertura del inventario y edición reversible.

### Sitio de revisión separado

[adicio-web.vercel.app](https://adicio-web.vercel.app) sirve la fuente animada (home + 13 subpáginas): 14 rutas + 116 recursos verificados por HTTP en el despliegue, y 42 recorridos de navegador a 1920/768/390 sin errores de página/red detectados, imágenes rotas, enlaces internos sin destino ni desborde horizontal. Los 33 videos montados en esos recorridos cargaron. Es una revisión `noindex`, sin cobro ni envío y sin reemplazar el dominio actual. Esta prueba no certifica paridad de animaciones en GHL ni edición desde su lienzo.
