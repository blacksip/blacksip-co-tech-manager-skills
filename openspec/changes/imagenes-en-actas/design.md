## Context

`md_to_gdoc.py` (stdlib + CLI `gws`) copia la plantilla y rellena celdas con `insertText`, de mayor a menor índice. El desarrollo de la agenda vive en **una sola celda** (tabla 1, fila 4, columna 0). Hoy `blocks()` solo conoce `p | ol | ul`: una línea `![alt](ruta)` sale como texto y una tabla markdown como una línea de pipes. Ver `proposal.md` para el motivo.

Validado con pruebas (Drive/Docs reales, cuenta de jochoa, plantilla real y el acta de People):

- El dominio permite compartir "cualquiera con el enlace" (`anyoneWithLink`, sin descubrimiento).
- `insertInlineImage` con `https://drive.google.com/uc?export=download&id=<id>` funciona dentro de la celda del desarrollo.
- La imagen queda **copiada** en el Doc: sigue ahí tras cerrar el permiso y borrar el archivo origen (comprobado con `inlineObjects` y exportando a PDF).
- Con el acta de People, las 8 imágenes entraron en su punto (ancho 440 pt; la celda mide ~460 pt) y el Doc pasó de 4 a 11 páginas.
- `gws drive files create --upload` solo acepta archivos **dentro del directorio actual**.
- Docs no admite tablas anidadas dentro de una celda.

## Goals / Non-Goals

**Goals:**
- Que las capturas del `.md` aparezcan dentro del Doc, en su punto de la agenda, sin dejar nada público ni huérfano en Drive, aunque el script falle.
- Que las tablas del acta se lean bien en el Doc (tablas reales, de cualquier tamaño, como Anexos en página nueva), sin pegar pipes.

**Non-Goals:**
- Subir un adjunto a Drive que quede como archivo permanente, o compartir el Doc (la skill ya no comparte ni mueve nada sin pedirlo).
- Tablas complejas (celdas combinadas, formato por celda), imágenes fuera de la celda del desarrollo e imitar la barra negra de la plantilla en el título "ANEXOS" (queda como texto en negrita).
- Decidir qué hace cada repo con `adjuntos/` (git u otro).

## Decisions

**1. Marcadores y segunda pasada.** `parse()` convierte cada línea-imagen en un bloque `img`; `build()` escribe el texto con un marcador `[[IMG:n]]` como párrafo propio y, en una **segunda pasada**, busca cada marcador en el Doc ya creado y, de abajo hacia arriba, hace `deleteContentRange` + `insertInlineImage` en ese índice. Alternativa descartada: insertar la imagen en la misma pasada que el texto, que obligaría a recalcular todos los índices de estilos y viñetas (cada imagen ocupa 1 índice).

**2. Permiso temporal con borrado.** Por imagen: subir directamente desde `adjuntos/<acta>/`. La skill no tiene ejecutor propio: Claude corre el comando de su `SKILL.md` con el directorio actual en la **raíz del proyecto donde está `actas/`** (como se hizo con `actas/20261019-…md` en `blacksip-co-scrum-of-scrum`), por lo que las imágenes quedan bajo el directorio actual, que es lo que exige `--upload`. Las rutas de imagen del `.md` se resuelven relativas a la carpeta del `.md` y se pasan a `gws` relativas al directorio actual; si una queda fuera de él, se avisa y esa imagen cae a enlaces u omitida, a la carpeta de Drive `adjuntos-actas-temp` (se busca por nombre en Mi unidad y se crea si no existe), nombrando el archivo en Drive `<acta>-NN-nombre.jpg` con el nombre del acta, `permissions.create anyone/reader`, insertar, y al terminar `permissions.delete` + `files.delete` del origen, todo en `finally`. Se borra el archivo además de cerrar el permiso porque el Doc ya tiene su copia. No se hace copia local: las imágenes ya viven en `adjuntos/<acta>/`. El nombre con el acta y la carpeta de Drive dedicada permiten localizar y borrar a mano cualquier resto si el script muere antes del `finally`. Alternativa descartada: dejar las imágenes en una carpeta "Adjuntos" de Drive con permisos del dominio; sirve para enlaces, pero no para ver la imagen en el Doc con la API actual sin exposición.

**3. Confirmación y modo.** Antes de abrir el permiso la skill pide confirmación una vez por documento (publica contenido interno unos segundos). `--imagenes=incrustar` (por defecto con confirmación) | `enlaces` | `ninguna`. Si `permissions.create` falla (política del dominio), se cae a `enlaces` y se avisa; no se aborta el Doc.

**4. Imagen en línea propia.** La skill escribe cada imagen como su propio párrafo. Además `blocks()` separa líneas mixtas (`![..](..) texto`) en imagen + párrafo, porque esa mezcla ya apareció al editar a mano y el resultado era que la imagen se ignoraba.

**5. Tablas como Anexos en página nueva.** Las tablas van en una sección `## ANEXOS` del `.md` (`### Anexo A. Título` + tabla), y el desarrollo las referencia con "ver Anexo A". En el Doc, al final y después de la tabla Autor, el script inserta un salto de página (`insertPageBreak` al final del cuerpo), el título "ANEXOS" y, por cada anexo, un título y una tabla real (`insertTable` al final del cuerpo, encabezado en negrita). Las tablas del anexo van tras el resto del contenido para no mover índices. Si queda una tabla suelta dentro del desarrollo, el script la promueve a un anexo nuevo y deja "ver Anexo N" en su lugar; nunca pega pipes. Sin anexos no hay salto de página ni título. **Enlace interno:** en el `.md` la referencia se escribe `[Anexo A](#anexo-a)`; el título de cada anexo se inserta con estilo `HEADING_2`, que Docs le asigna un `headingId`, y el script, en la segunda pasada (junto con las imágenes), lee ese id y aplica `updateTextStyle` con `link.headingId` sobre el texto de la referencia. Se vuelve a estilar el encabezado (tamaño y negrita) para que no cambie la apariencia de la plantilla. Un enlace `#anexo-x` sin anexo correspondiente se deja como texto plano y se avisa. Validado: el salto deja "ANEXOS" al inicio de una página nueva, la tabla de 5 columnas se ve bien y el enlace desde la celda del desarrollo al encabezado del anexo funciona (también en el PDF exportado). Alternativas descartadas: viñetas "col A: col B" (se rompen con tablas anchas o largas) y tablas anidadas (Docs no las admite). Las tablas de Asistentes, Compromisos, Firma y Autor no cambian.

**6. Ancho.** Solo `objectSize.width` = 440 pt; el alto se ajusta solo.

## Risks / Trade-offs

- [Un administrador restringe el compartir por enlace para otros TM] → fallback automático a enlaces y aviso claro.
- [El script muere entre abrir el permiso y cerrarlo] → `finally` con `permissions.delete` y `files.delete`; además cada archivo temporal lleva un prefijo identificable para borrarlo a mano.
- [Exposición breve de contenido interno] → ventana de segundos, ID no adivinable, confirmación previa y regla de privacidad de la skill (nada con datos personales).
- [El Doc crece (4 → 11 páginas con 8 capturas)] → la skill limita a unas 8 capturas.
- [La celda del desarrollo se parte entre páginas con imágenes grandes] → aceptado: no rompe el formato.
- [Cada imagen = subir + permiso + borrar: más llamadas a la API y más lento] → aceptado; son pocas imágenes por acta.

## Migration Plan

Cambio aditivo. Las actas sin imágenes ni tablas en el desarrollo se convierten igual que hoy. Subir `tm-actas` a 2.1.0; quienes ya tienen la 2.0.0 reciben la actualización con la nueva versión. Reversión: volver a la 2.0.0 (las actas con imágenes saldrían como hoy, con el texto literal).
