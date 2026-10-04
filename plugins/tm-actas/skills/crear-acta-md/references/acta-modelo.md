# ACTA DE SEGUIMIENTO DE PROYECTO — BlackSip

## INFORMACIÓN GENERAL DE LA REUNIÓN

| Campo | Detalle | | | |
| :-- | :-- | :-- | :-- | :-- |
| **Número de acta** | | | | |
| **Proyecto** | Cliente Ejemplo – Soporte | | | |
| **Lugar de la reunión** | Virtual (Google Meet) | | | |
| **Fecha de inicio** | **Día** | Enero 15 de 2026 | **Hora** | 10:00 am |
| **Fecha de finalización** | **Día** | Enero 15 de 2026 | **Hora** | 11:05 am |
| **Asunto** | Revisión de soportes: unificación del proceso de escalamiento de tickets | | | |

## ASISTENTES

| Nombre | Email | Empresa |
| :-- | :-- | :-- |
| Ana Pérez | ana.perez@clienteejemplo.com | Cliente Ejemplo |
| Carlos Gómez | _(por confirmar)_ | Cliente Ejemplo |
| María López | maria.lopez@blacksip.com | Blacksip |
| Luis Torres | luis.torres@blacksip.com | Blacksip |
| **Invitados que no asistieron** |  |  |
| Sofía Ramírez | sofia.ramirez@blacksip.com | Blacksip |
| Pedro Castro | pedro.castro@clienteejemplo.com | Cliente Ejemplo |

## DESARROLLO DE LA REUNIÓN

### Agenda

## **Objetivo de la reunión**

Revisar el estado de los tickets de soporte escalados en los últimos dos meses, identificar las causas de los casos no replicables y acordar un proceso unificado de escalamiento, evidencia y cierre de tickets entre Cliente Ejemplo (primer nivel) y Blacksip (segundo nivel).

## **Agenda**

1. Presentación del equipo y análisis de tickets escalados.
2. Causas de los casos no replicados.
3. Propuesta de formulario único de escalamiento.
4. Uso de grabaciones como evidencia y permisos.
5. Flujo ante casos no replicables y plazos de respuesta.
6. Cierre de casos y estados en la plataforma de soporte.
7. Casos pendientes de validación.
8. Compromisos y cierre.

### Desarrollo de la Agenda

### **1. Presentación del equipo y análisis de tickets escalados**

Ana Pérez presentó a Carlos Gómez, practicante de TI que apoya el soporte. Describió el proceso actual: la persona usuaria final registra el caso en la mesa de ayuda; TI del cliente lo revisa y, si no lo resuelve internamente, lo escala a Blacksip por dos vías: carga en un Excel de seguimiento y correo manual a soporte.

Expuso el análisis de los últimos dos meses: **20 casos escalados**, de los cuales el **50 % se desplegó** y el **40 % no pudo ser replicado**; el tiempo promedio de respuesta fue de **dos días**, considerado aceptable.

### **2. Causas de los casos no replicados**

El 40 % de casos no replicados se origina en la falta de información detallada que las personas usuarias registran inicialmente. Los reportes con grandes volúmenes de datos presentan lentitud o errores de tiempo de espera agotado. Luis Torres indicó que no pudo replicar un caso reciente por la ausencia de los filtros aplicados por la persona usuaria, y que consultas de períodos extensos (p. ej. un año completo) saturan el navegador.

### **3. Propuesta de formulario único de escalamiento**

Se identificó que el cliente realiza doble trabajo (Excel + correo manual). Ana Pérez propuso un formulario único; María López aceptó, indicando que debe enfocarse el esfuerzo en reducir el **40 %** de casos no replicados.

El formulario registrará de forma automática en el Excel de seguimiento y creará el ticket en la plataforma de soporte de Blacksip. Incluirá: nombre de la persona usuaria, módulo, ruta, ID o código del registro, pasos realizados, correo del usuario final y evidencia en video o captura. La persona usuaria final quedará en copia del ticket desde el inicio.

### **4. Uso de grabaciones como evidencia y permisos**

María López explicó que, cuando Blacksip no puede replicar una incidencia, responde con una grabación que muestra el flujo correcto, dado que los errores suelen ser procedimentales. Se evidenció que el cliente no podía ver esos videos, causa probable del alto porcentaje de casos no replicados. Se acordó revisar y corregir los permisos de los enlaces.

### **5. Flujo ante casos no replicables y plazos de respuesta**

Se acordó el siguiente flujo:

1. Blacksip siempre responderá con evidencia en video cuando indique que no logra replicar un caso.
2. El cliente revisa el video, contacta a la persona usuaria final y graba con ella el paso a paso.
3. El cliente escala de nuevo con esa grabación como evidencia.
4. Si aun con el video no se logra replicar, Blacksip contacta directamente a la persona usuaria final (con copia al cliente).
5. Si la persona usuaria no responde en **siete días calendario**, el caso se cierra automáticamente.

### **6. Cierre de casos y estados en la plataforma de soporte**

Antes, el cliente debía confirmar explícitamente para cerrar un caso. Nuevo acuerdo: cuando el cliente confirme, el caso pasa a estado **"Completado"**; si transcurren **10 días** desde el despliegue sin respuesta, el caso se cierra automáticamente por tiempo. Luis Torres automatizará el cierre por tiempo en la plataforma.

Se advirtió que las respuestas de usuarios a correos de tickets cerrados pueden reabrirlos o generar casos duplicados. María López se comprometió a validar si es posible limitar los correos autorizados; el esquema planteado depende de esta validación técnica.

### **7. Casos pendientes de validación**

Existen **30 casos desplegados en producción** en estado "pendiente validar", sin reporte de falla posterior. Se acordó cerrarlos todos.

### **8. Cierre**

María López creará el formulario y enviará el acta junto con el video de la sesión. Ana Pérez informará a Pedro Castro (invitado que no asistió) los cambios para que confirme al recibir el acta.

## CONCLUSIONES

- Se adoptará un **formulario único** para registrar y escalar solicitudes de soporte, con la persona usuaria final en copia.
- Todo escalamiento deberá incluir **evidencia en video** para reducir los casos no replicables (40 % actual).
- Si el caso no se replica con video, Blacksip contactará a la persona usuaria final; sin respuesta en **7 días calendario** el caso se cierra.
- Los casos desplegados sin respuesta del cliente se **cerrarán automáticamente tras 10 días**.
- Los **30 casos pendientes** ya desplegados serán cerrados.
- **Pendiente de validación técnica:** evitar que las respuestas de usuarios reabran tickets cerrados.

## COMPROMISOS

| Tarea | Responsable |
| :-- | :-- |
| Crear el formulario de soporte que registre en el Excel de seguimiento y cree el ticket. | María López – Blacksip |
| Validar si se pueden limitar los correos autorizados y evitar la reapertura de tickets cerrados. | María López – Blacksip |
| Enviar el acta junto con el video de la sesión. | María López – Blacksip |
| Automatizar el cierre por tiempo (10 días sin respuesta tras despliegue). | Luis Torres – Blacksip |
| Estandarizar la plantilla de escalamiento (ruta, ID, pasos, evidencia en video). | Ana Pérez – Cliente Ejemplo |
| Informar a Pedro Castro los nuevos procesos y acuerdos. | Ana Pérez – Cliente Ejemplo |
| Cerrar los 30 casos desplegados pendientes de validación. | Cliente Ejemplo y Blacksip |
| Adjuntar evidencia en video al responder o escalar tickets no replicables. | Todos |

## FIRMA DEL ACTA

| **Representante del Cliente** | **Representante de Blacksip** |
| :-: | :-: |
| &nbsp;<br>&nbsp;<br>&nbsp; | &nbsp;<br>&nbsp;<br>&nbsp; |
| **Ana Pérez**<br>Ingeniera TI – Cliente Ejemplo | **Luis Torres**<br>Tech Manager – Blacksip |

| **AUTOR** |  |  |  |
| :-- | :-- | :-- | :-- |
| **Versión** | **Nombre** | **Fecha envío** | **Observaciones** |
| 1.0 | María López | 2026-01-15 | Consolidado de notas de Gemini y Granola |
