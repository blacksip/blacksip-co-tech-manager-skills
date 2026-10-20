## 1. Parser del `.md` (md_to_gdoc.py)

- [x] 1.1 Reconocer líneas `![alt](ruta)` como bloque `img` y separar las líneas mixtas (imagen + texto) en imagen y párrafo; verificar con el acta de People: 8 bloques `img` y ninguno pegado a texto
- [x] 1.2 Leer la sección `## ANEXOS` (`### Anexo X. Título` + tabla) sin romper `FIRMA`/`AUTOR`; verificar que `parse()` devuelve el Anexo A del acta de People con 6 filas y que `FIRMA` sigue dando sus 2 tablas
- [x] 1.3 Reconocer enlaces `[texto](#anexo-x)` en los párrafos, sin dejar `[..](..)` literal; verificar con el punto 5 del acta de People
- [x] 1.4 Promover una tabla suelta del desarrollo a un anexo nuevo (siguiente letra libre), dejando en su lugar un enlace, y avisar por stderr; verificar con un `.md` de prueba con una tabla de 4 columnas en el desarrollo

## 2. Anexos en el Doc

- [x] 2.1 Insertar al final, tras Autor, salto de página + "ANEXOS" (negrita) solo si hay anexos; verificar en el PDF exportado que "ANEXOS" abre una página nueva y que sin anexos el PDF no cambia
- [x] 2.2 Insertar por anexo su título (HEADING_2 re-estilado a 12 pt negrita) y una tabla real con encabezado en negrita, rellenando las celdas de abajo hacia arriba; verificar con un anexo de 5 columnas y con el de 2 columnas del acta de People
- [x] 2.3 Aplicar el enlace interno leyendo el `headingId` de cada título; verificar que el `textStyle.link` de "Anexo A" apunta al `headingId` del título y que una referencia sin anexo queda como texto plano con aviso

## 3. Imágenes en el Doc

- [x] 3.1 Escribir cada imagen como marcador `[[IMG:n]]` en su párrafo y reemplazarlo en una segunda pasada, de abajo hacia arriba y junto con los enlaces; verificar que no queda ningún marcador en el Doc del acta de People
- [x] 3.2 Subir las imágenes desde `adjuntos/<acta>/` a la carpeta de Drive `adjuntos-actas-temp` (creada si no existe) como `<acta>-NN-nombre.jpg`, abrir `anyoneWithLink`, insertar con ancho 440 pt y, en `finally`, borrar permiso y archivo; verificar ejecutando desde la raíz de `blacksip-co-scrum-of-scrum` (`actas/…md`, imágenes en `actas/adjuntos/<acta>/`) con las 8 imágenes que el Doc las tiene y que la carpeta de Drive no conserva ningún archivo; verificar que una imagen fuera del directorio actual produce el aviso y no aborta la conversión
- [x] 3.3 Probar el cierre ante fallo: forzar un error tras abrir el primer permiso y verificar que el permiso y el archivo de Drive se borran; verificar además que los nombres de los restos, si los hubiera, empiezan por el nombre del acta
- [x] 3.4 Pedir confirmación antes de abrir el permiso y añadir `--imagenes=incrustar|enlaces|ninguna`; verificar que sin confirmación no se comparte nada y que con `ninguna` no hay subida
- [x] 3.5 Caer a enlaces con aviso si `permissions.create` es rechazado; verificar simulando el rechazo (por ejemplo con un fallo forzado en esa llamada) que el Doc se crea sin imágenes y el aviso es claro

## 4. Skill `crear-acta-md`

- [x] 4.1 Añadir el paso de capturas: listar IDs y descripciones con `get_meetings`, filtrar por privacidad con las descripciones, bajar de a un ID con `get_meeting_attachment`, copiar el blob a `adjuntos/<acta>/NN-nombre.jpg`, comprimir y enlazar; verificar siguiendo el paso a mano con la reunión de Granola del 19-oct y comparando con las 8 imágenes ya obtenidas
- [x] 4.2 Documentar el plan B (pedir al usuario que baje las capturas) y la regla de unas 8 capturas; verificar que el `SKILL.md` lo dice
- [x] 4.3 Indicar que el desarrollo va en prosa o listas, las tablas solo en `## ANEXOS`, y la sintaxis de referencia `[Anexo A](#anexo-a)`; actualizar `acta-modelo.md` con un anexo de ejemplo y verificar que el modelo convierte sin avisos

## 5. Skill `acta-md-to-google-docs`

- [x] 5.1 Actualizar `SKILL.md`: dejar explícito que el comando se ejecuta desde la raíz del proyecto donde está `actas/` (con la ruta `actas/…md`), imágenes y anexos, la confirmación de exposición temporal, los modos y los nuevos límites conocidos (quitar "tablas dentro del desarrollo no se convierten"); verificar que el texto describe los modos y el aviso de exposición
- [x] 5.2 Corrida de integración con el acta de People: convertir y verificar 8 imágenes, anexo en la página final, enlace interno, sin marcadores ni temporales en Drive, y revisar el PDF
- [x] 5.3 Regresión: convertir el acta del Scrum of Scrum del 5 de octubre y verificar que el PDF es equivalente al de la versión 2.0.0 (sin imágenes ni anexos, sin salto de página)

## 6. Versión y cierre

- [x] 6.1 Subir `tm-actas` a 2.1.0 en `plugin.json` y ajustar su descripción; verificar que `version` es 2.1.0
- [x] 6.2 Ejecutar `openspec validate imagenes-en-actas --strict` y verificar que da "valid"
- [x] 6.3 Borrar los Docs de prueba que queden en Drive (`PRUEBA ...`) y verificar con una búsqueda en Drive que no queda ninguno
