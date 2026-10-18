---
name: seguimiento-hub-scrum
description: Lee el seguimiento semanal de proyectos y evoluciones del Hub de Blacksip (hub.blacksip.com/project-updates) y actualiza los bloques 3 (Proyectos en alerta) y 4 (Evoluciones en alerta) de la agenda del Scrum of Scrum, agregando por TM lo que no tiene reporte y cruzando contra asignacion-proyectos-tm.md. Úsalo siempre que el usuario pida preparar o llenar la agenda del Scrum of Scrum, revisar el estado o seguimiento de proyectos/evoluciones, ver quién no reportó en el Hub, actualizar proyectos o evoluciones en alerta, o validar que la asignación de TM esté al día, aunque no nombre el Hub ni el skill.
---

# Seguimiento Hub → agenda del Scrum of Scrum

**Requisitos.** Ejecuta todo desde la carpeta de trabajo del Scrum of Scrum (donde viven, en `agendas/`, `asignacion-proyectos-tm.md`, `plantilla-tarea-semanal.md` y las agendas `YYYY-MM-DD-scrum-of-scrum.md`; en repos con la estructura anterior estaban en la raíz). Los scripts del skill leen y escriben ahí: `.hub-profile/` (sesión del Hub) y `scripts/out/` (resultados). Necesitas Node 20+ y `playwright` instalado en esa carpeta (`npm i playwright`). Si falta `asignacion-proyectos-tm.md`, avisa y no sigas.

Convierte los reportes del Hub en los bloques 3 y 4 de la agenda y avisa si `asignacion-proyectos-tm.md` quedó desactualizado. Los TM reportan jueves/viernes, por eso la semana que normalmente se revisa es la anterior.

## 1. Confirmar la semana (siempre, antes de ejecutar nada)

Corre `node ${CLAUDE_SKILL_DIR}/scripts/cruce-hub.mjs --info` y pregunta al usuario (AskUserQuestion) con esas fechas reales:

> Hoy es <fecha>, estamos en la **semana N** (lun–dom). ¿Qué semana leo?
> - **Semana pasada: semana N-1 (lunes YYYY-MM-DD)** (Recomendada: se reporta jueves/viernes)
> - Esta semana: semana N (lunes YYYY-MM-DD)

Si elige esta semana, avisa que puede venir incompleta porque aún no se reporta. Guarda el lunes elegido como `<lunes>`.

## 2. Leer el Hub

```bash
node ${CLAUDE_SKILL_DIR}/scripts/hub-updates.mjs --week=<lunes>
```

Abre Chrome con el perfil `.hub-profile`. Si pide login, el usuario inicia sesión a mano (el script espera hasta 5 min). No intentes copiar el perfil real de Chrome del usuario. Genera `scripts/out/hub-<lunes>.json` con todas las tarjetas (estado, avance, texto, próximos pasos). Si falla por perfil bloqueado, pide cerrar la ventana de Chrome/codegen que lo tenga abierto.

## 3. Cruzar con la asignación

```bash
node ${CLAUDE_SKILL_DIR}/scripts/cruce-hub.mjs --week=<lunes>
```

Escribe `scripts/out/cruce-<lunes>.md` (resumen legible) y `.json` (alertas con el texto completo). El cruce compara nombres normalizados (sin tildes ni guiones) contra las tablas de TM de `asignacion-proyectos-tm.md`, que **manda sobre el PM del Hub**. Entrega, por TM: según lo planeado, en alerta y sin reporte; más dos listas de diferencias.

## 4. Actualizar el documento de la agenda

**Qué archivo actualizar.** La reunión es el lunes siguiente a la semana leída: `<lunes> + 7 días`. Con la semana 40 (lunes 2026-09-28), la reunión es el 2026-10-05 y el archivo es `agendas/2026-10-05-scrum-of-scrum.md`.
1. Si ese archivo existe, actualiza sus bloques 2, 3, 4 y 5.
2. Si no existe, créalo desde `agendas/plantilla-tarea-semanal.md` con esa fecha y rellena TODOS los bloques con las fuentes de esta corrida. Aunque aparezca borrado en git, no lo restaures ni lo tomes de `git show`, de borradores o de archivos viejos en `scripts/out/` (p. ej. `old-agenda.md`) ni reutilices su texto: «Riesgo → qué se pide» y las demás celdas se redactan de nuevo desde `hub-<lunes>.json` y `cruce-<lunes>.json`. Solo un archivo que existe en `agendas/` en este momento cuenta como «existente».
3. Di en la respuesta qué archivo vas a tocar y si es uno existente o nuevo. Si hay más de un candidato o la fecha no cuadra, pregunta con AskUserQuestion antes de escribir.

Respeta el formato existente: cada bloque es un título `##`; dentro, cada TM va como título `### Nombre Tech Manager` (no en negrita), con su tabla de excepciones debajo.

**Orden de los TM (bloques 3 y 4, siempre igual):** alfabético por nombre completo, sin tildes (Cristian Calderón, Heidy Romero, Jorge De la Cruz, Juan Manuel Viveros, Leonardo Villamil, Lucia Díaz, Miguel Castellanos, Raul Oidor, Victor Guevara) y «Sin TM definido» al final. Es el orden de `resumen-bloque4`; no uses el orden de `asignacion-proyectos-tm.md` ni una lista escrita a mano. Un TM sin filas ni «Sin reporte» no lleva sección. Los textos que cierran el bloque 4 (p. ej. «Diferencias con la asignación de TM») van después de la última sección de TM, no dentro de ella.

**Bloque 2 · Acuerdos abiertos** (desde ClickUp, no del Hub; lo pega `armar-agenda`)
- Corre `npm run resumen-acuerdos -- --semana=<lunes>` (lee la lista Scrum of Scrum por API; necesita `CLICKUP_API_TOKEN` en el entorno o en `~/.config/blacksip/.env`) para generar `reportes/resumen-acuerdos-<lunes>.md`. No lo pegues a mano: `armar-agenda` lo pone en la sección 2 sin cambios.
- Si el script falla (sin token o sin ClickUp), no inventes la tabla: dilo; el plan de `armar-agenda` avisará que falta y dejará la sección 2 como estaba.
- Si la sección 2 de la agenda ya trae notas de sala (Observaciones o Resultado) y el resumen cambió, `armar-agenda` no la reemplaza y lo avisa; pregunta al usuario antes de usar `--forzar`.

**Bloques 3 y 4 · Proyectos y evoluciones en alerta** (los arma el script `armar-agenda` del repo desde el cruce; no los escribas a mano)
- **Tablas de ClickUp del bloque 4.** Si no existe `reportes/resumen-bloque4-<viernes>.md` (`<viernes>` = `<lunes>` + 4 días), córrelo: `npm run resumen-bloque4 -- --semana=<lunes>` (refresca el export de ClickUp, ~2–3 min; corte = viernes completo; el sábado 8 am es la hora habitual). Si falla el refresco, pregunta al usuario si usas `--sin-refrescar` (export anterior, queda rotulado). Si el repo no tiene ese script, dilo.
- **Plan.** Genera antes el bloque 5 (`npm run resumen-bloque5 -- --semana=<lunes>`, ver más abajo): el bloque 7 sale de su Lectura rápida. Corre `npm run armar-agenda -- --semana=<lunes>` (no escribe). Muestra al usuario el archivo (existente o nuevo), los conteos, los avisos (resúmenes ausentes, fecha de reunión distinta, datos vencidos, notas del bloque 2) y los pendientes de redacción. Al aplicar reemplaza por completo las secciones 2, 3, 4, 5 y 7 (lo editado a mano dentro de ellas se pierde; el texto «Diferencias con la asignación de TM» del final del bloque 4 se conserva): si la agenda ya existe, pide confirmación antes de aplicar.
- **Pendientes de redacción.** Por cada uno, el plan imprime el `id` del Hub, su huella ya calculada y el texto y los próximos pasos del reporte. Escribe en `capacidad/datos/riesgos-hub.json`, bajo ese `id` y esa huella (la del plan, copiada sin calcular) `"<id>": { "<huella>": { "frase": "<riesgo → qué se pide, en una frase; no copies el reporte>", "golive": "<solo si el reporte lo dice>", "dueno": "<Nombre · fecha, solo si el reporte lo dice>" } }`. Agrega la huella al objeto del `id` sin borrar las otras (son de otras semanas). Lo que el reporte no diga se omite: el script lo marca **(confirmar)**. No toques las entradas que el plan no lista. Repite el plan hasta que diga «Sin pendientes de redacción».
- **Aplicar.** `npm run armar-agenda -- --semana=<lunes> --aplicar`. El script calcula la fecha de la reunión (el martes si el lunes es festivo) y escribe el encabezado `**Hora:**`; no renombres el archivo a mano. Si la reunión se mueve a otra fecha, pasa `--reunion=YYYY-MM-DD` en el plan y al aplicar, y también a `resumen-acuerdos` y `subir-agenda`. El `S.NN` es la semana ISO de la reunión, no de la semana leída. Deja en cada bloque la fuente con los conteos, una sección `###` por TM en orden alfabético (más «Sin TM definido» al final), la tabla de alertas, `⚠️ **Sin reporte (N):**` y, en el bloque 4, las tablas del resumen. Si el script falla o el repo no lo tiene, dilo; no armes los bloques a mano.
- El Hub no distingue proyecto de evolución: la tabla del `.md` decide (los soportes de operación de cuenta cuentan como evolución).

**Bloque 7 · Cierre** (lo escribe `armar-agenda` desde la caché `capacidad/datos/cierre-agenda.json`; no lo escribas en la agenda)
- Antes de aplicar, `resumen-bloque5` debe estar generado (el plan usa su Lectura rápida). Si el plan dice «Bloque 7: PENDIENTE de redacción», imprime la huella y el material (alertas de proyectos y evoluciones, «sin reporte» y la Lectura rápida). Escribe en `capacidad/datos/cierre-agenda.json`, bajo la fecha de la reunión y esa huella (copiada sin calcular), `{ "proyectos": "<alertas por estado con los nombres y los sin reporte>", "capacidad": "<lo más relevante de la Lectura rápida: sobrecarga, vacantes sin cubrir, ausencias>", "okr": "<solo si hay cifras; si no, omítelo>" }`. Sin inventar cifras. Repite el plan y aplica; el script escribe el encabezado del BlackOps Weekly (el martes de la semana de la reunión) y los tres puntos.
- Si el material no cambió, el plan reutiliza la entrada y no hay nada que redactar. Si el bloque 7 de la agenda ya trae texto escrito a mano y hay entrada, el script lo reemplaza: el plan lo avisa.

**Bloque 5 · Capacidad y equipo** (informe de capacidad del repo, no del Hub en vivo)
- Si `capacidad/capacidad-fila.json` no existe, corre `npm run capacidad`; si el repo no tiene el script, deja la sección 5 como está y dilo.
- Si hay entradas vencidas, **refréscalas sin preguntar** (una sola tentativa; este flujo ya lo corre Jose Ochoa, dueño de la sesión del Hub): `npm run estado -- --refrescar` (abre el Hub; si pide login el usuario lo hace a mano, el script espera) y luego `npm run capacidad`; relee el JSON. Si el refresco falla o se agota la espera, **no preguntes ni te detengas**: calcula con lo que haya (`npm run capacidad`) y sigue. Solo omite el intento si el usuario pidió explícitamente no refrescar.
- **Completa el análisis antes de pegar.** Tras el refresco (o si no hizo falta), compara `base_analisis` de `capacidad/capacidad-fila.json` con `fila.base` de `capacidad/datos/analisis-capacidad.json`. Si son distintos o falta el archivo, el análisis guardado se escribió sobre otras cifras y el informe lo omite: invoca la skill `analisis-capacidad` del repo (`.claude/skills/analisis-capacidad`) con la Skill tool. Ella lee los informes, reescribe `analisis-capacidad.json`, regenera con `npm run capacidad` y verifica con `npm run verificar-analisis` hasta que no haya errores. Si son iguales, no la invoques. No le pidas abrir el Hub ni refrescar (ya se intentó). Hazlo también si el refresco falló: el análisis se escribe sobre las cifras que haya. Si la skill no existe en el repo, sigue sin análisis y dilo.
- **Genera el resumen; `armar-agenda` lo pega.** Corre `npm run resumen-bloque5 -- --semana=<lunes>`: `armar-agenda` lo pone en la sección 5 sin reescribirlo, con la línea «Informe completo: subtarea **S.<n> …**» justo después de la fuente. El archivo trae, en este orden: el bloque `> ⚠️ **DATOS VENCIDOS**` (solo si quedan entradas vencidas o falló el refresco), la línea de fuente, Lectura rápida y Resumen con su análisis. Si el plan repite el aviso de análisis desactualizado, repite el paso anterior. Si el script falla, dilo; la sección 5 queda como estaba. No bloquees ni omitas la sección por datos vencidos.
- Este es el único texto de la sección 5: no inventes ni resumas cifras.

No dejes celdas con datos supuestos: lo que no esté en el reporte se marca **(confirmar)**.

## 5. Informar diferencias con asignacion-proyectos-tm.md

Lo que requiere decisión **ya está en la agenda**: `armar-agenda` escribe al final del bloque 4 la sección «Decisiones de asignación de TM» (evoluciones sin TM con Technology en el SOW, evoluciones sin SOW, tarjetas nuevas del Hub, filas del `.md` sin reporte semanal) y el plan imprime cada caso y lo que no entra (SOW sin Technology, internas, evoluciones de ClickUp). No la clasifiques ni la reescribas a mano: al final de la respuesta resume lo que imprimió el plan (cuántos casos y cuáles). Si el plan avisa que la sección tiene notas de sala en «Decisión», no uses `--forzar` sin preguntar. Si `hub/proyectos-hub.json` falta o es viejo (el plan imprime su fecha), dilo: se refresca con `npm run proyectos-hub` (abre el Hub).

Aparte, menciona (sin decidir) si el cruce trae nombres casi iguales entre el Hub y el `.md` (p. ej. «Portal B2B Agrícola Himalaya» y «Portal B2B Himalaya»): es diferencia de nombre y se propone unificarla.

Si el usuario aprueba cambios, edita las tablas de `asignacion-proyectos-tm.md` (y su sección de reasignaciones si el PM del Hub difiere) y actualiza los conteos del encabezado.

## 6. Subir la agenda a ClickUp (último paso, con confirmación)

Deja en ClickUp la tarea de la sesión (`[Scrum of Scrum] - S.<semana ISO> <Mes> <día>`, con la agenda como descripción) y la subtarea `S.<semana ISO> Informe de capacidad (criterio rol)`. Necesita `CLICKUP_API_TOKEN`; si falta o ClickUp no responde, dilo y termina sin escribir.

1. Corre el plan, que **no escribe**: `npm run subir-agenda -- --semana=<lunes>` (el mismo `<lunes>` confirmado en el paso 1).
2. Muestra el plan tal cual: qué tarea y subtarea crea o actualiza, si guarda copia de la descripción anterior como adjunto .md y por qué (plantilla del equipo, texto de una persona o **editada a mano**).
3. Pregunta con AskUserQuestion, citando la reunión y la semana del plan: «¿Subo la agenda y el informe de capacidad a ClickUp (reunión <fecha>, semana <N>)?» con opciones Sí, súbelos / No, déjalo en el plan.
4. Solo con un sí corre el mismo comando con `--aplicar` y resume lo hecho (enlaces de la tarea y la subtarea). Con un no o sin respuesta no escribas nada. Nunca pases `--aplicar` sin esa confirmación en esta corrida.
5. Si el plan dice «sin cambios», no preguntes: dilo y sigue.

Una corrida automatizada (sin usuario) debe pasar `--semana` y `--aplicar` de forma explícita; sin ellos no escribe.

## Cierre

Resume en pocas líneas: semana leída, conteos, cuántos TM tienen alertas, y cuántas diferencias de asignación quedan por decidir. Recuerda que `scripts/out/` no se versiona.
