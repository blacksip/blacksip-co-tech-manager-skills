---
name: acta-md-to-google-docs
description: Convierte un acta de reunión BlackSip en Markdown (actas/YYYYMMDD-acta-<tema>.md, la que genera crear-acta-md) en un Google Doc nuevo, copiando la plantilla "Template/Plantilla - Acta de seguimiento de proyecto" y rellenándola. Úsala siempre que el usuario pida pasar/subir/exportar/publicar un acta a Google Docs o Drive, "crear el doc del acta", "acta en la plantilla", o quiera compartir o enviar el acta como documento, aunque no mencione la plantilla ni "markdown".
---

# acta-md-to-google-docs

Copia la plantilla de Drive y escribe en ella el contenido del acta `.md`, conservando el formato corporativo (logo, encabezados negros, tablas). Hacerlo con el script evita errores de índices en el Docs API y mantiene idénticos todos los documentos.

## Uso

```bash
python3 <directorio-de-esta-skill>/scripts/md_to_gdoc.py actas/YYYYMMDD-acta-<tema>.md
```

**Ejecútalo siempre desde la raíz del proyecto donde está `actas/`** (ruta `actas/…md`): `gws --upload` solo acepta archivos dentro del directorio actual y las imágenes viven en `actas/adjuntos/<acta>/`.

`<directorio-de-esta-skill>` es la carpeta donde está este `SKILL.md` (el "directorio base" que informa el cliente al cargar la skill); el script vive en su subcarpeta `scripts/`. Funciona igual en Claude Code (plugin) y en opencode.

Opciones: `--folder <id>` (por defecto la copia queda en la carpeta de la plantilla), `--name "<título>"` (por defecto `YYYY-MM-DD - Acta <Número de acta> - <Asunto antes de ":">` (el número se copia tal cual del campo "Número de acta", sea `20261002-01` o un consecutivo como `12`; si el campo está vacío se omite). Empezar por la fecha hace que el orden alfabético sea también cronológico), `--template <id>` (por defecto la plantilla de BlackSip), `--imagenes incrustar|enlaces|ninguna` (por defecto `incrustar`).

El script imprime la URL del documento. Entrégasela al usuario.

## Imágenes y anexos

- **Imágenes** (`![alt](ruta)` en su propia línea): se incrustan en su punto del desarrollo. Para eso el script sube cada imagen a la carpeta de Drive `adjuntos-actas-temp` (la crea si no existe) como `<acta>-NN-nombre.jpg`, la abre unos segundos a "cualquiera con el enlace", la inserta (queda copiada dentro del Doc) y **siempre** cierra el permiso y borra el temporal, aun si falla. **Antes de ejecutar, si el acta tiene imágenes, pide confirmación al usuario** de esa exposición temporal; si no confirma, usa `--imagenes enlaces` (deja el texto `[Imagen: …]`) o `ninguna`. Si el dominio rechaza compartir, o la imagen queda fuera del directorio actual, esa imagen queda como texto y se avisa; el Doc se crea igual. Si quedara algún resto, estará en `adjuntos-actas-temp` con el nombre del acta.
- **Anexos** (`## ANEXOS` con `### Anexo X. Título` + tabla): se insertan al final del Doc, tras Autor, en una página nueva con el título «ANEXOS» y una tabla real por anexo. Las referencias `[Anexo A](#anexo-a)` del cuerpo son enlaces internos. Una tabla suelta en el desarrollo se mueve sola a un anexo nuevo y el script avisa.

## Antes de ejecutar

1. Confirma que existe el `.md` y que sigue la estructura de `crear-acta-md` (secciones `## INFORMACIÓN GENERAL…`, `## ASISTENTES`, `## DESARROLLO…`, `## CONCLUSIONES`, `## COMPROMISOS`, `## FIRMA DEL ACTA`). Nunca elijas el acta por tu cuenta: si el usuario no indicó el archivo, o dio uno ambiguo, pregunta cuál convertir preguntándoselo al usuario (herramienta de preguntas del cliente), ofreciendo como opciones las 3 actas más recientes de `actas/` (ordena por el prefijo `YYYYMMDD` del nombre, de más nueva a más antigua) y la opción de indicar otra. Espera su respuesta antes de ejecutar el script.
2. Cada ejecución crea un documento **nuevo** en Drive; no hay forma de actualizar uno ya creado. Si el usuario quiere cambios, edita el `.md` y vuelve a generar, y avísale de que el anterior queda en Drive para borrarlo.
3. Si `gws` falla con `invalid_grant` / `invalid_rapt`, el token de Google venció: pide al usuario ejecutar `gws auth login` (no puedes hacerlo tú, es interactivo) y reintenta.

## Qué hace

- Copia la plantilla con `gws drive files copy`.
- Añade filas en ASISTENTES (plantilla trae 4) y COMPROMISOS (trae 6) si el acta tiene más.
- Rellena celdas respetando las celdas combinadas: negritas `**…**` y cursivas `_(…)_`, listas numeradas (agenda, flujos) y viñetas (conclusiones). Escribe de abajo hacia arriba para que los índices no se desplacen.
- "Número de acta" queda vacío si el `.md` no lo trae.

## Después de ejecutar

Verifica visualmente: exporta a PDF y míralo (`gws drive files export --params '{"fileId":"<id>","mimeType":"application/pdf"}' -o out.pdf`). Comprueba que no falte ninguna sección, que las filas añadidas conserven el formato y que la firma muestre nombre y cargo. No compartas el documento ni lo muevas de carpeta sin que el usuario lo pida.

## Límites conocidos

- Depende de la estructura actual de la plantilla (tablas y posiciones de celdas fijas en `build()`). Si el equipo cambia la plantilla, hay que ajustar los índices de tabla/fila/columna allí.
- Las horas largas (`10:00 am`) se parten en dos líneas por el ancho de la celda de la plantilla.
- Solo soporta párrafos, listas numeradas y con viñetas, negrita y cursiva; las tablas se convierten como anexos (sin celdas combinadas ni formato por celda) y las imágenes solo dentro del desarrollo.
