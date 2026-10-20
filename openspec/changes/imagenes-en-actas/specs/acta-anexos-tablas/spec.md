## Purpose

Define cómo las tablas de un acta se muestran en el Google Doc: como anexos con tablas reales en una página nueva al final, referenciados con enlaces internos desde el cuerpo del acta.

## ADDED Requirements

### Requirement: Sección de anexos en el acta markdown
Un acta SHALL poder declarar anexos en una sección `## ANEXOS`, con un `### Anexo X. Título` por anexo seguido de una tabla markdown. El cuerpo del acta SHALL referenciar cada anexo con un enlace `[Anexo X](#anexo-x)`. La skill `crear-acta-md` SHALL escribir el desarrollo de la agenda en prosa o listas y reservar las tablas para los anexos, salvo Asistentes, Compromisos, Firma y Autor.

#### Scenario: Acta con una tabla informativa
- **WHEN** el acta necesita mostrar una tabla de datos
- **THEN** la tabla se escribe en `## ANEXOS` y el punto de la agenda la referencia con un enlace al anexo

### Requirement: Anexos como tablas reales en página nueva
Al convertir a Google Docs, si el acta tiene anexos, `acta-md-to-google-docs` SHALL insertar al final del documento, después de la tabla Autor, un salto de página, el título "ANEXOS" y, por cada anexo, su título y una tabla real con el encabezado en negrita. La tabla MUST conservar todas sus columnas y filas, sin límite de ancho.

#### Scenario: Acta con un anexo de dos columnas
- **WHEN** el usuario convierte un acta con "Anexo A" de 2 columnas y 5 filas
- **THEN** el Doc termina con una página nueva que contiene "ANEXOS", el título "Anexo A" y una tabla de 2 columnas y 5 filas

#### Scenario: Anexo de cinco columnas
- **WHEN** el acta tiene un anexo con 5 columnas
- **THEN** el Doc muestra la tabla con las 5 columnas completas

#### Scenario: Acta sin anexos
- **WHEN** el acta no tiene sección `## ANEXOS`
- **THEN** el Doc no incluye salto de página ni título "ANEXOS"

### Requirement: Enlace interno al anexo
Cada referencia `[Anexo X](#anexo-x)` del cuerpo SHALL convertirse en un enlace que lleve al título de ese anexo dentro del mismo Doc. Una referencia sin anexo correspondiente MUST dejarse como texto plano, y la conversión SHALL avisar al usuario.

#### Scenario: Referencia con anexo
- **WHEN** el punto 5 contiene `[Anexo A](#anexo-a)` y existe el Anexo A
- **THEN** el texto "Anexo A" del Doc es un enlace al título del Anexo A

#### Scenario: Referencia sin anexo
- **WHEN** el cuerpo referencia `#anexo-z` y no existe ese anexo
- **THEN** el texto queda sin enlace y el usuario recibe un aviso

### Requirement: Tablas sueltas en el desarrollo
Si un acta trae una tabla markdown dentro del desarrollo de la agenda, la conversión SHALL moverla a un anexo nuevo, dejar en su lugar un enlace al anexo y avisar al usuario. La conversión MUST NOT pegar líneas de pipes como texto en el Doc.

#### Scenario: Tabla dentro del desarrollo
- **WHEN** el desarrollo contiene una tabla markdown fuera de `## ANEXOS`
- **THEN** el Doc la muestra como anexo al final, con un enlace en el punto original, y el usuario recibe un aviso

### Requirement: Tablas fijas de la plantilla
Las tablas de Asistentes, Compromisos, Firma y Autor SHALL convertirse como hasta ahora, sin pasar a anexos.

#### Scenario: Acta sin tablas en el desarrollo
- **WHEN** el acta solo tiene las tablas fijas de la plantilla
- **THEN** el Doc se genera igual que antes de este cambio
