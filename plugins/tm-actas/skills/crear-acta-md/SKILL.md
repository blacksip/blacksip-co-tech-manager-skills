---
name: crear-acta-md
description: Crea un acta de reunión de BlackSip en Markdown (actas/YYYYMMDD-acta-<tema>.md) a partir de notas de Google (Gemini/Docs), Granola o texto pegado por el usuario. Pide confirmación de los compromisos antes de escribir el archivo. Úsala siempre que el usuario pida "crear/hacer/generar el acta", "pasar las notas a acta", "acta de la reunión", o pegue notas/transcripción de una reunión y quiera un acta, aunque no diga "markdown".
---

# crear-acta-md

Convierte notas de reunión en un acta `.md` con el formato fijo de BlackSip. El modelo de referencia es `references/acta-modelo.md` (en esta misma skill; datos ficticios): **léelo primero** y replica su estructura, tono y nivel de detalle.

## 1. Obtener las notas

Según lo que dé el usuario:
- **Texto pegado**: úsalo tal cual.
- **Granola**: busca la reunión con `mcp__granola__list_meetings` / `get_meetings` y, si hace falta, `get_meeting_transcript` (cargar con ToolSearch).
- **Google (Gemini/Docs)**: usa la skill `gws-docs` o `gws-drive` con el enlace o nombre del documento.
  Un Google Doc puede tener varias pestañas (`?tab=t.xxxx`), una por reunión. `read_file_content` y `download_file_content` del conector de Drive devuelven **sólo la primera pestaña**, que puede ser otra reunión: comprueba que el título y los asistentes correspondan. Para leer una pestaña concreta usa `gws docs documents get --params '{"documentId":"<id>","includeTabsContent":true}'` y filtra por el `tabId` del enlace. Si `gws` da error de autenticación, pide al usuario que ejecute `gws auth login`.
- Granola entrega nombres incompletos o apodos (`Roidor`, `Ingenieroti`, "Mauro" por Raúl Mauricio Oidor) y emails genéricos. Completa los nombres con lo que digan las notas y el resto de actas de `actas/`; si dudas, pregunta.
- Si hay varias fuentes (p. ej. Gemini + Granola), consolídalas y anótalo en Observaciones.

### Consolidar las fuentes

Las notas automáticas (Gemini, Granola) son un borrador con errores típicos; el acta es la versión limpia. Al compararlas con el acta de ejemplo se ve qué corregir:

- **Cifras y plazos que cambian durante la reunión**: Gemini registra propuestas intermedias (p. ej. "cerrar en 5 días") y luego el acuerdo final (7 días calendario). El acta lleva sólo lo acordado. Si dos fuentes difieren en una cifra (p. ej. "15 o 20 días" vs "15 días a un mes"), verifica en la transcripción y, si sigue la duda, pregúntalo.
- **Próximos pasos duplicados o con responsables genéricos**: Gemini repite tareas con otras palabras ("Crear formulario soporte" y "Crear formulario de soporte") y asigna a "La colectividad" o "El grupo". Fusiona duplicados y reemplaza por "Todos" o "OMEGA y Blacksip" según corresponda. Granola puede omitir al responsable de una tarea (p. ej. cerrar casos antiguos).
- **Hora de inicio y fin**: Gemini toma las horas exactas de Google Meet (están en el título del documento, p. ej. `2026/10/02 10:02 GMT-05:00`). Inicio: 1) Gemini, 2) Granola, 3) preguntar. Fin: 1) hora explícita de Gemini/Granola, 2) inicio + última marca de tiempo de la transcripción (p. ej. `01:03:51` tras un inicio 10:02 → 11:05; redondea al minuto), 3) preguntar. Si calculaste el fin con la transcripción, dilo al usuario para que lo corrija si no coincide con Meet. Sólo pregunta inicio y fin cuando no haya ninguna de estas fuentes.
- **Asistentes**: la lista de "Invitado" de Gemini son los convocados, no los asistentes. Los asistentes salen de lo que se dice en la reunión (p. ej. un practicante presentado en vivo); quien fue invitado y no habló ni se mencionó va en "Invitados que no asistieron". Confírmalo con el usuario.
- **Nombres mal transcritos** (p. ej. "Dilan Rios" vs Dilan Naranjo, "Julian"/"Julián"): unifica con la versión confiable y marca la duda.
- **Detalle**: el acta amplía las notas con matices de la transcripción (causas, ejemplos, advertencias). Úsala cuando las notas sean escuetas, pero no añadas nada que no se haya dicho.

Si falta algo que no se puede inferir de las notas (asistentes con email/empresa, hora de inicio/fin, firmantes), pregúntalo en un solo mensaje; no inventes. Lo que siga sin confirmarse se deja como `_(por confirmar)_`.

### Número de acta

Pregunta siempre (junto con las demás dudas, en el mismo mensaje) si el proyecto lleva **numeración continua** de actas y, de ser así, cuál número corresponde a esta (revisa antes los números de las actas existentes en `actas/` para proponer el siguiente). Si el usuario dice que no hay numeración continua, usa el número automático `YYYYMMDD-NN`: la fecha de la reunión y un consecutivo de dos dígitos de las actas de ese día, empezando en `01`. Calcula `NN` contando los archivos `actas/YYYYMMDD-*` ya existentes de esa fecha más uno (si el acta que vas a crear ya es la única, es `01`). Nunca dejes el campo vacío ni inventes un número sin preguntar.

## 2. Extraer y pedir confirmación de compromisos (obligatorio)

Antes de escribir el archivo, presenta al usuario una tabla **Tarea | Responsable (Nombre – Empresa)** con los compromisos detectados y pregunta explícitamente si es correcta, qué falta o qué sobra. **Espera su respuesta.** Los compromisos son lo que la gente cobra después; un responsable mal asignado o una tarea inventada genera conflictos, por eso nunca se escribe el acta sin este visto bueno. Incorpora los ajustes y sólo entonces continúa.

Reglas: una tarea por fila, verbo en infinitivo, responsable explícito. Si es de varios, "Todos" o "OMEGA y Blacksip" (como en el modelo). Si no hay responsable claro, pregunta.

## 3. Escribir el acta

Ruta: `actas/YYYYMMDD-acta-<tema-en-kebab-case>.md` (fecha de la reunión, no la de hoy). Crea `actas/` si no existe. Si el archivo ya existe, no lo sobrescribas sin preguntar.

Secciones, en este orden y con estos encabezados exactos:

1. `# ACTA DE SEGUIMIENTO DE PROYECTO — BlackSip`
2. `## INFORMACIÓN GENERAL DE LA REUNIÓN` — tabla de 5 columnas (`Campo | Detalle | | |`): Número de acta (el definido en "Número de acta" del paso 1), Proyecto, Lugar, Fecha de inicio y de finalización (`**Día** | Octubre 2 de 2026 | **Hora** | 10:00 am`), Asunto.
3. `## ASISTENTES` — tabla `Nombre | Email | Empresa`; fila `**Invitados que no asistieron**` y luego esos invitados.
4. `## DESARROLLO DE LA REUNIÓN` → `### Agenda` con `## **Objetivo de la reunión**` (un párrafo) y `## **Agenda**` (lista numerada); luego `### Desarrollo de la Agenda` con un `### **N. Tema**` por punto de la agenda. Narra en tercera persona y en pasado (quién dijo/propuso/acordó qué), con cifras y fechas en **negrita**. Escribe prosa, no transcripción. Acuerdos de flujo paso a paso van como lista numerada. Cierra con `### **N. Cierre**`.
5. `## CONCLUSIONES` — viñetas con las decisiones adoptadas; marca lo pendiente de validación como **Pendiente de validación técnica:** o similar.
6. `## COMPROMISOS` — la tabla confirmada en el paso 2.
7. `## FIRMA DEL ACTA` — tabla de dos columnas (Representante del Cliente / Representante de Blacksip) con tres líneas `&nbsp;<br>` de espacio para firma y debajo nombre y cargo; pregunta quiénes firman si no es evidente.
8. Tabla `**AUTOR**` con `Versión | Nombre | Fecha envío | Observaciones`: versión `1.0` (o la siguiente si es revisión), autor = el usuario (Jose Ochoa por defecto), fecha de envío = hoy (`YYYY-MM-DD`), observaciones = fuentes usadas (p. ej. "Consolidado de notas de Gemini y Granola").

Usa español. Respeta tildes y los nombres propios tal como aparecen en las notas.

## 4. Cerrar

Indica la ruta del archivo creado y señala en una línea lo que quedó `por confirmar`. No hagas commit salvo que el usuario lo pida.
