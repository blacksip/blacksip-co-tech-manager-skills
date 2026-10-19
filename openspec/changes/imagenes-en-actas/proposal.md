## Why

Las reuniones con presentación (p. ej. el lanzamiento de Desempeño 2026 II) generan capturas de pantalla que explican mejor que el texto, pero el acta no las puede llevar: `crear-acta-md` no las contempla y `md_to_gdoc.py` las pega como texto literal (`![alt](ruta)`) en el Google Doc. Lo mismo pasa con las tablas dentro del desarrollo: hoy se pegan como una sola línea de pipes. Ambas cosas ya fallan con actas reales.

## What Changes

- `crear-acta-md`: paso opcional de capturas. Si Granola las trae (`get_meetings` lista sus IDs y descripciones), se filtran por privacidad usando las descripciones y se bajan con `get_meeting_attachment` **de a un ID por llamada** (en lote la respuesta supera el límite de ~6 MB y llegan solo descripciones). El cliente guarda cada imagen como PNG en disco y la ruta aparece en la salida de la herramienta; la skill la copia a `adjuntos/<acta>/NN-nombre.jpg`. Plan B: si el cliente no entrega archivo, pide al usuario que las baje. Selecciona pocas (unas 8), comprime (~120 KB), y las referencia con `![alt](ruta)` en su punto de la agenda.
- No hay otra vía oficial: la API REST pública de Granola (`/v1/notes`) expone notas, transcripciones y resúmenes, sin endpoint de adjuntos (según su documentación); no se usan herramientas no oficiales.
- Regla de privacidad: excluir capturas con datos personales (resultados o notas de personas, listas de nombres).
- `md_to_gdoc.py`: nuevo tipo de bloque `img`. Por defecto incrusta las imágenes en el Doc (subida a Drive, permiso público **temporal**, `insertInlineImage`, permiso cerrado siempre, incluso si falla). Pide confirmación antes de abrir el permiso y cae a enlaces de Drive si el dominio no permite compartir.
- `md_to_gdoc.py`: las tablas van como **Anexos** al final del Doc, en una página nueva tras la firma y el autor, como tablas reales de cualquier tamaño; el desarrollo las referencia con un enlace interno al anexo (`[Anexo A](#anexo-a)`). Una tabla suelta en el desarrollo se mueve sola a un anexo. `crear-acta-md` escribe prosa o listas en el desarrollo y las tablas solo en `## ANEXOS`.
- Subir `tm-actas` a 2.1.0.
- Iniciar OpenSpec en este repo (no había specs de las skills; las de `blacksip-tech_docs` son de contenido de formación).

## Validación previa

Probado con Drive y Docs reales (plantilla BlackSip y el acta de People, 8 capturas): el dominio permite compartir por enlace, la imagen se incrusta dentro de la celda del desarrollo y sigue en el Doc tras cerrar el permiso y borrar el archivo origen; `gws --upload` exige el archivo dentro del directorio actual; Docs no admite tablas anidadas en una celda. Detalle en `design.md`.

## Capabilities

### New Capabilities
- `acta-imagenes`: capturas en el acta `.md` (selección, privacidad, carpeta `adjuntos/`, sintaxis) y en el Google Doc (incrustación con permiso temporal, fallback a enlaces).
- `acta-anexos-tablas`: sección `## ANEXOS` con tablas markdown, y su conversión a tablas reales en una página nueva al final del Google Doc (incluye la promoción de tablas sueltas del desarrollo).

### Modified Capabilities

(Ninguna: el repo no tenía specs vigentes.)

## Impact

- `plugins/tm-actas/skills/crear-acta-md/SKILL.md` y `plugins/tm-actas/skills/acta-md-to-google-docs/` (`SKILL.md`, `scripts/md_to_gdoc.py`), `plugin.json` (2.1.0).
- Granola MCP: depende de que el cliente persista la imagen devuelta en disco (verificado en Claude Code); en otros clientes aplica el plan B manual.
- Drive/Docs: la subida de imágenes y el permiso público temporal requieren el alcance de Drive de `gws` y que el dominio permita compartir por enlace.
- Fuera de alcance: qué hace cada repo con los adjuntos (git, almacenamiento); la skill solo los genera.
