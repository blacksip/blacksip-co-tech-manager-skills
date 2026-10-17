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
1. Si ese archivo existe, actualiza sus bloques 2, 3 y 4.
2. Si no existe, créalo desde `agendas/plantilla-tarea-semanal.md` con esa fecha.
3. Di en la respuesta qué archivo vas a tocar y si es uno existente o nuevo. Si hay más de un candidato o la fecha no cuadra, pregunta con AskUserQuestion antes de escribir.

Respeta el formato existente: cada bloque es un título `##`; dentro, cada TM va como título `### Nombre Tech Manager` (no en negrita), con su tabla de excepciones debajo.

**Bloque 2 · Acuerdos abiertos** (desde ClickUp, no del Hub)
- Corre `npm run resumen-acuerdos -- --semana=<lunes>` (lee la lista Scrum of Scrum por API; necesita `CLICKUP_API_TOKEN` en el entorno o en `~/.config/blacksip/.env`) y toma `reportes/resumen-acuerdos-<lunes>.md`.
- Reemplaza la tabla vacía de la sección 2 por la del archivo, sin reescribirla ni cambiar columnas; copia la leyenda de estados y la línea de fuente, y deja "Observaciones" y "Resultado" en blanco (se llenan en sala). El archivo ya trae Responsable primero (una vez por persona), el emoji de estado en cada acuerdo y `S.<semana> · fecha · retraso` en Fecha original. Si no hay acuerdos abiertos, deja el texto que trae el archivo.
- Abierto = subtarea de una reunión anterior que no está en `done` ni `Closed`, haya vencido o no. Si el script falla (sin token o sin ClickUp), no inventes la tabla: dilo y deja la sección 2 como estaba.

**Bloque 3 · Proyectos en alerta** (tipo Proyecto)
- Por TM, tabla con los proyectos en 🔴 desviación, 🟡 riesgo o 🟣 suspendido: `Proyecto | 🚦 | Avance · Go live | Riesgo → qué se pide | Dueño · fecha`. El riesgo y la petición salen del texto y los próximos pasos del reporte, resumidos en una frase; no copies el reporte.
- Debajo de cada TM, una línea nueva con `⚠️ **Sin reporte (N):**` (N = cantidad de ítems) y, justo después de los dos puntos, en la misma línea, la lista de proyectos que no reportaron; si N es 0, omite la línea (el cruce los entrega por TM). Quien no reportó no ocupa tiempo de sala: se le pide actualizar el Hub.
- Los proyectos en verde no se mencionan: el bloque es por excepción. Solo aparecen alertas y «Sin reporte».
- Actualiza la línea de fuente con los conteos reales (reportaron, por estado, sin reporte) y la línea de cierre del bloque 7.

**Bloque 4 · Evoluciones en alerta** (tipo Evolución)
- Mismo criterio con las evoluciones que el Hub reporta en alerta, por TM, más su línea `⚠️ **Sin reporte (N):** lista`, igual que en proyectos, también bajo un `###` por TM.
- Cuentas con consumo fuera de rango y soportes fuera de SLO vienen de ClickUp, no del Hub; no las calcules ni las inventes. Las genera el script del repo: corre `npm run resumen-bloque4 -- --semana=<lunes>` (refresca el export de ClickUp, ~2–3 min; corte = viernes completo; el sábado 8 am es la hora habitual) y toma `reportes/resumen-bloque4-<viernes>.md` (`<viernes>` = `<lunes>` + 4 días). El archivo trae una sección `### <TM>` por cada TM con excepciones, cada una con su tabla "Cuentas con consumo fuera de rango" y después su tabla "Soportes fuera de SLO". Pega cada par de tablas tal cual al final de la sección del mismo TM en el bloque 4, en ese orden, después de sus alertas del Hub y de "Sin reporte" (si el TM no tiene sección, créala; "Sin TM definido" va al final); no dejes tablas sueltas fuera de los TM ni las reordenes ni repitas la cuenta (en soportes va solo en su primera fila). Copia una sola vez, en la línea de fuente del bloque, el resumen y la leyenda de "Cuentas con consumo fuera de rango" que trae el archivo. Deja en blanco "Acción · dueño · fecha". Actualiza la línea de fuente con el corte y la fecha del export y copia los avisos (⚠️) si los hay. Si falla el refresco, pregunta al usuario si usas `--sin-refrescar` (export anterior, queda rotulado). Si el repo no tiene ese script, deja las tablas como estén y dilo.
- El Hub no distingue proyecto de evolución: la tabla del `.md` decide (los soportes de operación de cuenta cuentan como evolución).

No dejes celdas con datos supuestos: lo que no esté en el reporte se marca **(confirmar)**.

## 5. Informar diferencias con asignacion-proyectos-tm.md

Al final de la respuesta, tras mostrar el resultado, incluye estas dos secciones aunque estén vacías (di «ninguno»):

1. **Nuevos en el Hub, no están en el .md.** Lista cada uno con su PM del Hub y si ese PM es uno de los TM considerados (Leonardo Villamil, Lucia Díaz, Victor Guevara, Raul Oidor, Heidy Romero, Jorge De la Cruz, Cristian Calderón, Juan Manuel Viveros, Miguel Castellanos). Los de un TM considerado, o de PM que ya tenga reasignación, se priorizan y se **sugiere agregarlos** indicando TM y tipo (Proyecto/Evolución) propuestos. No edites el `.md` sin que el usuario confirme: la asignación es decisión suya. Antes de listarlo como nuevo, revisa que no sea solo una diferencia de nombre (p. ej. «Agrícola Himalaya · Implementación Portal B2B» vs. «… Portal B2B Agrícola Himalaya»); si lo es, dilo como diferencia de nombre y propón unificarla.
2. **Están en el .md, no aparecen en el Hub.** Sepáralos en: (a) los marcados *fuera del Hub* (esperados), (b) evoluciones de cuenta que viven en ClickUp y no tienen ficha en el Hub (esperable, pero menciónalo), (c) el resto, que pueden estar finalizados/suspendidos y ocultos por el filtro del Hub, renombrados o mal escritos. Pide revisarlos.

Si el usuario aprueba cambios, edita las tablas de `asignacion-proyectos-tm.md` (y su sección de reasignaciones si el PM del Hub difiere) y actualiza los conteos del encabezado.

## Cierre

Resume en pocas líneas: semana leída, conteos, cuántos TM tienen alertas, y cuántas diferencias de asignación quedan por decidir. Recuerda que `scripts/out/` no se versiona.
