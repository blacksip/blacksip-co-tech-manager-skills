## Purpose

Permite que un acta de BlackSip lleve capturas de pantalla de la reunión, tanto en el archivo `.md` como dentro del Google Doc, sin exponer contenido interno ni dejar archivos huérfanos.

## ADDED Requirements

### Requirement: Capturas en el acta markdown
La skill `crear-acta-md` SHALL, cuando la reunión tenga capturas disponibles, ofrecer incluirlas en el acta. Cada captura elegida MUST guardarse en `adjuntos/<acta>/NN-nombre.jpg`, junto al `.md` del acta, comprimida a un tamaño de unos 120 KB, y MUST referenciarse con `![descripción](ruta-relativa)` como párrafo propio, en el punto de la agenda al que corresponde. La skill SHALL limitarse a unas 8 capturas por acta.

#### Scenario: Reunión de Granola con capturas
- **WHEN** el usuario pide un acta de una reunión de Granola que tiene capturas
- **THEN** la skill lista las capturas con su descripción, descarta las que no aplican, baja las elegidas de una en una, las guarda comprimidas en `adjuntos/<acta>/` y las enlaza en su punto de la agenda

#### Scenario: El cliente no entrega las imágenes
- **WHEN** la herramienta de Granola devuelve solo descripciones y no la imagen
- **THEN** la skill pide al usuario que baje las capturas y las usa desde la carpeta que indique

#### Scenario: Reunión sin capturas
- **WHEN** la reunión no tiene capturas
- **THEN** el acta se genera sin imágenes y sin carpeta `adjuntos/`

### Requirement: Privacidad de las capturas
La skill MUST excluir del acta las capturas que muestren datos personales, como resultados o notas de personas o listas de nombres, y SHALL usar la descripción de cada captura para decidirlo antes de bajarla.

#### Scenario: Captura con resultados de una persona
- **WHEN** la descripción de una captura menciona notas o resultados de una persona concreta
- **THEN** la skill no la incluye en el acta ni la baja

### Requirement: Imágenes dentro del Google Doc
Al convertir un acta a Google Docs, `acta-md-to-google-docs` SHALL incrustar cada imagen referenciada en el punto de la agenda donde aparece en el `.md`, con un ancho que quepa en la celda del desarrollo, y SHALL conservar el orden relativo al texto.

#### Scenario: Acta con imágenes
- **WHEN** el usuario convierte un acta con 8 imágenes y confirma la incrustación
- **THEN** el Doc contiene las 8 imágenes en su punto de la agenda y ningún texto `![...](...)` literal

#### Scenario: Imagen junto a texto en la misma línea
- **WHEN** el `.md` tiene una imagen en la misma línea que texto
- **THEN** el Doc muestra la imagen como párrafo propio seguida del texto

### Requirement: Exposición temporal controlada
Para incrustar imágenes, la skill MUST pedir confirmación al usuario antes de compartir temporalmente un archivo con "cualquiera con el enlace". El permiso y el archivo temporal MUST eliminarse al terminar, incluso si la conversión falla, y la imagen MUST permanecer en el Doc.

#### Scenario: Conversión exitosa
- **WHEN** el usuario confirma y la conversión termina
- **THEN** no queda ningún archivo temporal ni permiso público en Drive y las imágenes siguen visibles en el Doc

#### Scenario: Fallo a mitad de la conversión
- **WHEN** la conversión falla después de abrir un permiso
- **THEN** el permiso y los archivos temporales creados hasta ese punto se eliminan

#### Scenario: Archivos temporales identificables
- **WHEN** la conversión sube una imagen para incrustarla
- **THEN** el archivo temporal se guarda en una carpeta `adjuntos-actas-temp` (creada si no existe) con un nombre que empieza por el nombre del acta, de modo que cualquier resto se localice en un solo lugar

#### Scenario: El usuario no confirma
- **WHEN** el usuario no confirma la exposición temporal
- **THEN** la skill no comparte ningún archivo y deja las imágenes como enlaces o las omite, según el modo elegido

### Requirement: Alternativa cuando no se puede compartir
Si el dominio no permite compartir por enlace, la conversión SHALL continuar sin imágenes incrustadas y avisar al usuario de que usó enlaces o las omitió.

#### Scenario: Dominio con compartir restringido
- **WHEN** el intento de compartir una imagen es rechazado por la política del dominio
- **THEN** la conversión termina, el Doc se crea sin esas imágenes y el usuario recibe un aviso claro

### Requirement: Modos de imagen
La conversión SHALL admitir los modos incrustar (por defecto, con confirmación), enlaces y ninguna.

#### Scenario: Modo ninguna
- **WHEN** el usuario convierte con el modo "ninguna"
- **THEN** el Doc se crea sin imágenes y sin pedir confirmación de exposición
